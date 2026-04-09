import io
import pytest
from fastapi.testclient import TestClient
from api.main import app

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_home_ui(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "Document Portal" in res.text

def test_analyze_document(client, monkeypatch):
    class MockHandler:
        def save_pdf(self, file):
            return "dummy.pdf"

        def read_pdf(self, path):
            return "dummy text"

    class MockAnalyzer:
        def analyze_document(self, text):
            return {"summary": "ok"}

    monkeypatch.setattr(
        "api.main.DocumentHandler", lambda: MockHandler()
    )
    monkeypatch.setattr(
        "api.main.DocumentAnalyzer", lambda: MockAnalyzer()
    )

    file = ("test.pdf", io.BytesIO(b"fake pdf content"), "application/pdf")

    res = client.post("/analyze", files={"file": file})

    assert res.status_code == 200
    assert res.json()["summary"] == "ok"

def test_compare_documents(client, monkeypatch):
    class MockComparator:
        session_id = "123"

        def save_uploaded_files(self, ref, act):
            return "ref.pdf", "act.pdf"

        def combine_documents(self):
            return "combined text"

    class MockLLM:
        def compare_documents(self, text):
            class DF:
                def to_dict(self, orient):
                    return [{"result": "ok"}]
            return DF()

    monkeypatch.setattr(
        "api.main.DocumentComparator", lambda: MockComparator()
    )
    monkeypatch.setattr(
        "api.main.DocumentComparatorLLM", lambda: MockLLM()
    )

    files = {
        "reference": ("ref.pdf", io.BytesIO(b"ref"), "application/pdf"),
        "actual": ("act.pdf", io.BytesIO(b"act"), "application/pdf"),
    }

    res = client.post("/compare", files=files)

    assert res.status_code == 200
    assert "rows" in res.json()
    assert res.json()["session_id"] == "123"

def test_chat_index(client, monkeypatch):
    class MockIngestor:
        session_id = "abc"

        def __init__(self, *args, **kwargs):
            pass

        def build_retriver(self, *args, **kwargs):
            return

    monkeypatch.setattr(
        "api.main.DocumentIngestor", lambda *a, **k: MockIngestor()
    )

    files = [
        ("files", ("doc.pdf", io.BytesIO(b"data"), "application/pdf"))
    ]

    res = client.post("/chat/index", files=files)

    assert res.status_code == 200
    assert res.json()["session_id"] == "abc"

def test_chat_query(client, monkeypatch):
    class MockRAG:
        def __init__(self, session_id=None):
            pass

        def load_retriever_from_faiss(self, *args, **kwargs):
            return

        def invoke(self, question, chat_history):
            return "mock answer"

    monkeypatch.setattr(
        "api.main.ConversationalRAG", lambda *a, **k: MockRAG()
    )

    # also mock os.path.isdir
    monkeypatch.setattr("os.path.isdir", lambda x: True)

    res = client.post(
        "/chat/query",
        data={
            "question": "What is this?",
            "session_id": "abc",
            "use_session_dirs": "true",
        },
    )

    assert res.status_code == 200
    assert res.json()["answer"] == "mock answer"
    
def test_analyze_failure(client, monkeypatch):
    def fail(*args, **kwargs):
        raise Exception("boom")

    monkeypatch.setattr("api.main.DocumentAnalyzer", fail)

    file = ("test.pdf", io.BytesIO(b"data"), "application/pdf")
    res = client.post("/analyze", files={"file": file})

    assert res.status_code == 500
    
def test_chat_query_missing_session(client):
    res = client.post(
        "/chat/query",
        data={
            "question": "Hello",
            "use_session_dirs": "true"
        },
    )
    assert res.status_code == 400