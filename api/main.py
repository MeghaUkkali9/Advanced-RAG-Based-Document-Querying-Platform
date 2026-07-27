import os
from typing import Any, Dict, List, Optional
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from utils.file_adapter import FastAPIFileAdapter
from logger import GLOBAL_LOGGER as log

from src.document_ingestion.document_ingestion import (
    DocumentHandler,
    DocumentComparator,
    DocumentIngestor
    )
from src.doc_analyzer.data_analysis import DocumentAnalyzer
from src.document_comparison.document_comparison import DocumentComparatorLLM
from src.document_chat.retrieval import ConversationalRAG

app = FastAPI(
    title="Advanced RAG Based Document Querying Platform",
    version="0.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

FAISS_BASE = os.getenv("FAISS_BASE", "faiss_index")
UPLOAD_BASE = os.getenv("UPLOAD_BASE", "data")
FAISS_INDEX_NAME = os.getenv("FAISS_INDEX_NAME", "index")

BASE_DIR = Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.get("/", response_class=HTMLResponse)
async def serve_ui(request: Request):
    response = templates.TemplateResponse(request, "index.html", {})
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok", "service": "Document Querying Platform"}

def __read_pdf_handler(handler: DocumentHandler, path:str) -> str:
    if hasattr(handler, "read_pdf"):
        return handler.read_pdf(path)
    if hasattr(handler, "read_"):
        return handler.read_(path)
    raise RuntimeError("Document Handler has neither read_pdf nor read_ method")
    
@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)) -> Any:
    try:
        doc_handler = DocumentHandler()
        saved_path = doc_handler.save_pdf(FastAPIFileAdapter(file))
        text = __read_pdf_handler(doc_handler, saved_path)
        analyzer = DocumentAnalyzer()
        result = analyzer.analyze_document(text)
        return JSONResponse(content = result)
        
    except HTTPException as e:
        raise HTTPException(status_code=500, detail=f"Analyze failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")


@app.post("/compare")
async def compare_documents(
    reference: UploadFile = File(...),
    actual: UploadFile = File(...)
) -> Any:
    try:
        doc_compare = DocumentComparator()
        ref_path, act_path = doc_compare.save_uploaded_files(
            FastAPIFileAdapter(reference),
            FastAPIFileAdapter(actual))
        _ = ref_path, act_path
        combined_text = doc_compare.combine_documents()
        compare_documents = DocumentComparatorLLM()
        df = compare_documents.compare_documents(combined_text)
        return {
            "rows": df.to_dict(orient="records"),
            "session_id": doc_compare.session_id
        }
        
    except HTTPException as e:
        raise HTTPException(status_code=500, detail=f"Compare failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compare failed: {e}")


@app.post("/chat/index")
async def chat_build_index(
    files: List[UploadFile] = File(...),
    session_id: Optional[str] = Form(None),
    use_session_dirs: bool = Form(True),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    k: int = Form(5),
) -> Any:
    try:
        log.info(f"Indexing chat session. Session ID: {session_id}, Files: {[f.filename for f in files]}")
        wrapped = [FastAPIFileAdapter(f) for f in files]
        ci = DocumentIngestor(
            temp_base=UPLOAD_BASE,
            faiss_base=FAISS_BASE,
            use_session_dirs=use_session_dirs,
            session_id=session_id or None,
        )
       
        ci.build_retriver(
            wrapped, chunk_size=chunk_size, chunk_overlap=chunk_overlap, k=k
        )
        
        log.info(f"Index created successfully for session: {ci.session_id}")
        return {"session_id": ci.session_id, "k": k, "use_session_dirs": use_session_dirs}
    except HTTPException:
        raise
    except Exception as e:
        log.exception("Chat index building failed")
        raise HTTPException(status_code=500, detail=f"Indexing failed: {e}")

@app.post("/chat/query")
async def chat_query(
    question: str = Form(...),
    session_id: Optional[str] = Form(None),
    use_session_dirs: bool = Form(True),
    k: int = Form(5),
) -> Any:
    try:
        log.info(f"Received chat query: '{question}' | session: {session_id}")
        if use_session_dirs and not session_id:
            raise HTTPException(status_code=400, detail="session_id is required when use_session_dirs=True")

        index_dir = os.path.join(FAISS_BASE, session_id) if use_session_dirs else FAISS_BASE
        if not os.path.isdir(index_dir):
            raise HTTPException(status_code=404, detail=f"FAISS index not found at: {index_dir}")

        rag = ConversationalRAG(session_id=session_id)
        rag.load_retriever_from_faiss(index_dir, k=k, index_name=FAISS_INDEX_NAME) 
        response = rag.invoke(question, chat_history=[])
        log.info("Chat query handled successfully.")

        return {
            "answer": response,
            "session_id": session_id,
            "k": k,
            "engine": "LCEL-RAG"
        }
    except HTTPException:
        raise
    except Exception as e:
        log.exception("Chat query failed")
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")
