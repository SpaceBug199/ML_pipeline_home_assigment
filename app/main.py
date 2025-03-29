import uuid
from typing import List
from datetime import datetime

from fastapi import FastAPI, HTTPException, Path

from models import Scenario, MLModel, ModelStatus, Statistics, Status, PredictionRequest, PredictionResponse, TrainingResponse, ScenarioDetail, ModelActivationResponse, Applicant
# Initialize FastAPI app
app = FastAPI(title="ML pipeline API", version="1.0.0")

# TODO: these scenarios will be implemented in a database and they are used as a mock data

scenarios = [
    Scenario(
        scenario_ID="scenario-001",
        scenario_name="Credit Score Prediction",
        description="Predicts credit score based on applicant data"
    ),
    Scenario(
        scenario_ID="scenario-002",
        scenario_name="Loan Approval Prediction",
        description="Predicts loan approval based on applicant data"
    )
]

models = {
    "scenario-001": [
        MLModel(
            model_ID="model-001",
            model_name="RandomForest v1",
            model_filename="rf_v1.pkl",
            statistics=Statistics(
                accuracy=0.85,
                precision=0.82,
                recall=0.79,
                f1_score=0.80
            ),
            creation_time=datetime.now(),
            status=Status(
                time=datetime.now(),
                model_status=ModelStatus.DEPLOYED
            )
        ),
        MLModel(
            model_ID="model-002",
            model_name="XGBoost v1",
            model_filename="xgb_v1.pkl",
            statistics=Statistics(
                accuracy=0.87,
                precision=0.85,
                recall=0.84,
                f1_score=0.84
            ),
            creation_time=datetime.now(),
            status=Status(
                time=datetime.now(),
                model_status=ModelStatus.INACTIVE
            )
        )
    ],
    "scenario-002": [
        MLModel(
            model_ID="model-003",
            model_name="LogisticRegression v1",
            model_filename="lr_v1.pkl",
            statistics=Statistics(
                accuracy=0.79,
                precision=0.77,
                recall=0.76,
                f1_score=0.76
            ),
            creation_time=datetime.now(),
            status=Status(
                time=datetime.now(),
                model_status=ModelStatus.DEPLOYED
            )
        )
    ]
}
# Active model tracker
active_models = {
    "scenario-001": "model-001",
    "scenario-002": "model-003"
}

@app.get("/")
def read_root():
    return {"message": "now it auto reloads but i need to request a page reaload manually"}

# GET /v1/scenarios
@app.get("/v1/scenarios", response_model=List[Scenario])
async def get_scenarios():
    print("GET /v1/scenarios - Returning list of available scenarios")
    return scenarios

# GET /v1/scenarios/{scenario_ID}
@app.get("/v1/scenarios/{scenario_ID}", response_model=ScenarioDetail)
async def get_scenario(scenario_ID: str = Path(..., description="The ID of the scenario to retrieve")):
    print(f"GET /v1/scenarios/{scenario_ID} - Retrieving scenario details")
    
    # Find the scenario
    scenario = next((s for s in scenarios if s.scenario_ID == scenario_ID), None)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Get the active model for this scenario
    active_model_id = active_models.get(scenario_ID)
    active_model = None
    
    if active_model_id and scenario_ID in models:
        active_model = next((m for m in models[scenario_ID] if m.model_ID == active_model_id), None)
    
    return ScenarioDetail(
        scenario_ID=scenario.scenario_ID,
        scenario_name=scenario.scenario_name,
        description=scenario.description,
        current_model=active_model
    )

# GET /v1/scenarios/{scenario_ID}/models
@app.get("/v1/scenarios/{scenario_ID}/models", response_model=List[MLModel])
async def get_scenario_models(scenario_ID: str = Path(..., description="The ID of the scenario")):
    print(f"GET /v1/scenarios/{scenario_ID}/models - Listing available models for the scenario")
    
    if scenario_ID not in models:
        raise HTTPException(status_code=404, detail="Scenario not found or has no models")
    
    return models[scenario_ID]

# POST /v1/scenarios/{scenario_ID}/predict
@app.post("/v1/scenarios/{scenario_ID}/predict", response_model=PredictionResponse)
async def predict(
    prediction_request: PredictionRequest,
    scenario_ID: str = Path(..., description="The ID of the scenario")
):
    print(f"POST /v1/scenarios/{scenario_ID}/predict - Running prediction using currently loaded model")
    print(f"Applicant data: {prediction_request.applicant}")
    
    # Check if scenario exists
    scenario = next((s for s in scenarios if s.scenario_ID == scenario_ID), None)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Check if there's an active model for this scenario
    if scenario_ID not in active_models:
        raise HTTPException(status_code=400, detail="No active model for this scenario")
    
    # In a real application, we would load the model and make a prediction
    # For this example, we'll just return a sample response
    return PredictionResponse(
        prediction_ID=str(uuid.uuid4()),
        result=True,
        confidence=0.85,
        timestamp=datetime.now()
    )

# POST /v1/scenarios/{scenario_ID}/train/training_data
@app.post("/v1/scenarios/{scenario_ID}/train/training_data", response_model=TrainingResponse)
async def train_with_data(
    applicants: List[Applicant],
    scenario_ID: str = Path(..., description="The ID of the scenario")
):
    print(f"POST /v1/scenarios/{scenario_ID}/train/training_data - Training model with provided data")
    print(f"Number of training records: {len(applicants)}")
    
    # Check if scenario exists
    scenario = next((s for s in scenarios if s.scenario_ID == scenario_ID), None)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # In a real application, this would initiate a training job
    return TrainingResponse(
        training_ID=str(uuid.uuid4()),
        status="training_started",
        timestamp=datetime.now()
    )

# POST /v1/scenarios/{scenario_ID}/train/{data_ID}
@app.post("/v1/scenarios/{scenario_ID}/train/{data_ID}", response_model=TrainingResponse)
async def train_with_data_id(
    scenario_ID: str = Path(..., description="The ID of the scenario"),
    data_ID: str = Path(..., description="The ID of the training data")
):
    print(f"POST /v1/scenarios/{scenario_ID}/train/{data_ID} - Training model with existing dataset")
    
    # Check if scenario exists
    scenario = next((s for s in scenarios if s.scenario_ID == scenario_ID), None)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # In a real application, this would retrieve the specified dataset and initiate a training job
    return TrainingResponse(
        training_ID=str(uuid.uuid4()),
        status="training_started",
        timestamp=datetime.now()
    )

# POST /v1/scenarios/{scenario_ID}/models/{model_ID}/activate
@app.post("/v1/scenarios/{scenario_ID}/models/{model_ID}/activate", response_model=ModelActivationResponse)
async def activate_model(
    scenario_ID: str = Path(..., description="The ID of the scenario"),
    model_ID: str = Path(..., description="The ID of the model to activate")
):
    print(f"POST /v1/scenarios/{scenario_ID}/models/{model_ID}/activate - Activating model")
    
    # Check if scenario exists
    scenario = next((s for s in scenarios if s.scenario_ID == scenario_ID), None)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Check if model exists for this scenario
    if scenario_ID not in models:
        raise HTTPException(status_code=404, detail="Scenario has no models")
    
    model = next((m for m in models[scenario_ID] if m.model_ID == model_ID), None)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found for this scenario")
    
    # Update the active model for this scenario
    active_models[scenario_ID] = model_ID
    
    return ModelActivationResponse(
        status="model_activated",
        timestamp=datetime.now(),
        activated_model_ID=model_ID
    )

# DELETE /v1/scenarios/{scenario_ID}/models/{model_ID}
@app.delete("/v1/scenarios/{scenario_ID}/models/{model_ID}")
async def delete_model(
    scenario_ID: str = Path(..., description="The ID of the scenario"),
    model_ID: str = Path(..., description="The ID of the model to delete")
):
    print(f"DELETE /v1/scenarios/{scenario_ID}/models/{model_ID} - Deleting model")
    
    # Check if scenario exists
    scenario = next((s for s in scenarios if s.scenario_ID == scenario_ID), None)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Check if model exists for this scenario
    if scenario_ID not in models:
        raise HTTPException(status_code=404, detail="Scenario has no models")
    
    model_index = next((i for i, m in enumerate(models[scenario_ID]) if m.model_ID == model_ID), None)
    if model_index is None:
        raise HTTPException(status_code=404, detail="Model not found for this scenario")
    
    # Check if the model is currently active
    if scenario_ID in active_models and active_models[scenario_ID] == model_ID:
        raise HTTPException(status_code=400, detail="Cannot delete an active model. Deactivate it first.")
    
    # Remove the model
    models[scenario_ID].pop(model_index)
    
    return {"message": "Model deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
