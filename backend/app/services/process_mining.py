import pandas as pd
import pm4py
from typing import Dict, Any, List, Optional
import os
from app.core.logging import get_logger

logger = get_logger(__name__)

class ProcessMiningService:
    """
    Service for Process Mining capabilities using PM4Py
    """
    
    @staticmethod
    def analyze_event_log(file_path: str, case_id_col: str, activity_col: str, timestamp_col: str) -> Dict[str, Any]:
        """
        Analyze an event log CSV file and return process metrics and graph data
        
        Args:
            file_path: Path to the CSV event log
            case_id_col: Column name for Case ID
            activity_col: Column name for Activity
            timestamp_col: Column name for Timestamp
            
        Returns:
            Dictionary containing process metrics and graph representation
        """
        try:
            # Read CSV
            df = pd.read_csv(file_path)
            
            # Convert timestamp column
            df[timestamp_col] = pd.to_datetime(df[timestamp_col])
            
            # Format for PM4Py
            df = pm4py.format_dataframe(
                df, 
                case_id=case_id_col, 
                activity_key=activity_col, 
                timestamp_key=timestamp_col
            )
            
            # Discover Petri Net (Alpha Miner)
            net, initial_marking, final_marking = pm4py.discover_petri_net_alpha(df)
            
            # Discover DFG (Directly-Follows Graph)
            dfg, start_activities, end_activities = pm4py.discover_dfg(df)
            
            # Calculate basic statistics
            num_cases = len(df[case_id_col].unique())
            num_events = len(df)
            num_activities = len(df[activity_col].unique())
            
            # Get start and end activities statistics
            start_activities_stats = pm4py.get_start_activities(df)
            end_activities_stats = pm4py.get_end_activities(df)
            
            # Convert DFG to node-link format for frontend visualization (e.g., React Flow or Cytoscape)
            nodes = set()
            links = []
            
            # Add nodes
            for activity in df[activity_col].unique():
                nodes.add(activity)
            
            # Add edges from DFG
            for (source, target), count in dfg.items():
                links.append({
                    "source": source,
                    "target": target,
                    "value": count
                })
            
            # Calculate variants
            variants = pm4py.get_variants_as_tuples(df)
            top_variants = sorted(
                [{"variant": " -> ".join(v), "count": c} for v, c in variants.items()],
                key=lambda x: x["count"],
                reverse=True
            )[:10]  # Top 10 variants
            
            return {
                "metrics": {
                    "cases": num_cases,
                    "events": num_events,
                    "activities": num_activities,
                    "variants": len(variants)
                },
                "graph": {
                    "nodes": [{"id": n, "label": n} for n in nodes],
                    "edges": links
                },
                "statistics": {
                    "start_activities": start_activities_stats,
                    "end_activities": end_activities_stats,
                    "top_variants": top_variants
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing event log: {str(e)}")
            raise Exception(f"Failed to analyze event log: {str(e)}")

    @staticmethod
    def discover_process_map(file_path: str, case_id_col: str, activity_col: str, timestamp_col: str) -> str:
        """
        Generate a BPMN model from the event log
        """
        try:
            df = pd.read_csv(file_path)
            df[timestamp_col] = pd.to_datetime(df[timestamp_col])
            df = pm4py.format_dataframe(df, case_id=case_id_col, activity_key=activity_col, timestamp_key=timestamp_col)
            
            # Discover BPMN (Inductive Miner)
            bpmn_model = pm4py.discover_bpmn_inductive(df)
            
            # Convert to XML string
            # Note: PM4Py usually exports to file. We might need to save temp file and read it or use string export if available.
            # For now, we'll return a placeholder or implement file saving logic if needed.
            # pm4py.write_bpmn(bpmn_model, "temp.bpmn")
            
            return "BPMN generation successful (XML export pending implementation)"
            
        except Exception as e:
            logger.error(f"Error discovering BPMN: {str(e)}")
            raise Exception(f"Failed to discover BPMN: {str(e)}")
