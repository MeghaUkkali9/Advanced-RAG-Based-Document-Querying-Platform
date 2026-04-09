# advanced-rag-document-querying-portal

## Commands to be follwed:
```
conda create -n documentqueryingportal python = 3.10
```
```
conda activate documentqueryingportal
```

To install all packages required for this project:
pip install -r requirements.txt


What all should be having for this project
1. LLM model: open ai, groq, gemini, claude, hugging face
2. Embedding model: open ai, huggingface, gemini
3. vector database: ##inmemory ##ondisk ##cloud-based db

## why do we need setuptools
We use the setuptools library to package our project as a Python package so it can be installed and imported like any other libraries.

When we run:
```
pip install -e .
```

pip uses setuptools to install the project. The -e means editable mode (development mode). Instead of copying the code, Python creates a link to the project directory. During this process, setuptools creates a .egg-info folder.

This folder stores metadata about the project, such as:

1. project name
2. version
3. dependencies
4. author

This metadata helps pip and Python manage the package including installation, dependency tracking, and uninstallation.

To run this application: 
uvicorn api.main:app --reload, uvicorn api.main:app --port 8080 --reload
uvicorn is server to run an application.

Build Docker image:
                    docker build -t rag-based-document-portal .

Run docker container: 
                    docker run -d -p 8093:8080 --name rag-doc-portal rag-based-document-portal

Access swagger page: 
                    http://localhost:8093/docs

To Run tests: pytest tests/unit_tests.py -v

##Setup Pre hook 
cd ~/Documents/Advanced-RAG-Based-Document-Querying-Platform

touch .git/hooks/pre-push
chmod +x .git/hooks/pre-push

nano .git/hooks/pre-push

#!/bin/bash

echo "Running tests before push..."

PYTHONPATH=. pytest tests/
if [ $? -ne 0 ]; then
  echo "Tests failed. Push aborted."
  exit 1
fi

echo "Tests passed. Proceeding with push..."