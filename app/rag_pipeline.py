"""
RAG Pipeline: PDF processing, embeddings, and retrieval
"""
import streamlit as st
import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List, Dict
import io
from app.config import CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_CHUNKS, EMBEDDING_MODEL

class RAGPipeline:
    """Handles PDF processing, chunking, embedding, and retrieval"""
    
    def __init__(self):
        """Initialize RAG pipeline with embedding model"""
        if "embedding_model" not in st.session_state:
            with st.spinner("Loading embedding model..."):
                st.session_state.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        
        self.embedding_model = st.session_state.embedding_model
        self.dimension = self.embedding_model.get_sentence_embedding_dimension()
        
        # Initialize vector store if not exists
        if "vector_store" not in st.session_state:
            st.session_state.vector_store = None
            st.session_state.chunks = []
            st.session_state.chunk_embeddings = None
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from a PDF file"""
        try:
            text = ""
            with pdfplumber.open(io.BytesIO(pdf_file.read())) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        return chunks
    
    def create_embeddings(self, chunks: List[str]) -> np.ndarray:
        """Create embeddings for text chunks"""
        embeddings = self.embedding_model.encode(chunks, show_progress_bar=False)
        return np.array(embeddings).astype('float32')
    
    def build_vector_store(self, chunks: List[str], embeddings: np.ndarray):
        """Build FAISS vector store"""
        if len(chunks) == 0:
            return
        
        # Create FAISS index
        index = faiss.IndexFlatL2(self.dimension)
        index.add(embeddings)
        
        st.session_state.vector_store = index
        st.session_state.chunks = chunks
        st.session_state.chunk_embeddings = embeddings
    
    def process_pdfs(self, uploaded_files: List) -> int:
        """
        Process multiple PDF files: extract, chunk, embed, and store
        Returns number of chunks created
        """
        all_chunks = []
        
        for pdf_file in uploaded_files:
            try:
                # Extract text
                text = self.extract_text_from_pdf(pdf_file)
                
                # Chunk text
                chunks = self.chunk_text(text)
                all_chunks.extend(chunks)
                
            except Exception as e:
                st.error(f"❌ Error processing {pdf_file.name}: {str(e)}")
                continue
        
        if len(all_chunks) == 0:
            raise Exception("No text could be extracted from the PDFs")
        
        # Create embeddings
        with st.spinner("Creating embeddings..."):
            embeddings = self.create_embeddings(all_chunks)
        
        # Build vector store
        self.build_vector_store(all_chunks, embeddings)
        
        return len(all_chunks)
    
    def retrieve_relevant_chunks(self, query: str, top_k: int = TOP_K_CHUNKS) -> List[str]:
        """
        Retrieve top-k most relevant chunks for a query
        Returns list of chunk texts
        """
        if st.session_state.vector_store is None or len(st.session_state.chunks) == 0:
            return []
        
        try:
            # Create query embedding
            query_embedding = self.embedding_model.encode([query])
            query_vector = np.array(query_embedding).astype('float32')
            
            # Search in vector store
            k = min(top_k, len(st.session_state.chunks))
            distances, indices = st.session_state.vector_store.search(query_vector, k)
            
            # Retrieve chunks
            relevant_chunks = [st.session_state.chunks[i] for i in indices[0]]
            return relevant_chunks
        except Exception as e:
            st.error(f"Error retrieving chunks: {str(e)}")
            return []
    
    def get_context_for_query(self, query: str) -> str:
        """
        Get relevant context chunks for a query
        Returns formatted context string
        """
        chunks = self.retrieve_relevant_chunks(query)
        if not chunks:
            return "No relevant information found in the uploaded documents."
        
        context = "\n\n".join([f"[Context {i+1}]: {chunk}" for i, chunk in enumerate(chunks)])
        return context

