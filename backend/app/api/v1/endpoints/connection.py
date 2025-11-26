from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session
from app.services.metadata import MetadataService
from app.db.session import get_db
from app.models.models import DatabaseConnection, User
from app.core.deps import get_current_active_user
from app.core.validators import validate_connection_name, validate_port

router = APIRouter()

class ConnectionConfig(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., min_length=1, max_length=50)
    host: str = Field(..., min_length=1, max_length=255)
    port: int = Field(..., ge=1, le=65535)
    database: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1)
    description: Optional[str] = Field(None, max_length=500)

    @validator('name')
    def validate_name(cls, v):
        return validate_connection_name(v)

    @validator('port')
    def validate_port_range(cls, v):
        return validate_port(v)

class ConnectionResponse(BaseModel):
    id: int
    name: str
    type: str
    connection_string: str
    description: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class ColumnMetadata(BaseModel):
    name: str
    type: str
    nullable: bool
    default: Optional[str] = None
    autoincrement: bool = False

class ForeignKeyMetadata(BaseModel):
    name: Optional[str]
    columns: List[str]
    referred_table: str
    referred_columns: List[str]

class IndexMetadata(BaseModel):
    name: Optional[str]
    columns: List[str]
    unique: bool = False

class ConstraintMetadata(BaseModel):
    name: Optional[str]
    columns: Optional[List[str]] = None
    sqltext: Optional[str] = None

class TableMetadata(BaseModel):
    name: str
    columns: List[ColumnMetadata]
    primary_key: List[str] = []
    foreign_keys: List[ForeignKeyMetadata] = []
    indexes: List[IndexMetadata] = []
    unique_constraints: List[ConstraintMetadata] = []
    check_constraints: List[ConstraintMetadata] = []
    row_count: Optional[int] = None

def build_connection_string(config: ConnectionConfig) -> str:
    """Build connection string from individual components"""
    if config.type.lower() == "postgresql":
        return f"postgresql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
    elif config.type.lower() == "mysql":
        return f"mysql+pymysql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
    elif config.type.lower() == "mssql":
        return f"mssql+pyodbc://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}?driver=ODBC+Driver+17+for+SQL+Server"
    else:
        # Default to PostgreSQL format
        return f"{config.type}://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"

@router.post("/connect", response_model=ConnectionResponse)
async def create_connection(
    config: ConnectionConfig,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new database connection and save to database"""
    # Build connection string
    connection_string = build_connection_string(config)

    # Test connection
    try:
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            pass  # Just test the connection
        engine.dispose()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")

    # Save to database
    db_connection = DatabaseConnection(
        name=config.name,
        type=config.type,
        connection_string=connection_string,
        description=config.description,
        is_active=True,
        owner_id=current_user.id
    )

    db.add(db_connection)
    db.commit()
    db.refresh(db_connection)

    return db_connection

@router.get("/connections", response_model=List[ConnectionResponse])
async def get_connections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all database connections for the current user"""
    # Admin can see all connections, regular users only see their own
    if current_user.is_superuser or current_user.role == "admin":
        connections = db.query(DatabaseConnection).filter(DatabaseConnection.is_active == True).all()
    else:
        connections = db.query(DatabaseConnection).filter(
            DatabaseConnection.is_active == True,
            DatabaseConnection.owner_id == current_user.id
        ).all()
    return connections

@router.get("/metadata/{connection_name}", response_model=List[TableMetadata])
async def get_metadata(
    connection_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get metadata for a specific connection"""
    connection = db.query(DatabaseConnection).filter(
        DatabaseConnection.name == connection_name,
        DatabaseConnection.is_active == True
    ).first()

    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    # Check ownership
    if not (current_user.is_superuser or current_user.role == "admin" or connection.owner_id == current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this connection")

    try:
        service = MetadataService(connection.connection_string)
        return service.get_tables()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metadata extraction failed: {str(e)}")

