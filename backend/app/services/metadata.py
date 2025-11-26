from sqlalchemy import create_engine, inspect, text
from typing import List, Dict, Any, Optional

class MetadataService:
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        self.inspector = inspect(self.engine)

    def get_tables(self) -> List[Dict[str, Any]]:
        """Extract comprehensive metadata for all tables"""
        tables = []
        for table_name in self.inspector.get_table_names():
            table_metadata = self._get_table_metadata(table_name)
            tables.append(table_metadata)
        return tables
    
    def _get_table_metadata(self, table_name: str) -> Dict[str, Any]:
        """Get detailed metadata for a single table"""
        # Get columns
        columns = []
        for col in self.inspector.get_columns(table_name):
            columns.append({
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col["nullable"],
                "default": str(col.get("default")) if col.get("default") else None,
                "autoincrement": col.get("autoincrement", False)
            })
        
        # Get primary key
        pk = self.inspector.get_pk_constraint(table_name)
        primary_key = pk.get("constrained_columns", [])
        
        # Get foreign keys
        foreign_keys = []
        for fk in self.inspector.get_foreign_keys(table_name):
            foreign_keys.append({
                "name": fk.get("name"),
                "columns": fk.get("constrained_columns", []),
                "referred_table": fk.get("referred_table"),
                "referred_columns": fk.get("referred_columns", [])
            })
        
        # Get indexes
        indexes = []
        for idx in self.inspector.get_indexes(table_name):
            indexes.append({
                "name": idx.get("name"),
                "columns": idx.get("column_names", []),
                "unique": idx.get("unique", False)
            })
        
        # Get unique constraints
        unique_constraints = []
        try:
            for uc in self.inspector.get_unique_constraints(table_name):
                unique_constraints.append({
                    "name": uc.get("name"),
                    "columns": uc.get("column_names", [])
                })
        except NotImplementedError:
            # Some databases don't support this
            pass
        
        # Get check constraints
        check_constraints = []
        try:
            for cc in self.inspector.get_check_constraints(table_name):
                check_constraints.append({
                    "name": cc.get("name"),
                    "sqltext": cc.get("sqltext")
                })
        except NotImplementedError:
            # Some databases don't support this
            pass
        
        return {
            "name": table_name,
            "columns": columns,
            "primary_key": primary_key,
            "foreign_keys": foreign_keys,
            "indexes": indexes,
            "unique_constraints": unique_constraints,
            "check_constraints": check_constraints,
            "row_count": self._get_row_count(table_name)
        }
    
    def _get_row_count(self, table_name: str) -> Optional[int]:
        """Get approximate row count for a table"""
        try:
            with self.engine.connect() as conn:
                # Use SQLAlchemy text() with proper identifier quoting
                result = conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"'))
                return result.scalar()
        except Exception:
            return None
    
    def get_table_sample(self, table_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get sample rows from a table"""
        try:
            # Validate limit to prevent abuse
            limit = max(1, min(limit, 1000))

            with self.engine.connect() as conn:
                # Use SQLAlchemy text() with proper identifier quoting and parameter binding
                result = conn.execute(text(f'SELECT * FROM "{table_name}" LIMIT :limit'), {"limit": limit})
                columns = result.keys()
                rows = []
                for row in result:
                    rows.append(dict(zip(columns, row)))
                return rows
        except Exception as e:
            raise Exception(f"Failed to get sample data: {str(e)}")

