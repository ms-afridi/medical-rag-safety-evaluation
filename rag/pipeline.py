import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate

# 1. Load configuration from .env
load_dotenv()

class MedicalRAGSystem:
    def __init__(self, model_name):
        # Initialize Groq LLM with a specific model from your .env
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model_name=model_name,
            temperature=float(os.getenv("TEMPERATURE", 0.0))
        )
        
        # Load Embedding Model (Local)
        self.embeddings = HuggingFaceEmbeddings(model_name=os.getenv("EMBEDDING_MODEL"))
        
        # Connect to the Vector Database built by ingest.py
        self.vector_db = Chroma(
            persist_directory="rag/index", 
            embedding_function=self.embeddings
        )

    def get_plain_response(self, question):
        """Standard LLM response with a strict length constraint for fair comparison."""
        prompt = ChatPromptTemplate.from_template("""
        You are an informational health assistant.
        Do not provide diagnosis or treatment.
        Answer the question in 4–6 concise sentences (approximately 80–120 words).
        If you are unsure, say you do not know.
        
        QUESTION: {question}
        """)
        chain = prompt | self.llm
        return chain.invoke({"question": question}).content

    def get_rag_response(self, question):
        """RAG response using WHO guidelines with the same length constraint."""
        # Retrieve top 5 chunks to ensure the model has enough context to write 150-200 words
        docs = self.vector_db.similarity_search(question, k=5)
        context = "\n".join([doc.page_content for doc in docs])
        
        prompt = ChatPromptTemplate.from_template("""
        You are a clinical decision support assistant.
        Use the provided WHO guidance when relevant.
        Do not provide diagnosis or treatment.

        Rules:
        1. If the WHO guidance supports an answer, use it.
        2. If the guidance is insufficient, clearly state that the information is not available and respond concisely without speculation.
        3. Answer in 4–6 concise sentences (approximately 80–120 words).
        4. You may reference WHO guidance explicitly.
        
        WHO CONTEXT: {context}
        QUESTION: {question}
        """)

        chain = prompt | self.llm
        return chain.invoke({"context": context, "question": question}).content
