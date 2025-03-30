import uuid
from typing import List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from supabase import Client

from models.models import Scenario
from database.database import get_db
from database.crud import get_scenarios

router = APIRouter()
STORAGE_BUCKET = "training-data"

@router.get("/")
def read_root():
    return {"message": "See the ML pipeline documentation on how to use this training and inference pipeline"}

# GET /v1/scenarios
@router.get("/v1/scenarios", response_model=List[Scenario])
async def get_scenarios_list( supabase: Client = Depends(get_db)):
    print("GET /v1/scenarios - Returning list of available scenarios")
    try:
        scenarios = await get_scenarios(supabase)
        if scenarios == None:
            raise HTTPException(status_code=404, detail="No Scenarios found")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    scenarios_data = scenarios
    print (scenarios_data)
    return scenarios_data


@router.post("/v1/scenarios/{scenario_ID}/train/training_data")
async def upload_training_data_file(
    file: UploadFile = File(...), 
    supabase: Client = Depends(get_db)):
    try:
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed.")
        file_uuid = str(uuid.uuid4())
        content = await file.read()
        file_path = f"{file_uuid}/{file.filename}"
        storage_response = supabase.storage\
                .from_(STORAGE_BUCKET)\
                .upload(file_path, content)
        if not storage_response:
            raise HTTPException(status_code=500, detail="Failed to upload file to storage.")

        file_url = f"/storage/v1/object/public/{STORAGE_BUCKET}/{file_path}"
        data = {
            "model_training_data_id": file_uuid,
            "model_training_data_url": file_url,
            "model_training_data_name": file.filename,
            "used_status": False,
            "created_at": datetime.now().isoformat()
        }

        db_response = supabase.table("training_data").insert(data).execute()
        if not db_response:
            raise HTTPException(status_code=500, detail="Failed to insert file metadata into database.")
        return {"message": "File uploaded successfully", "file_id": file_uuid, "file_url": file_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))