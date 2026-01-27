import os
import shutil
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# 1. Load configuration
load_dotenv()

def build_vector_db():
    # Define paths
    data_path = "data/medical_guidelines/WHO"
    index_path = "rag/index"

    print(f"🧹 Cleaning old index at {index_path}...")
    if os.path.exists(index_path):
        shutil.rmtree(index_path)

    print(f"🛠️  Step 1: Loading WHO Guidelines from {data_path}...")
    # Fix: Added encoding='utf-8' inside loader_kwargs to prevent UnicodeDecodeErrors
    try:
        loader = DirectoryLoader(
            data_path, 
            glob="./*.txt", 
            loader_cls=TextLoader,
            loader_kwargs={'encoding': 'utf-8'}
        )
        documents = loader.load()
        print(f"✅ Loaded {len(documents)} source files.")
    except Exception as e:
        print(f"❌ Error loading documents: {e}")
        return

    print(f"✂️  Step 2: Chunking text (Size: {os.getenv('CHUNK_SIZE')}, Overlap: {os.getenv('CHUNK_OVERLAP')})...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=int(os.getenv("CHUNK_SIZE", 512)),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", 50)),
        length_function=len,
        add_start_index=True, # Useful for research to know where chunks came from
    )
    chunks = text_splitter.split_documents(documents)
    print(f"✅ Split into {len(chunks)} semantic chunks.")

    print(f"🧠 Step 3: Generating Embeddings [{os.getenv('EMBEDDING_MODEL')}]...")
    try:
        embeddings = HuggingFaceEmbeddings(model_name=os.getenv("EMBEDDING_MODEL"))
        
        print(f"💾 Saving to Vector Store at {index_path}...")
        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=index_path
        )
        print(f"✅ Success! Vector database is ready for research.")
    except Exception as e:
        print(f"❌ Error creating vector store: {e}")

if __name__ == "__main__":
    build_vector_db()
