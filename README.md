# FastAPI Project

## Overview
- This is a FastAPI project with PostgreSQL connectivity, vector store integration using ChromaDB, and structured API routes, models, and schemas.

## important
- Two llm options are added openai, Groq
- currently using openai llm to get response please attach openai key in env file, 


## embeddings
for creating embedding using "all-MiniLM-L6-v2"


## setup 
- create python virtual env
- install requirement.txt
- for vscode debug mode

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug FastAPI (Uvicorn)",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "main:app",
        "--reload",
        "--host",
        "127.0.0.1",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": true,
      "env": {
        "ENV": "dev"
      }
    }
  ]
}
```

## run terminal use 
- main.py 

## make sure postgres sql connectivity 
- need to run alembic revision and migration using alembic revision --autogenerate -m "initial" alembic upgrade head

## streaming test
- added html file for streaming test app/core/streaming.html

## vector store
- using chromadb data/vector_store 

## app log
- application logs are available /logs/app.log

## file upload
- uploaded files are storing app/uploads


## Requirements
- Python 3.9+
- PostgreSQL
- FastAPI
- ChromaDB
- Alembic (for database migrations)

---


