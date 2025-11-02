import os
from typing import List
import numpy as np
import chromadb
import uuid

class VectorStore:
    def __init__(self, pdf_id: str | None=None, collection_name: str = "pdf_collection", persist_directory: str = None):
        self.collection_name = collection_name
        # Calculate absolute path from project root
        if persist_directory is None:
            project_root = os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))))
            persist_directory = os.path.join(
                project_root, "data", "vector_store")
            print(f"Using default vector store path: {persist_directory}")

        self.persist_directory = os.path.abspath(
            persist_directory)  # Convert to absolute path
        self.client = None
        self.collection = None
        if pdf_id is None:
            self.pdf_id = uuid.uuid4().hex[:8]
        else:
             self.pdf_id = pdf_id
             
        self._initialize_vector_store()

    def _initialize_vector_store(self):
        try:
            print(
                f"Creating vector store directory at: {self.persist_directory}")
            # Create all parent directories if they don't exist
            os.makedirs(self.persist_directory, exist_ok=True)

            print("Initializing ChromaDB client...")
            self.client = chromadb.PersistentClient(
                path=self.persist_directory)

            print(f"Creating/getting collection: {self.collection_name}")
            # create or get the collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "PDF document embedding for RAG"}
            )

            print(
                f"Vector store initialized with collection '{self.collection_name}' at '{self.persist_directory}'")
            print(
                f"Number of vectors in the collection: {self.collection.count()}")

        except Exception as e:
            print(f"Error initializing vector store: {str(e)}")
            # Re-raise the exception after logging
            raise RuntimeError(
                f"Failed to initialize vector store: {str(e)}") from e

    def add_documents(self, documents: List[any], embedding: np.ndarray):
        try:
            len_docs = len(documents)
            len_embedding = len(embedding)

            if (len_docs != len_embedding):
                raise ValueError(
                    f"The number of documents {len_docs} must match the number of embeddings {len_embedding}. ")

            print(f"Adding {len_docs} documents to the vector store...")

            ids = []
            metadatas = []
            doc_texts = []
            embedding_list = []

            for i, (doc, embed) in enumerate(zip(documents, embedding)):
                doc_id = f"{self.pdf_id}_{i}"

                # meta data
                ids.append(doc_id)
                meta_data = dict(doc.metadata)
                meta_data["doc_index"] = i
                meta_data["content_length"] = len(doc.page_content)
                metadatas.append(meta_data)

                # doc
                doc_texts.append(doc.page_content)

                # embedding
                embedding_list.append(embed.tolist())

            self.collection.add(
                ids=ids,
                documents=doc_texts,
                metadatas=metadatas,
                embeddings=embedding_list,
            )

            print(
                f"Successfully added {len_docs} documents to the vector store. Total vectors now: {self.collection.count()}\n\n")

        except Exception as e:
            print(f"An error occurred while adding documents: {e}")
