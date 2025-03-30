import os
import logging
import asyncio
from functools import lru_cache

from models.models import MLModel, Scenario
from supabase import create_client, Client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("supabase_client")


async def get_scenarios(db: Client)->list[Scenario]:
    logger.info(f"Getting scenario list")
    scenarios = db.table("scenarios").select("*").execute()
    if not scenarios.data or len(scenarios.data) == 0:
        logger.info(f"No scenarois found in the database")
        return None
    return scenarios.data

async def get_scenario_models(scenario_id: str, db: Client)->list[MLModel]:
    logger.info(f"Getting model list for scenario_id:{scenario_id} ")
    models = db.tabel("scenarios_models").select("*").eq("scenario_id", scenario_id).execute()
    if not models.data or len(models.data) == 0: 
        logger.info(f"No models found for the assigned scenario")
        return None
    return models.data

async def get_scenario_data(scenario_id: str, db: Client)->Scenario:
    logger.info(f"Getting Scenario metadata for scenario_id:{scenario_id}")
    scenario_data = db.table("scenarios").select("*").eq("scenario_id", scenario_id).execute()
    if not scenario_data.data or len(scenario_data.data) == 0:
        logger.info(f"Scenario {scenario_id} not found in the databse") 
        return None
    
    if len(scenario_data.data) > 1:
        logger.error(f"Multiple rows found for {scenario_id},\
                    this might be a data coruption or incomplete scenario ID was provided")
        return None
    return scenario_data.data[0] 

async def update_active_model(scenario_id: str, model_id: str, db: Client) -> bool:
    """ Set active model for a selected scenario
        Reutrn true if model set sucessfully
        Return false if model or scenario don't exist or other errors occur
    """
    scenario_id = "NOT IMPLEMENTED"
    model_id = "NOT IMPLEMENTED"
    logger.error (f"setting active model: {model_id} NOT IMPLEMENTED for Scenario: {scenario_id}")
    pass


