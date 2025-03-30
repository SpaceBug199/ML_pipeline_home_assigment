from fastapi import FastAPI
from routes.crud import router as crud_router
from routes.inference import router as inference_router
from routes.training import router as training_router

# Initialize FastAPI app
app = FastAPI(title="ML pipeline API", version="1.0.0")

#add crud routes
app.include_router(crud_router)

#add training routes
app.include_router(training_router)

#add  inference routes
app.include_router(inference_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
