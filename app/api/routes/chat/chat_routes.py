import shutil
from fastapi.responses import StreamingResponse
from git import Tree
from sqlalchemy.orm import Session
from streamlit import user
from sympy import true
from app.api.depends import Database
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
import os
from app.core import settings
from app.api.models import User,Files
from app.api.utils.auth import get_current_user
from app.llm import split_documents
from app.llm import VectorStore, Embedding, RAGRetrievalPipeline, rag_from_llm, stream_chat_response
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
import asyncio
from app.api.schema import ChatStreamChunk, ChatStreamInput
from app.logs import logger

chat_router = APIRouter(prefix="/chat")
db_class = Database()



UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)



@chat_router.post("/upload-file")
async def upload_pdf_db(*,file: UploadFile = File(...), db: Session = Depends(db_class.get_db), current_user:User = Depends(get_current_user)):
    try:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        pdf = Files(file_name=file.filename, path=f"upload/{file.filename}", process_status=True, user_id=current_user.id)
        db.add(pdf)
        db.commit()
        db.refresh(pdf)
        chunks = split_documents(file_path)
        doc_content = [doc.page_content for doc in chunks]
        vector_store = VectorStore(pdf_id=pdf.id)
        embedding_manager = Embedding()
        embedding = embedding_manager.generate_embedding(doc_content)
        vector_store.add_documents(chunks, embedding)
        return {"filename": file.filename, "message": "PDF uploaded successfully!"}
    except FileNotFoundError:
        logger.error(f"error to reading file: {file.filename}")
        raise HTTPException(status_code=400, detail="error to reading file ")
    except Exception as e:
        logger.error(f"error to reading file: {str(e)}")
        raise HTTPException(status_code=500, detail="try again something went wrong")



@chat_router.post("/", response_model=ChatStreamChunk)
async def chat_stream(*, db: Session = Depends(db_class.get_db), query_in: ChatStreamInput, current_user:User = Depends(get_current_user)):
    try:
        query = query_in.query
        return StreamingResponse(stream_chat_response(query), media_type="application/x-ndjson")
    except Exception as e:
            logger.error(f"streaming error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))



        

# @chat_router.post("/")
# # def chat( db: Session = Depends(db_class.get_db), current_user:User = Depends(get_current_user)):
# def chat( db: Session = Depends(db_class.get_db)):
#     gro_llm = ChatGroq(api_key=settings.GROQ_API_KEY, model="gemma2-9b-it",temperature=0.1, max_tokens=1024)
#     openai_llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY,model="gpt-4o-mini", temperature=0.1,)
    
#     embedding_manager = Embedding()
#     vector_store = VectorStore()
#     rag_retrieval_pipeline = RAGRetrievalPipeline(vector_storage=vector_store, embedding_manager=embedding_manager)
#     result = rag_from_llm("details 2024-2025 budget details related to the agriculture industry", rag_retrieval_pipeline, openai_llm,)
#     print(result)
#     return {}




        

