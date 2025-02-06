from fastapi import APIRouter, Request, HTTPException, Response, Cookie
from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse
import os
from logging import info
import sqlite3
import session_mgmt
from typing import Union
from fastapi.responses import HTMLResponse

router = APIRouter()

# OAuth Setup
oauth = OAuth()
oauth.register(
    name="microsoft",
    client_id=os.getenv("MICROSOFT_CLIENT_ID"),
    client_secret=os.getenv("MICROSOFT_CLIENT_SECRET"),
    server_metadata_url="https://login.microsoftonline.com/ba996644-d001-41de-b4ab-a45ca8507b5e/v2.0/.well-known/openid-configuration",
    #multi-tenant server_metadata_url="https://login.microsoftonline.com/organizations/v2.0/.well-known/openid-configuration",    
    #authorize_url="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
    #access_token_url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
    client_kwargs={"scope": "openid email profile Files.ReadWrite.All"}
)

@router.get("/login")
async def login(request: Request, response: Response):
    redirect_uri = str(request.url_for("auth"))
    return await oauth.microsoft.authorize_redirect(request, redirect_uri)

@router.get("/callback")
async def auth(request: Request):
    info("Entered callback function")
    token = await oauth.microsoft.authorize_access_token(request)    
    if "id_token" not in token:
        raise HTTPException(status_code=400, detail="Missing id_token in OAuth response") 
    if "userinfo" not in token:
        raise HTTPException(status_code=400, detail="Missing userinfo in OAuth response") 
    if "access_token" not in token:
        raise HTTPException(status_code=400, detail="Missing access_token in OAuth response") 
    user_info = token["userinfo"]
    access_token = token["access_token"]
    session_id = session_mgmt.create_user_session(user_info["oid"], "Microsoft", access_token)
    request.session["session_id"] = session_id
    info("Started session %s for user %s", session_id, user_info["email"])
    return RedirectResponse(url="com.mytestapp://?session_id=%s&name=%s&email=%s" % (session_id, user_info["name"], user_info["email"]))
   

@router.get("/logout")
async def logout(request: Request):    
    session_id = request.session.get("session_id")
    if not session_id:
        return {"message": "No session found"}  
    request.session.pop("session_id", None)
    session_mgmt.delete_session(session_id)
    info("Deleted session %s", session_id)

    return RedirectResponse(url="/dashboard")

@router.get("/sessiondebug")
async def session_debug(request: Request):
    #user = request.session.get("user")
    #if not user:
    #    raise HTTPException(status_code=403, detail="Unauthorized")
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT session_id, user_id, provider, creation, expiration FROM sessions")
    
    allsessions = [row[0] for row in cursor.fetchall() if row[0]]
    conn.close()
    
    if not allsessions:
        return {"message": "No sessions found"}
        
    return {"response": allsessions}