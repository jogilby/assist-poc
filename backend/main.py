from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware
from routes.auth_routes import router as auth_router
from routes.onedrive_routes import router as onedrive_router
from routes.query_routes import router as query_router
import os
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from logging import basicConfig, info, INFO 

basicConfig(level=INFO)

# Load environment variables
load_dotenv()

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY"))
# Allow CORS for all origins, methods, and headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use ["https://example.com"] to restrict
    allow_credentials=True,
    allow_methods=["*"],  # Use ["GET", "POST"] to restrict
    allow_headers=["*"],  # Use ["Authorization", "Content-Type"] to restrict
)

# Include routers
app.include_router(auth_router, prefix="/auth")
app.include_router(onedrive_router, prefix="/onedrive")
app.include_router(query_router, prefix="/query")

# Initialize database
init_db()

@app.get("/")
def root():
    return {"message": "Welcome to the File Query System!"}

@app.get("/dashboard")
async def dashboard(request: Request):    
    session_id = request.session.get("session_id")
    info("Dashboard for session %s", session_id)
    if not session_id:
        return RedirectResponse(url="/login")
    return {"message": "Welcome", "session_id": session_id}