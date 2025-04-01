from enum import Enum, auto
from typing import Optional

class TableName(str, Enum):
    MODELS_BUCKET = "models",
    TRAINING_DATA_BUCKET = "training-data",
    SCENARIOS = "scenarios",
    ML_MODELS = "ml_models",
    SCENARIO_MODELS = "scenario_models",
    PREDICTION_RESPONSES = "prediction_responses",
    TRAINING_DATA = "training_data",
    APPLICANTS = "applicants",
    
    def __str__(self) -> str:
        return self.value