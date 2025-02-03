from fastapi import APIRouter, Request, HTTPException
from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse
import os

router = APIRouter()

# OAuth Setup
oauth = OAuth()
oauth.register(
    name="microsoft",
    client_id=os.getenv("MICROSOFT_CLIENT_ID"),
    client_secret=os.getenv("MICROSOFT_CLIENT_SECRET"),
    authorize_url="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
    access_token_url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
    client_kwargs={"scope": "openid email profile Files.ReadWrite.All"}
)

@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth")
    return await oauth.microsoft.authorize_redirect(request, redirect_uri)

@router.get("/callback")
async def auth(request: Request):
    token = await oauth.microsoft.authorize_access_token(request)
    user_info = await oauth.microsoft.parse_id_token(request, token)
    if not user_info:
        raise HTTPException(status_code=400, detail="Authentication failed")
    request.session["user"] = user_info
    return RedirectResponse(url="/dashboard")