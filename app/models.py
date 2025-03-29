from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import  Optional


class EmploymentType(str, Enum):
    FULL = "full_time"
    PART = "part_time"
    UNEMPLOYED = "unemployed"
    
class MaritalStatus(str, Enum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced" 

class DeviceType(str, Enum):
    DESKOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"

class Applicant(BaseModel):
    user_ID: str
    age: int
    income: float
    employment_type: EmploymentType
    marital_status: MaritalStatus
    time_spent_on_platform: float
    number_of_sesions: int
    fields_filled_precentage: float
    previoud_year_filing: bool
    device_type: DeviceType
    referral_source: str
    completed_filing: bool
    
    
class ModelStatus(str, Enum):
    TRAINING = "training"
    DEPLOYED = "deployed"
    FAILES = "failed"
    INACTIVE = "inactive"
    PENDING = "pending"    
        
class Status(BaseModel):
    time: datetime
    model_status: ModelStatus

class Statistics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
        
class MLModel(BaseModel):
    model_ID: str
    model_name: str
    model_filename: str
    statistics: Statistics
    creation_time: datetime
    status: Status
    
# Additional models for the API
class Scenario(BaseModel):
    scenario_ID: str
    scenario_name: str
    description: str
    
class ScenarioDetail(BaseModel):
    scenario_ID: str
    scenario_name: str
    description: str
    current_model: Optional[MLModel] = None

class PredictionRequest(BaseModel):
    applicant: Applicant

class PredictionResponse(BaseModel):
    prediction_ID: str
    result: bool
    confidence: float
    timestamp: datetime

class TrainingResponse(BaseModel):
    training_ID: str
    status: str
    timestamp: datetime
    
class ModelActivationResponse(BaseModel):
    status: str
    timestamp: datetime
    activated_model_ID: str
