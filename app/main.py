from fastapi import FastAPI, HTTPException, Path
from datetime import datetime
from models import Scenario, MLModel, ModelStatus, Statistics, Status
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