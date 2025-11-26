from typing import Dict, Any, List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
import pandas as pd
from datetime import datetime


class VisualizationService:
    """
    Service for generating data visualizations and chart configurations
    """
    
    @staticmethod
    def suggest_chart_type(data: List[Dict[str, Any]], columns: List[str]) -> Dict[str, Any]:
        """
        Suggest appropriate chart type based on data characteristics
        
        Args:
            data: Query result data
            columns: Column names
            
        Returns:
            Chart configuration suggestion
        """
        if not data or not columns:
            return {"type": "table", "reason": "No data available"}
        
        df = pd.DataFrame(data)
        num_columns = len(columns)
        num_rows = len(data)
        
        # Analyze column types
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Decision logic
        if num_columns == 1:
            return {
                "type": "metric",
                "config": {
                    "value_column": columns[0]
                },
                "reason": "Single value - best shown as metric"
            }
        
        elif num_columns == 2 and len(numeric_cols) == 1 and len(categorical_cols) == 1:
            # One categorical, one numeric - bar or pie chart
            if num_rows <= 10:
                return {
                    "type": "bar",
                    "config": {
                        "x_axis": categorical_cols[0],
                        "y_axis": numeric_cols[0]
                    },
                    "reason": "Categorical vs numeric comparison"
                }
            else:
                return {
                    "type": "line",
                    "config": {
                        "x_axis": categorical_cols[0],
                        "y_axis": numeric_cols[0]
                    },
                    "reason": "Time series or trend data"
                }
        
        elif len(numeric_cols) >= 2:
            # Multiple numeric columns - scatter or line chart
            return {
                "type": "scatter",
                "config": {
                    "x_axis": numeric_cols[0],
                    "y_axis": numeric_cols[1]
                },
                "reason": "Correlation between numeric values"
            }
        
        else:
            # Default to table
            return {
                "type": "table",
                "config": {},
                "reason": "Complex data structure - table view recommended"
            }
    
    @staticmethod
    def generate_chart_config(
        chart_type: str,
        data: List[Dict[str, Any]],
        x_column: str,
        y_column: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate chart configuration for frontend
        
        Args:
            chart_type: Type of chart (bar, line, pie, scatter)
            data: Query result data
            x_column: X-axis column name
            y_column: Y-axis column name (optional)
            
        Returns:
            Chart configuration object
        """
        config = {
            "type": chart_type,
            "data": data,
            "options": {
                "responsive": True,
                "maintainAspectRatio": False
            }
        }
        
        if chart_type == "bar":
            config["options"]["scales"] = {
                "x": {"title": {"display": True, "text": x_column}},
                "y": {"title": {"display": True, "text": y_column or "Value"}}
            }
        
        elif chart_type == "line":
            config["options"]["scales"] = {
                "x": {"title": {"display": True, "text": x_column}},
                "y": {"title": {"display": True, "text": y_column or "Value"}}
            }
            config["options"]["elements"] = {
                "line": {"tension": 0.4}
            }
        
        elif chart_type == "pie":
            config["options"]["plugins"] = {
                "legend": {"position": "right"}
            }
        
        return config
    
    @staticmethod
    def get_query_statistics(db: Session, connection_id: int) -> Dict[str, Any]:
        """
        Get query execution statistics for dashboard
        
        Args:
            db: Database session
            connection_id: Database connection ID
            
        Returns:
            Statistics dictionary
        """
        # This would query chat_messages table for statistics
        # Placeholder implementation
        return {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "avg_execution_time": 0,
            "most_queried_tables": []
        }
