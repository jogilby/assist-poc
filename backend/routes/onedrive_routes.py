from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
import httpx
import sqlite3
from logging import info
from session_mgmt import get_session

router = APIRouter()


@router.get("/root")
async def get_root_folder(request: Request):
    session_id = request.cookies.get("session_id")    
    info(f"Session ID: {session_id}")
    if not session_id:
        return RedirectResponse(url="/login")
    access_token = get_session(session_id)["access_token"]
    info(f"Access token: {access_token}")
    if not access_token:
        return RedirectResponse(url="/login")
    url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return JSONResponse(content=response.json())

@router.post("/select-folder")
async def select_folder(request: Request, folder_id: str, folder_name: str):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=403, detail="Unauthorized")
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO projects (user_id, folder_id, folder_name) VALUES (?, ?, ?)",
                   (user["sub"], folder_id, folder_name))
    conn.commit()
    conn.close()
    return {"message": "Folder selected", "folder_id": folder_id, "folder_name": folder_name}


@router.post("/sync-files")
async def sync_files(request: Request, folder_id: str):
    user = request.session.get("user")
    access_token = request.session.get("access_token")
    if not user or not access_token:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM projects WHERE user_id = ? AND folder_id = ?", (user["sub"], folder_id))
    project = cursor.fetchone()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project_id = project[0]
    
    url = f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}/children"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        files = response.json().get("value", [])
    
    existing_files = {row[0] for row in cursor.execute("SELECT file_id FROM files WHERE project_id = ?", (project_id,))}
    new_files = [(project_id, file["id"], file["name"]) for file in files if file["id"] not in existing_files]
    
    cursor.executemany("INSERT INTO files (project_id, file_id, file_name) VALUES (?, ?, ?)", new_files)
    cursor.execute("DELETE FROM files WHERE project_id = ? AND file_id NOT IN ({})".format(",".join(f"'{f['id']}'" for f in files)), (project_id,))
    
    conn.commit()
    conn.close()
    return {"message": "File sync complete", "added": len(new_files), "total": len(files)}
