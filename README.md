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

This metadata helps pip and Python manage the package including installation, dependency tracking, and uninstallation.

