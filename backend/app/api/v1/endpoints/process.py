from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from typing import Optional
import shutil
import os
import tempfile
from app.services.process_mining import ProcessMiningService
from app.core.logging import get_logger
from app.api.v1.endpoints.auth import get_current_active_user
from app.models.models import User

router = APIRouter()
logger = get_logger(__name__)

@router.post("/analyze")
async def analyze_process(
    file: UploadFile = File(...),
    case_id_col: str = Form(...),
    activity_col: str = Form(...),
    timestamp_col: str = Form(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload an event log (CSV) and analyze it
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    # Save uploaded file to temp directory
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
            
        logger.info(f"Analyzing event log: {file.filename}")
        
        # Analyze using service
        result = ProcessMiningService.analyze_event_log(
            tmp_path,
            case_id_col,
            activity_col,
            timestamp_col
        )
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return result
        
    except Exception as e:
        # Ensure cleanup
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
            
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/discover-bpmn")
async def discover_bpmn(
    file: UploadFile = File(...),
    case_id_col: str = Form(...),
    activity_col: str = Form(...),
    timestamp_col: str = Form(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Discover BPMN model from event log
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
            
        result = ProcessMiningService.discover_process_map(
            tmp_path,
            case_id_col,
            activity_col,
            timestamp_col
        )
        
        os.unlink(tmp_path)
        return {"message": result}
        
    except Exception as e:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=f"Discovery failed: {str(e)}")
