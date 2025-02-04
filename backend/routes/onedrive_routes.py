from fastapi import APIRouter, Request, HTTPException
import httpx

router = APIRouter()

@router.get("/root")
async def get_root_folder(request: Request):
    access_token = request.session.get("access_token")
    if not access_token:
        return HTTPException(status_code=403, detail="Unauthorized")
    
    url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

@router.post("/sync-files")
async def sync_files(request: Request, folder_id: str):
    user = request.session.get("user")
    access_token = request.session.get("access_token")
    if not user or not access_token:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    url = f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}/children"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()