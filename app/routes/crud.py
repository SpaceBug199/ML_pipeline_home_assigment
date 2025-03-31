import uuid
from typing import List
from datetime import datetime
import pickle
import logging

from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from supabase import Client

from models.models import Scenario, ModelStatus
from database.database import get_db
from database.crud import get_scenarios, update_active_model, get_scenario_data
from utility.logging_setup import setup_logging

STORAGE_BUCKET = "training-data"
MODELS_BUCKET = "models"

router = APIRouter()
setup_logging()
logger = logging.getLogger("router_crud")
logging.info("logging started for CRUD router")


@router.get("/")
def read_root():
    return {
        "message": "See the ML pipeline documentation on how to use this training and inference pipeline"
    }


# GET /v1/scenarios
@router.get("/v1/scenarios", response_model=List[Scenario])
async def get_scenarios_list(supabase: Client = Depends(get_db)):
    """Get scenarios list from the database and return as JSON response
    Returns:
        List[Scenario]: List of scenarios from the database
    Raises:
        HTTPException: 500 If there is an error with the database connection
        HTTPException: 404 If no scenarios are found in the database

    """
    print("GET /v1/scenarios - Returning list of available scenarios")
    try:
        scenarios = await get_scenarios(supabase)
        if scenarios == None:
            raise HTTPException(status_code=404, detail="No Scenarios found")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )
    scenarios_data = scenarios
    print(scenarios_data)
    return scenarios_data


@router.post("/v1/scenarios/{scenario_id}/train/training_data")
async def upload_training_data_file(
    file: UploadFile = File(...), supabase: Client = Depends(get_db)
):
    """Upload training data file to the storage and insert metadata into the database
    Args:
        file (UploadFile): File to be uploaded
        supabase (Client): Supabase client
    Returns:
        dict: File upload status
    Raises:
        HTTPException: 500 If there is an error with the database connection
        HTTPException: 400 If the file is not in CSV file format
        HTTPException: 500 If the file upload fails
    """
    try:
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed.")
        file_uuid = str(uuid.uuid4())
        content = await file.read()
        file_path = f"{file_uuid}/{file.filename}"
        storage_response = supabase.storage.from_(STORAGE_BUCKET).upload(
            file_path, content
        )
        if not storage_response:
            raise HTTPException(
                status_code=500, detail="Failed to upload file to storage."
            )

        file_url = f"/storage/v1/object/public/{STORAGE_BUCKET}/{file_path}"
        data = {
            "model_training_data_id": file_uuid,
            "model_training_data_url": file_url,
            "model_training_data_name": file.filename,
            "used_status": False,
            "created_at": datetime.now().isoformat(),
        }

        db_response = supabase.table("training_data").insert(data).execute()
        if not db_response:
            raise HTTPException(
                status_code=500, detail="Failed to insert file metadata into database."
            )
        return {
            "message": "File uploaded successfully",
            "file_id": file_uuid,
            "file_url": file_url,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/v1/scenarios/{scenario_id}/models/model")
async def upload_model(
    model_name: str = "Form completion prediction",
    model_precision: float = 0.5,
    accuracy: float = 0.5,
    recall: float = 0.5,
    f1_score: float = 0.5,
    model_version: float = 1.0,
    # model_training_data: UUID = "data-001",
    file: UploadFile = File(...),
    supabase: Client = Depends(get_db),
):
    """Upload model file to the storage and insert metadata into the database
    Args:
        model_name (str): Model name
        model_precision (float): Model precision
        accuracy (float): Model accuracy
        recall (float): Model recall
        f1_score (float): Model F1 score
        model_version (float): Model version
        file (UploadFile): File to be uploaded
        supabase (Client): Supabase client
    Returns:
        dict: File upload status
    Raises:
        HTTPException: 500 If there is an error with the database connection
        HTTPException: 400 If the file is not in pickle file format
        HTTPException: 500 If the file upload fails
    """
    try:
        if not file.filename.endswith(".pkl"):
            raise HTTPException(
                status_code=400, detail="Only pickle models are currently supported."
            )
        file_uuid = str(uuid.uuid4())
        content = await file.read()
        file_path = f"{file_uuid}/{file.filename}"
        storage_response = supabase.storage.from_(MODELS_BUCKET).upload(
            file_path, content
        )
        if not storage_response:
            raise HTTPException(
                status_code=500, detail="Failed to upload file to storage."
            )

        file_url = f"/storage/v1/object/public/{MODELS_BUCKET}/{file_path}"
        current_time = datetime.now().isoformat()

        data = {
            "model_id": file_uuid,
            "model_url": file_url,
            "model_name": model_name,
            "model_filename": file.filename,
            "accuracy": accuracy,
            "model_precision": model_precision,
            "recall": recall,
            "f1_score": f1_score,
            "created_at": current_time,
            "modified_at": current_time,
            "model_state": ModelStatus.INACTIVE,
            "model_training_data_id": file_uuid,
            "model_version": model_version,
            "trained_at": current_time,
        }

        db_response = supabase.table("ml_models").insert(data).execute()
        if not db_response:
            raise HTTPException(
                status_code=500, detail="Failed to insert file metadata into database."
            )
        return {
            "message": "File uploaded successfully",
            "file_id": file_uuid,
            "file_url": file_url,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/v1/scenarios/{scenario_id}/models/{model_id}/activate")
async def set_active_model(scenario_id: str, model_id: str, supabase: Client = Depends(get_db)):
    """ Set active model for a selected scenario by changing the model state to ACTIVE in database.
        Must update model status in both the model table and the scenario_models table 
    Returns:
        dict: Model activation status
    Raises:
        HTTPException: 500 If there is an error with the database connection
        HTTPException: 404 If the model or scenario does not exist
    """
    try:
        model_update = await update_active_model(scenario_id, model_id, supabase)
        if not model_update:
            raise HTTPException(
                status_code=404, detail="Model or scenario does not exist."
            )
        return {"message": "Model activated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    pass
