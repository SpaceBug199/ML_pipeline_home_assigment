import os
import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, Path, Depends, status
from supabase import Client

from models.models import  PredictionRequest, PredictionResponse, TaxFilingPredictionResponse, TaxFilingPredictionRequest
from database.database import get_db
from utility.model_executor import ModelExecutor
from utility.logging_setup import setup_logging
from utility.model_loader import ModelLoader


logging = setup_logging()
router = APIRouter()

# # POST /v1/scenarios/{scenario_ID}/predict
# @router.post("/v1/scenarios/{scenario_ID}/predict", response_model=PredictionResponse)
# async def predict(
#     prediction_request: PredictionRequest,
#     scenario_ID: str = Path(..., description="The ID of the scenario"),
#     db: Client = Depends(get_db)
# ):
#     print(f"POST /v1/scenarios/{scenario_ID}/predict - Running prediction using currently loaded model")
#     print(f"Applicant data: {prediction_request.applicant}")
#     scenario_response = db.table("scenarios").select("*").eq("scenario_id", scenario_ID).execute()
#     if not scenario_response.data or len (scenario_response) == 0:
#         raise HTTPException(status_code=404, detail="Scenario not found")
#     # Check if scenario exists
   
#     if not scenario_response.data or len(scenario_response.data)==0:
#         raise HTTPException(status_code=404, detail="Scenario not found")
 
#     # # Check if there's an active model for this scenario
#     # if scenario_ID not in active_models:
#     #     raise HTTPException(status_code=400, detail="No active model for this scenario")
    
#     # In a real application, we would load the model and make a prediction
#     # For this example, we'll just return a sample response
#     return PredictionResponse(
#         prediction_ID=str(uuid.uuid4()),
#         result=True,
#         confidence=0.85,
#         timestamp=datetime.now()
#     )


@router.post("/v1/scenarios/{scenario_ID}/predict", response_model=TaxFilingPredictionResponse)
async def predict_tax_filing_completion(request: TaxFilingPredictionRequest):
    """Predict whether a user will complete their tax filing.
    
    Args:
        request: User tax data for prediction
        
    Returns:
        Prediction result with confidence score
        
    Raises:
        HTTPException: If prediction fails
    """
    try:
        # Convert Pydantic model to dictionary
        input_data = request.model_dump()  # Using model_dump() instead of dict()
        
        # Execute inference
        prediction, confidence = ModelExecutor.execute_inference(input_data)
        
        # Return response
        return TaxFilingPredictionResponse(
            will_complete_filing=bool(prediction),
            confidence_score=confidence
        )
        
    except ValueError as e:
        # Input validation error
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        # Model execution error
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # Unexpected error
        logging.error(f"Unexpected error in prediction endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
