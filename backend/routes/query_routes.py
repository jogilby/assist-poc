from fastapi import APIRouter, Request, HTTPException
import openai
import sqlite3
import os

router = APIRouter()
openai.api_key = os.getenv("OPENAI_API_KEY")

@router.post("/")
async def query_documents(request: Request, project_id: int = None, query: str = ""):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    if project_id:
        cursor.execute("SELECT file_content FROM files WHERE project_id = ?", (project_id,))
    else:
        cursor.execute("SELECT file_content FROM files")
    
    documents = [row[0] for row in cursor.fetchall() if row[0]]
    conn.close()
    
    if not documents:
        raise HTTPException(status_code=404, detail="No documents found")
    
    prompt = f"You are an AI assistant. Answer the following query based on these documents:\n\n{query}\n\nDocuments:\n{documents}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return {"response": response["choices"][0]["message"]["content"]}