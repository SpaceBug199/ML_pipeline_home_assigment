from pydantic import BaseModel, Field, field_validator
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

class PerformanceMetrics(str, Enum):
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    

class Applicant(BaseModel):
    user_id: str
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

class ModelStatistics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
        
class MLModel(BaseModel):
    model_id: str
    model_name: str
    model_filename: str
    statistics: ModelStatistics
    creation_time: datetime
    status: Status
    
# Additional models for the API
class Scenario(BaseModel):
    scenario_id: str
    scenario_name: str
    description: str
    current_model_id: Optional[MLModel] = None
    
    
class ScenarioDetail(BaseModel):
    scenario_id: str
    scenario_name: str
    description: str
    current_model_id: Optional[MLModel] = None

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



class TaxFilingPredictionRequest(BaseModel):
    """Request schema for tax filing completion prediction."""
    age: int = Field(..., ge=18, le=120)
    income: float = Field(..., ge=0)
    employment_type: str
    marital_status: str
    time_spent_on_platform: float = Field(..., ge=0)
    number_of_sessions: int = Field(..., ge=0)
    fields_filled_percentage: float = Field(..., ge=0, le=100)
    previous_year_filing: int = Field(..., ge=0, le=1)
    device_type: str
    referral_source: str
    
    @field_validator('employment_type')
    @classmethod
    def validate_employment(cls, v):
        valid_types = ['full_time', 'part_time', 'self_employed', 'unemployed', 'retired']
        if v.lower() not in valid_types:
            raise ValueError(f"employment_type must be one of {valid_types}")
        return v.lower()
    
    @field_validator('marital_status')
    @classmethod
    def validate_marital(cls, v):
        valid_statuses = ['single', 'married', 'divorced', 'widowed', 'separated']
        if v.lower() not in valid_statuses:
            raise ValueError(f"marital_status must be one of {valid_statuses}")
        return v.lower()
    
    @field_validator('device_type')
    @classmethod
    def validate_device(cls, v):
        valid_devices = ['mobile', 'desktop', 'tablet']
        if v.lower() not in valid_devices:
            raise ValueError(f"device_type must be one of {valid_devices}")
        return v.lower()
    
    @field_validator('referral_source')
    @classmethod
    def validate_referral(cls, v):
        valid_sources = ['friend_referral', 'organic_search', 'social_media_ad', 
                         'email_campaign', 'affiliate']
        if v.lower() not in valid_sources:
            raise ValueError(f"referral_source must be one of {valid_sources}")
        return v.lower()


class TaxFilingPredictionResponse(BaseModel):
    """Response schema for tax filing completion prediction."""
    will_complete_filing: bool
    confidence_score: float
    