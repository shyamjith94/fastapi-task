import os
from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter


def read_pdf(file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The folder {file_path} does not exist.")
        all_document=[]
        # pdf_files = (Path(folder_path)).glob("**/*.pdf")
        # pdf_files = list(pdf_files)  # Convert the generator to a list
        

        print("start processing file",file_path)
        loader = PyPDFLoader(str(file_path))
        documents = loader.load()

        print("Document length before split",len(documents), end="\n")
        # add some more meta data
        for doc in documents:
            doc.metadata["source"] = str(file_path)
            doc.metadata["type"] = "pdf"
        all_document.extend(documents)
        print(f"Number of document process from dir{len(all_document)}",  end="\n")
        return all_document
    except Exception as e:
        print(f"An error occurred: {e}")

def split_documents(file_path: str, chunk_size: int=1000, chunk_overlap: int=200):
    documents = read_pdf(file_path)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        separators=["\n","\n\n", " ", ""],
        chunk_overlap=chunk_overlap,
        length_function=len,
        )
    splitted_docs = splitter.split_documents(documents)

    print(f"Number of document {len(documents)} after split {len(splitted_docs)}",  end="\n\n")

    if splitted_docs:
        print("Example of splitted document content\n", splitted_docs[0].page_content[:200], end="\n\n")
        print("Example of splitted document metadata\n", splitted_docs[0].metadata, end="\n\n")
    return splitted_docs