from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class ModelType(str, Enum):
    OLTP = "OLTP"
    OLAP = "OLAP"
    FACT_DIM = "FACT_DIM"
    PROCESS_MINING = "PROCESS_MINING"
    GENERIC = "GENERIC"

class ModelBase(BaseModel):
    name: str
    type: ModelType
    description: Optional[str] = None

class ModelCreate(ModelBase):
    pass

class ModelUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[ModelType] = None
    description: Optional[str] = None
    is_published: Optional[bool] = None

class ModelInDB(ModelBase):
    id: int
    owner_id: int
    is_published: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Model(ModelInDB):
    pass

# Connection schemas
class ConnectionType(str, Enum):
    POSTGRES = "POSTGRES"
    MYSQL = "MYSQL"
    MSSQL = "MSSQL"
    ORACLE = "ORACLE"
    SNOWFLAKE = "SNOWFLAKE"
    BIGQUERY = "BIGQUERY"

class ConnectionBase(BaseModel):
    name: str
    type: ConnectionType
    description: Optional[str] = None

class ConnectionCreate(ConnectionBase):
    host: str
    port: int
    database: str
    username: str
    password: str

class ConnectionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class ConnectionInDB(ConnectionBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Connection(ConnectionInDB):
    pass
