import uuid
from typing import List
from datetime import datetime
import pickle
import logging
from typing import io, BinaryIO, Any, Optional
import io

from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Body, Form
from supabase import Client

from models.models import Scenario, ModelStatus, ModelStatistics
from database.database import get_db
from database.crud import get_scenarios, update_active_model, get_models, upload_new_model
from utility.logging_setup import setup_logging
from database.table_names import TableName



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
        storage_response = supabase.storage.from_(TableName.TRAINING_DATA_BUCKET).upload(
            file_path, content
        )
        if not storage_response:
            raise HTTPException(
                status_code=500, detail="Failed to upload file to storage."
            )

        file_url = f"/storage/v1/object/public/{TableName.TRAINING_DATA_BUCKET}/{file_path}"
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
    model_name: str = Form(...),
    file: UploadFile = File(...),
    supabase: Client = Depends(get_db),
    model_performance: str = Form(...),   
    model_version: Optional[float] = Form(None), 
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
    logger.info(f" model parameters are {model_performance}")
    try:
        if not file.filename.endswith(".pkl"):
            raise HTTPException(
                status_code = 400, detail="Only pickle models are currently supported."
            )
        model_id = str(uuid.uuid4()) # assign a unique UUID to the model
        model_content = await file.read()
        model_file = io.BytesIO(model_content)

        upload_result = await upload_new_model(
                file = model_file,
                file_name = file.filename,
                model_name = model_name,
                model_id = model_id,
                model_version = model_version,
                model_performance = model_performance,
                db = supabase)
        if not upload_result:
            raise HTTPException(
                status_code = 500, detail="Failed to upload model to storage."
            )

        return {
            "message": "File uploaded successfully",
            "model_id": model_id,
            "model_url": upload_result,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/v1/scenarios/{scenario_id}/models")
async def get_scenario_models(scenario_id: str, supabase: Client = Depends(get_db)):
    """Get models for a selected scenario from the database and return as JSON response
    Args:
        scenario_id (str): Scenario ID
        supabase (Client): Supabase client
    Returns:
        List[dict]: List of models for the selected scenario
    Raises:
        HTTPException: 500 If there is an error with the database connection
        HTTPException: 404 If the scenario does not exist
    """
    try:
        scenario_data = await get_models(scenario_id, supabase)
        if not scenario_data:
            raise HTTPException(status_code=404, detail="Scenario not found")
        scenario_models = supabase.table("scenario_models").select("*").eq("scenario_id", scenario_id).execute()
        if not scenario_models.data or len(scenario_models.data) == 0:
            raise HTTPException(status_code=404, detail="No models found for the assigned scenario")
        return scenario_models.data
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