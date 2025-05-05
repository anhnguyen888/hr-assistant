import os
import argparse
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PDFMinerLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

# Import the custom database utilities
from db_utils import init_database, get_pgvector_store, delete_collection, collection_exists

# Tải biến môi trường
load_dotenv()

# Cấu hình đường dẫn
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# Default collection name for documents
COLLECTION_NAME = "hr_documents"

def load_documents():
    """Tải tất cả tài liệu từ thư mục data"""
    loaders = {
        "pdf": DirectoryLoader(f"{DATA_PATH}", glob="**/*.pdf", loader_cls=PDFMinerLoader),
        "txt": DirectoryLoader(f"{DATA_PATH}", glob="**/*.txt", loader_cls=TextLoader),
    }
    
    documents = []
    for loader_type, loader in loaders.items():
        print(f"Loading {loader_type} documents...")
        documents.extend(loader.load())
    
    return documents

# def process_documents(documents):
#     """Chia nhỏ tài liệu và tạo embeddings"""
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000,
#         chunk_overlap=200,
#     )
#     chunks = text_splitter.split_documents(documents)
    
#     # Tạo embeddings
#     embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
#     # Lưu vào Chroma
#     vectordb = Chroma.from_documents(
#         documents=chunks,
#         embedding=embeddings,
#         persist_directory=DB_PATH
#     )
    
#     # Lưu cơ sở dữ liệu
#     vectordb.persist()
#     print(f"Ingested {len(chunks)} document chunks into {DB_PATH}")
    
#     return vectordb

def process_documents(documents, collection_name=COLLECTION_NAME, recreate=False):
    """Chia nhỏ tài liệu và tạo embeddings vào PostgreSQL với pgvector"""
    # Initialize the database first
    init_database()
    
    # Check if collection exists and delete if recreate is True
    if collection_exists(collection_name) and recreate:
        print(f"Deleting existing collection {collection_name}...")
        delete_collection(collection_name)
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )
    chunks = text_splitter.split_documents(documents)
    
    # Sử dụng HuggingFaceEmbeddings 
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Get PGVector store
    vectordb = get_pgvector_store(collection_name=collection_name, embedding_function=embeddings)
    
    # Add documents to the store
    vectordb.add_documents(documents=chunks)
    
    print(f"Ingested {len(chunks)} document chunks into PostgreSQL collection '{collection_name}'")
    
    return vectordb

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest documents into PostgreSQL vector database")
    parser.add_argument("--collection", type=str, default=COLLECTION_NAME, help="Collection name to store documents")
    parser.add_argument("--recreate", action="store_true", help="Recreate collection if exists")
    args = parser.parse_args()
    
    documents = load_documents()
    print(f"Loaded {len(documents)} documents")
    process_documents(documents, collection_name=args.collection, recreate=args.recreate)
