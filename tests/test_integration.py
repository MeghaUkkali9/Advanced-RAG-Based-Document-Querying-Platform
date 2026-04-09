import io
import pytest
from fastapi.testclient import TestClient
from api.main import app

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_health_integration(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

def test_home_ui_integration(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "<html" in res.text

def test_analyze_integration(client, monkeypatch):
    class MockHandler:
        def save_pdf(self, file):
            return "dummy.pdf"

        def read_pdf(self, path):
            return "This is a test document."

    class MockAnalyzer:
        def analyze_document(self, text):
            return {"summary": "This is a test summary"}

    monkeypatch.setattr("api.main.DocumentHandler", lambda: MockHandler())
    monkeypatch.setattr("api.main.DocumentAnalyzer", lambda: MockAnalyzer())

    file = ("test.pdf", io.BytesIO(b"fake content"), "application/pdf")

    res = client.post("/analyze", files={"file": file})

    assert res.status_code == 200
    assert "summary" in res.json()

def test_compare_integration(client, monkeypatch):
    class MockComparator:
        session_id = "int-123"

        def save_uploaded_files(self, ref, act):
            return "ref.pdf", "act.pdf"

        def combine_documents(self):
            return "combined content"

    class MockLLM:
        def compare_documents(self, text):
            class DF:
                def to_dict(self, orient):
                    return [{"diff": "ok"}]
            return DF()

    monkeypatch.setattr("api.main.DocumentComparator", lambda: MockComparator())
    monkeypatch.setattr("api.main.DocumentComparatorLLM", lambda: MockLLM())

    files = {
        "reference": ("ref.pdf", io.BytesIO(b"ref"), "application/pdf"),
        "actual": ("act.pdf", io.BytesIO(b"act"), "application/pdf"),
    }

    res = client.post("/compare", files=files)

    assert res.status_code == 200
    assert "rows" in res.json()

def test_chat_query_integration(client, monkeypatch):
    class MockRAG:
        def __init__(self, session_id=None):
            pass

        def load_retriever_from_faiss(self, *args, **kwargs):
            return

        def invoke(self, question, chat_history):
            return "integration answer"

    monkeypatch.setattr("api.main.ConversationalRAG", lambda *a, **k: MockRAG())
    monkeypatch.setattr("os.path.isdir", lambda x: True)

    res = client.post(
        "/chat/query",
        data={
            "question": "Explain this",
            "session_id": "abc",
            "use_session_dirs": "true",
        },
    )

    assert res.status_code == 200
    assert res.json()["answer"] == "integration answer"