from pydantic import BaseModel
from enum import Enum

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
    
    
    