import os
import logging
import asyncio
from io import BytesIO
from functools import lru_cache
from typing import BinaryIO
from datetime import datetime
import json

from models.models import MLModel, Scenario, ModelStatus, ModelStatistics, PerformanceMetrics
from supabase import create_client, Client
from database.table_names import TableName
from utility.model_loader import ModelLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("supabase_client")


async def get_scenarios(db: Client) -> list[Scenario]:
    logger.info(f"Getting scenario list")
    scenarios = db.table("scenarios").select("*").execute()
    if not scenarios.data or len(scenarios.data) == 0:
        logger.info(f"No scenarois found in the database")
        return None
    return scenarios.data


async def get_models(scenario_id: str, db: Client) -> list[MLModel]:
    """Get all models for a given scenario
    Args:
        scenario_id (str): Scenario ID
        db (Client): Supabase client
    Returns:
        list[MLModel]: List of models for the given scenario
    """
    logger.info(f"Getting model list for scenario_id:{scenario_id} ")
    models = (
        db.table("scenario_models")
        .select("*")
        .eq("scenario_id", scenario_id)
        .execute()
    )
    if not models.data or len(models.data) == 0:
        logger.info(f"No models found for the assigned scenario")
        return None
    return models.data


async def get_scenario_data(scenario_id: str, db: Client) -> Scenario:
    logger.info(f"Getting Scenario metadata for scenario_id:{scenario_id}")
    scenario_data = (
        db.table("scenarios").select("*").eq("scenario_id", scenario_id).execute()
    )
    if not scenario_data.data or len(scenario_data.data) == 0:
        logger.info(f"Scenario {scenario_id} not found in the databse")
        return None

    if len(scenario_data.data) > 1:
        logger.error(
            f"Multiple rows found for {scenario_id},\
                    this might be a data coruption or incomplete scenario ID was provided"
        )
        return None
    return scenario_data.data[0]


async def upload_new_model(file: BinaryIO, file_name: str, model_name: str, model_id: str, model_version: float, model_performance: ModelStatistics, scenario_id: str, db: Client) -> str:
    """Upload a new model to the storage and insert metadata into the database
    Args:
        model (MLModel): Model metadata
        file (BinaryIO): Model file
        db (Client): Supabase client
    Returns:
        bool: True if model uploaded successfully, False otherwise
    """
    model_file = file.read()
    file_path = f"{model_id}/{file_name}"
    current_time = datetime.now().isoformat()
    file_url = f"/storage/v1/object/public/{TableName.MODELS_BUCKET}/{file_path}"

    
    try: 
        logger.info(f"Decoding model performance data {model_performance}")
        performance = json.loads(model_performance)
        logger.info(f"Model performance data decoded successfully {performance}")
    except json.JSONDecodeError as e:
        return {"error": f"Error decoding model performance data: {str(e)}"}
    
    logger.info(f"unpacked data type {type(performance)}, performance = {performance}")
    logger.info(f"dict keys = {performance.keys()}")
    data = {
        "model_id": model_id,
        "model_url": file_url,
        "model_name": model_name,
        "model_filename": file_name,
        "accuracy": performance[PerformanceMetrics.ACCURACY],
        "model_precision": performance[PerformanceMetrics.PRECISION],
        "recall": performance[PerformanceMetrics.RECALL],
        "f1_score": performance[PerformanceMetrics.F1_SCORE],
        "created_at": current_time,
        "modified_at": current_time,
        "model_state": ModelStatus.INACTIVE,
        "model_training_data_id": model_id,
        "model_version": model_version,
        "trained_at": current_time,
    }

    logger.info(f"Uploading model {model_id} to the storage")
    storage_response = db.storage.from_(TableName.MODELS_BUCKET).upload(file_path, model_file)
    if not storage_response:
        logger.error(f"Error uploading model {model_id} to the storage")
        return False
    
    db_response = db.table(TableName.ML_MODELS).insert(data).execute()
    logger.info(f"supabase response = {db_response}")
    if not db_response:
        logger.error(
            f"Error inserting model {model_id} metadata into the database"
        )
        return False 
    db_response = db.table(TableName.SCENARIO_MODELS).insert({"scenario_id": scenario_id, "model_id": model_id, "is_active": False}).execute()
    if not db_response:
        logger.error(
            f"Error inserting model {model_id} metadata into the scenario_models table"
        )
        return False

    return file_url


async def update_active_model(scenario_id: str, model_id: str, db: Client) -> bool:
    """Set active model for a selected scenario
    Reutrn true if model set sucessfully
    Return false if model or scenario don't exist or other errors occur
    Args:
        scenario_id (str): Scenario ID
        model_id (str): Model ID
        db (Client): Supabase client
    Returns:
        bool: True if model set successfully, False otherwise
    """
    file_name = db.table(TableName.ML_MODELS).select("model_filename").eq("model_id", model_id).execute().data[0]["model_filename"]
    file_path = f"{model_id}/{file_name}"
    
    # Download the model from the storage
    storage_response = db.storage.from_(TableName.MODELS_BUCKET).download(file_path)
    if not storage_response:
        logger.error(f"Error downloading model {model_id} from the storage")
        return False
    # Load the model into memory
    model_binary = BytesIO(storage_response)
    loader = ModelLoader()
    if not loader.load_model_from_binary(model_binary):
        logger.error(f"Error loading model {model_id} from binary data")
        return False
    # Update database to set the active model
    model_data = db.table(TableName.ML_MODELS).select("*").eq("model_id", model_id).execute()
    if not model_data.data or len(model_data.data) == 0:
        logger.error(f"Model {model_id} not found in the database")
        return False
    # If database update fails we could have loaded model that is different than the database !!!
    # We should consider rolling back the model in memory if the database update fails
    
    logger.info(f"Setting active model: {model_id} for Scenario: {scenario_id}")
    logger.info(f"Setting all other models to inactive")
    response = (
        db.table(TableName.SCENARIO_MODELS)
        .update({"is_active": False})
        .eq("scenario_id", scenario_id)
        .execute()
    )
    logger.info(f"response is {response}")
    if "error" in response:
        logger.error(f"Error setting all models to inactive: {response.error}")
        loader.rollback_model()
        return False
    
    logger.info(f"Setting model {model_id} to active")
    response = (
        db.table(TableName.SCENARIO_MODELS)
        .update({"is_active": True})
        .eq("scenario_id", scenario_id)
        .eq("model_id", model_id)
        .execute()
    )
    logger.info(f"response is {response}")
    if "error" in response:
        logger.error(f"Error setting model {model_id} to active: {response.error}")
        return False
    logger.info(f"Model {model_id} set to active successfully")

    return True
