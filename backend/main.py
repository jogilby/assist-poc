from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from routes.auth_routes import router as auth_router
from routes.onedrive_routes import router as onedrive_router
from routes.query_routes import router as query_router
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY"))

# Include routers
app.include_router(auth_router, prefix="/auth")
app.include_router(onedrive_router, prefix="/onedrive")
app.include_router(query_router, prefix="/query")

@app.get("/")
def root():
    return {"message": "Welcome to the File Query System!"}