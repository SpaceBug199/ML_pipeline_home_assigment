import os
import uuid
from typing import List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Path, Depends, status
from supabase import Client
from dotenv import load_dotenv

from models.models import Scenario, MLModel, ModelStatus, Statistics, Status, PredictionRequest, PredictionResponse, TrainingResponse, ScenarioDetail, ModelActivationResponse, Applicant
from database.database import get_db

router = APIRouter()

# POST /v1/scenarios/{scenario_ID}/train/{data_ID}
@router.post("/v1/scenarios/{scenario_ID}/train/{data_ID}", response_model=TrainingResponse, )
async def train_with_data_id(
    scenario_ID: str = Path(..., description="The ID of the scenario"),
    data_ID: str = Path(..., description="The ID of the training data")
):
    print(f"POST /v1/scenarios/{scenario_ID}/train/{data_ID} - Training model with existing dataset")
    
    # In a real application, this would retrieve the specified dataset and initiate a training job
    return TrainingResponse(
        training_ID=str(uuid.uuid4()),
        status="training_started",
        timestamp=datetime.now()
    )