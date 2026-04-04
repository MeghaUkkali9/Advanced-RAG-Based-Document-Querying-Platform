import os
from typing import Any, Dict

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(
    title="Advanced RAG Based Document Querying Platform",
    version="0.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"] 
)

app.mount("/static", StaticFiles(directory="../static"), name="static")
templates = Jinja2Templates(directory="../templates")

# Routes
@app.get("/", response_class=HTMLResponse)
async def serve_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok", "service": "Document Querying Platform"}


@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)) -> Any:
    try:
        return {"message": "Analyze endpoint not implemented yet"}
    except HTTPException as e:
        raise HTTPException(status_code=500, detail=f"Analyze failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")


@app.post("/compare")
async def compare_documents(
    references: UploadFile = File(...),
    actual: UploadFile = File(...)
) -> Any:
    try:
        return {"message": "Compare endpoint not implemented yet"}
    except HTTPException as e:
        raise HTTPException(status_code=500, detail=f"Compare failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compare failed: {e}")


@app.post("/chat/index")
async def chat_build_index() -> Any:
    try:
        return {"message": "Chat index not implemented yet"}
    except HTTPException as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {e}")


@app.post("/chat/query")
async def chat_query() -> Any:
    try:
        return {"message": "Chat query not implemented yet"}
    except HTTPException as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")