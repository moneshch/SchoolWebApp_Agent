from langchain_community.document_loaders import (
    PyPDFLoader
)

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

from langchain_chroma import Chroma

from .embeddings import embeddings


CHROMA_DB_DIR = "./chroma_langchain_db"

COLLECTION_NAME = "school_documents"


# =========================================================
# LOAD VECTOR STORE
# =========================================================

vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=CHROMA_DB_DIR
)


# =========================================================
# INGEST PDF
# =========================================================

def ingest_pdf(pdf_path):

    loader = PyPDFLoader(pdf_path)

    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    splits = splitter.split_documents(docs)

    vector_store.add_documents(splits)

    return len(splits)


# =========================================================
# LOAD VECTOR STORE
# =========================================================

def load_vectorstore():

    return vector_store