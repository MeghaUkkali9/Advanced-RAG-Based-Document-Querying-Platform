# Advanced RAG Based Document Querying Platform

This is a document Q&A tool. You upload your documents, PDF, DOCX or TXT, and instead of reading the whole thing yourself you just ask questions and it answers based on what's actually in the document.

## What it actually does

In simple words this is what happens behind the scenes:

1. You upload a document.
2. The document gets split into small chunks since an LLM can't read a 200 page PDF in one go.
3. Each chunk gets converted into an embedding, basically a bunch of numbers that represent the meaning of that text, and stored in a FAISS vector database.
4. When you ask a question it finds the chunks that are most relevant to your question, then sends only those chunks plus your question to the LLM.
5. The LLM answers using that context so the answer is grounded in your document instead of the model just making things up.

This approach is called RAG, short for Retrieval Augmented Generation.

## Features

Chat with documents. Upload one or more PDFs, DOCX or TXT files and have a proper back and forth conversation about them. It remembers what you asked earlier in the same session.

Analyze a document. Upload a single PDF and get a structured summary out of it.

Compare documents. Upload two PDFs, like two versions of a contract, and get the differences between them.

There's a simple web UI included, or you can just hit the API directly through the Swagger docs at `/docs`.

## Tech stack

FastAPI for the backend server. LangChain to wire up the LLM, retriever and prompts. FAISS as the vector database for storing document embeddings. OpenAI and Groq as the LLM providers, configurable in `config/config.yaml`. Docker to containerize the app. AWS ECR and ECS for deployment, details in `docs/deployment.md`.

## Running it locally

Create and activate the environment:
```
conda create -n documentqueryingportal python=3.10
conda activate documentqueryingportal
```

Install the dependencies:
```
pip install -r requirements.txt
```

### Why do we need setuptools

We use the setuptools library to package our project as a Python package so it can be installed and imported like any other library.

When we run:
```
pip install -e .
```
pip uses setuptools to install the project. The `-e` means editable mode, or development mode. Instead of copying the code, Python creates a link to the project directory. During this process setuptools creates a `.egg-info` folder.

This folder stores metadata about the project such as:
1. project name
2. version
3. dependencies
4. author

This metadata helps pip and Python manage the package, including installation, dependency tracking and uninstallation.

### Run the app

```
uvicorn api.main:app --reload
```
uvicorn is the server that actually runs the FastAPI app. Once it's running open `http://localhost:8000` for the UI or `http://localhost:8000/docs` for the API.

### Run with Docker

Build the image:
```
docker build -t rag-based-document-portal .
```

Run the container:
```
docker run -d -p 8093:8080 --name rag-doc-portal rag-based-document-portal
```

Then open `http://localhost:8093/docs` for the Swagger page.

### Run tests

```
pytest tests/ -v
```

There's also a pre-push git hook set up that runs the tests automatically before every push so a broken build doesn't accidentally get pushed. Setup details are in `docs/deployment.md`.

## Deployment

This app is deployed on AWS using ECR and ECS through GitHub Actions. The full setup, IAM roles, secrets, task definitions, is written up separately in `docs/deployment.md` so this README stays focused on what the project is and how to run it.
