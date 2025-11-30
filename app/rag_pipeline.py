import os
import warnings
import logging

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'

warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', module='tensorflow')
warnings.filterwarnings('ignore', module='tf_keras')

logging.getLogger('tensorflow').setLevel(logging.ERROR)
logging.getLogger('tf_keras').setLevel(logging.ERROR)

import streamlit as st
import pdfplumber
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List, Dict
import io
from app.config import CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_CHUNKS, EMBEDDING_MODEL

class RAGPipeline:
    def __init__(self):
        if "embedding_model" not in st.session_state:
            with st.spinner("Loading embedding model..."):
                st.session_state.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        
        self.embedding_model = st.session_state.embedding_model
        self.dimension = self.embedding_model.get_sentence_embedding_dimension()
        
        if "vector_store" not in st.session_state:
            st.session_state.vector_store = None
            st.session_state.chunks = []
            st.session_state.chunk_embeddings = None
    
    def extract_text_from_pdf(self, pdf_file) -> str:
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
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        return chunks
    
    def create_embeddings(self, chunks: List[str]) -> np.ndarray:
        embeddings = self.embedding_model.encode(chunks, show_progress_bar=False)
        return np.array(embeddings).astype('float32')
    
    def build_vector_store(self, chunks: List[str], embeddings: np.ndarray):
        if len(chunks) == 0:
            return
        
        index = faiss.IndexFlatL2(self.dimension)
        index.add(embeddings)
        
        st.session_state.vector_store = index
        st.session_state.chunks = chunks
        st.session_state.chunk_embeddings = embeddings
    
    def process_pdfs(self, uploaded_files: List) -> int:
        all_chunks = []
        
        for pdf_file in uploaded_files:
            try:
                text = self.extract_text_from_pdf(pdf_file)
                chunks = self.chunk_text(text)
                all_chunks.extend(chunks)
                
            except Exception as e:
                st.error(f"❌ Error processing {pdf_file.name}: {str(e)}")
                continue
        
        if len(all_chunks) == 0:
            raise Exception("No text could be extracted from the PDFs")
        
        with st.spinner("Creating embeddings..."):
            embeddings = self.create_embeddings(all_chunks)
        
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
            query_embedding = self.embedding_model.encode([query])
            query_vector = np.array(query_embedding).astype('float32')
            
            k = min(top_k, len(st.session_state.chunks))
            distances, indices = st.session_state.vector_store.search(query_vector, k)
            
            relevant_chunks = [st.session_state.chunks[i] for i in indices[0]]
            return relevant_chunks
        except Exception as e:
            st.error(f"Error retrieving chunks: {str(e)}")
            return []
    
    def get_context_for_query(self, query: str) -> str:
        chunks = self.retrieve_relevant_chunks(query)
        if not chunks:
            return "No relevant information found in the uploaded documents."
        
        context = "\n\n".join([f"[Context {i+1}]: {chunk}" for i, chunk in enumerate(chunks)])
        return context

