from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import business, assessment, upload, auth

#app = FastAPI(title=settings.app_name)
app = FastAPI()
# CORS middleware - Explicitly allow localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    max_age=3600,
)

# Include routers
app.include_router(auth.router)
app.include_router(business.router)
app.include_router(assessment.router)
app.include_router(upload.router)

#@app.get("/health")
#async def health_check():
    #return {"status": "healthy", "app": settings.app_name}
def health():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "Financial Health Assessment Platform API"}
