import json
from app.llm import VectorStore, Embedding
from typing import List, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from app.core import settings
from app.api.schema import ChatStreamChunk
import asyncio
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from app.logs import logger


class RAGRetrievalPipeline:
    """
    handle query based retrieval from vector store
    """
    def __init__(self, vector_storage:VectorStore, embedding_manager:Embedding)-> List[Dict[str, Any]]:
        self.vector_store_control = vector_storage
        self.embedding_control = embedding_manager

    def retrieve_from_store(self, query: str, top_k:int = 5, score_threshold:float=0.0):
        """
        retrieve information based on user query
        """

        # user query convert to embedding
        query_embedding = self.embedding_control.generate_embedding([query])[0]

        # query in  vector db

        result = self.vector_store_control.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            )
        if result["documents"] and result["documents"][0]:
            documents = result["documents"][0]
            metadatas = result["metadatas"][0]
            distances = result["distances"][0]
            ids = result["ids"][0]

        
        retrieved_docs = []
        for i, (doc_id, document, metadata, distance) in enumerate(zip(ids, documents, metadatas, distances)):

            # convert distance into similarity score chromo DB use cosine distance 
            similarity_score = 1-distance

            if similarity_score >=score_threshold:
                retrieved_docs.append({
                    "id":doc_id,
                    "content":document,
                    "metadata":metadata,
                    "similarity_score":similarity_score,
                    "distance":distance,
                    "rank":i+1,
                })
        print(f'Retrieved documents len {len(retrieved_docs)} ')
        print('documents are -')
        print('-'*10)
        print(retrieved_docs)

        return retrieved_docs

class FastAPIStreamCallback(BaseCallbackHandler):
    def __init__(self):
        self.queue = asyncio.Queue()

    async def on_llm_new_token(self, token: str, **kwargs):
        await self.queue.put(token)

    async def on_llm_end(self, *args, **kwargs):
        await self.queue.put("[END]")



async def stream_chat_response(query: str):
    callback = FastAPIStreamCallback()

    try:
        openai_llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model="gpt-4o-mini",
            temperature=0.1,
            streaming=True,
            callbacks=[callback],
        )

        embedding_manager = Embedding()
        vector_store = VectorStore()
        rag_retrieval_pipeline = RAGRetrievalPipeline(
            vector_storage=vector_store, embedding_manager=embedding_manager
        )

        result = rag_retrieval_pipeline.retrieve_from_store(query)
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        yield json.dumps(ChatStreamChunk(content=f"Initialization error: {e}", is_final=True).dict()) + "\n"
        return
    
    context = "\n\n".join([doc["content"] for doc in result]) if result else ""
    prompt_text = f"""
    Use the following context to answer accurately:
    Context:
    {context}

    Question:
    {query}

    Answer:
    """
    prompt = ChatPromptTemplate.from_template(prompt_text)
    chain = prompt | openai_llm

    # Run the chain in background and catch errors
    async def _run_chain():
        try:
            await chain.ainvoke({"query": query, "prompt": prompt})
        except Exception as e:
            await callback.queue.put(f"[ERROR]{str(e)}")
            await callback.queue.put("[END]")

    asyncio.create_task(_run_chain())

    # Stream tokens as they arrive
    while True:
        try:
            token = await callback.queue.get()
        except Exception as e:
            logger.error(f"Internal streamer error: {e}")
            yield json.dumps(ChatStreamChunk(content=f"Internal streamer error: {e}", is_final=True).dict()) + "\n"
            break

        if token == "[END]":
            yield json.dumps(ChatStreamChunk(content="", is_final=True).dict()) + "\n"
            break
        if isinstance(token, str) and token.startswith("[ERROR]"):
            err_text = token[len("[ERROR]"):]
            yield json.dumps(ChatStreamChunk(content=err_text, is_final=True).dict()) + "\n"
            break
        try:
            yield json.dumps(ChatStreamChunk(content=token).dict()) + "\n"
        except Exception as e:
            logger.error(f"Serialization error: {e}")
            yield json.dumps(ChatStreamChunk(content=f"Serialization error: {e}", is_final=True).dict()) + "\n"
            break


        


def rag_from_llm(query:str, retriever:RAGRetrievalPipeline,llm, top_k=3):
    """_summary_

    Args:
        query (str): _description_
        retriever (RAGRetrievalPipeline): _description_
        top_k (int, optional): _description_. Defaults to 3.
    """
    result = retriever.retrieve_from_store(query=query, top_k=top_k)
    context = "\n\n".join([doc["content"] for doc in result]) if result else ""
    if not context:
        print("there is not relevant context found in vector db for your query")

    prompt = f""" Use the flowing context and provide accurate answers
        Context:
        {context}

        Question:
        {query}

        Answers:"""
    prompt = ChatPromptTemplate.from_template(prompt)

    chain = prompt | llm
    response = chain.invoke(
        {"prompt":prompt,
         "query":query
         }
    )
    print("-"*10)
    # response = llm.invoke([prompt.format(context=context, query=query)])
    return response.content