"""
RAG (Retrieval Augmented Generation) system for GitScribe.

Handles document indexing, semantic search, and retrieval using ChromaDB
and sentence transformers for embeddings.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
import json
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np

from .config import GitScribeConfig

logger = logging.getLogger(__name__)


class RAGSystem:
    """RAG system for document indexing and semantic search."""
    
    def __init__(self, config: GitScribeConfig):
        """Initialize the RAG system."""
        self.config = config
        self.client: Optional[chromadb.ClientAPI] = None
        self.collection: Optional[chromadb.Collection] = None
        self.embedding_model: Optional[SentenceTransformer] = None
        self.search_history: List[Dict[str, Any]] = []
        self.indexed_documents: List[Dict[str, Any]] = []
    
    async def initialize(self):
        """Initialize the RAG system components."""
        logger.info("Initializing RAG system...")
        
        # Initialize ChromaDB
        await self._initialize_chromadb()
        
        # Initialize embedding model
        await self._initialize_embedding_model()
        
        logger.info("RAG system initialized successfully")
    
    async def _initialize_chromadb(self):
        """Initialize ChromaDB client and collection."""
        try:
            # Create persist directory if it doesn't exist
            persist_dir = Path(self.config.chroma_persist_directory)
            persist_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=str(persist_dir),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(
                    name=self.config.chroma_collection_name
                )
                logger.info(f"Found existing collection: {self.config.chroma_collection_name}")
            except Exception:
                self.collection = self.client.create_collection(
                    name=self.config.chroma_collection_name,
                    metadata={"description": "GitScribe documentation collection"}
                )
                logger.info(f"Created new collection: {self.config.chroma_collection_name}")
                
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            raise
    
    async def _initialize_embedding_model(self):
        """Initialize the sentence transformer model."""
        try:
            logger.info(f"Loading embedding model: {self.config.embedding_model}")
            self.embedding_model = SentenceTransformer(self.config.embedding_model)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise
    
    async def index_documents(self, documents: List[Dict[str, Any]]) -> int:
        """
        Index a list of documents.
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            Number of documents indexed
        """
        if not self.collection or not self.embedding_model:
            raise RuntimeError("RAG system not initialized")
        
        logger.info(f"Indexing {len(documents)} documents...")
        
        indexed_count = 0
        
        for doc in documents:
            try:
                await self._index_single_document(doc)
                indexed_count += 1
                self.indexed_documents.append({
                    'url': doc.get('url', ''),
                    'title': doc.get('title', ''),
                    'indexed_at': time.time(),
                    'source_type': doc.get('source_type', 'unknown')
                })
            except Exception as e:
                logger.warning(f"Error indexing document {doc.get('url', 'unknown')}: {e}")
        
        logger.info(f"Successfully indexed {indexed_count} documents")
        return indexed_count
    
    async def _index_single_document(self, document: Dict[str, Any]):
        """Index a single document."""
        # Extract text content
        content = document.get('content', '')
        if not content:
            return
        
        # Split content into chunks
        chunks = self._split_text_into_chunks(content)
        
        # Generate embeddings for chunks
        embeddings = self.embedding_model.encode(chunks)
        
        # Prepare metadata for each chunk
        base_metadata = {
            'url': document.get('url', ''),
            'title': document.get('title', ''),
            'source_type': document.get('source_type', 'unknown'),
            'file_type': document.get('file_type', ''),
            'scraped_at': document.get('scraped_at', time.time()),
            'indexed_at': time.time()
        }
        
        # Add code blocks if available
        code_blocks = document.get('code_blocks', [])
        if code_blocks:
            base_metadata['has_code'] = True
            # Convert list to string for ChromaDB compatibility
            languages = list(set(
                block.get('language', 'unknown') for block in code_blocks
            ))
            base_metadata['code_languages'] = ','.join(languages)
        
        # Create unique IDs for chunks
        doc_id_base = f"{document.get('url', 'unknown')}_{int(time.time())}"
        
        # Add chunks to collection
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = f"{doc_id_base}_chunk_{i}"
            chunk_metadata = base_metadata.copy()
            chunk_metadata['chunk_index'] = i
            chunk_metadata['chunk_count'] = len(chunks)
            
            # Add to ChromaDB
            self.collection.add(
                ids=[chunk_id],
                embeddings=[embedding.tolist()],
                documents=[chunk],
                metadatas=[chunk_metadata]
            )
        
        # Index code blocks separately if available
        if code_blocks:
            await self._index_code_blocks(code_blocks, document, doc_id_base)
    
    async def _index_code_blocks(self, code_blocks: List[Dict[str, str]], document: Dict[str, Any], doc_id_base: str):
        """Index code blocks separately for better code search."""
        for i, code_block in enumerate(code_blocks):
            code_content = code_block.get('code', '')
            if not code_content:
                continue
            
            # Create embedding for code
            code_embedding = self.embedding_model.encode([code_content])[0]
            
            # Prepare metadata
            code_metadata = {
                'url': document.get('url', ''),
                'title': document.get('title', ''),
                'source_type': document.get('source_type', 'unknown'),
                'content_type': 'code',
                'language': code_block.get('language', 'unknown'),
                'context': code_block.get('context', ''),
                'scraped_at': document.get('scraped_at', time.time()),
                'indexed_at': time.time()
            }
            
            code_id = f"{doc_id_base}_code_{i}"
            
            # Add to ChromaDB
            self.collection.add(
                ids=[code_id],
                embeddings=[code_embedding.tolist()],
                documents=[code_content],
                metadatas=[code_metadata]
            )
    
    def _split_text_into_chunks(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        if not text:
            return []
        
        # Simple sentence-based chunking
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Add sentence to current chunk
            test_chunk = current_chunk + ". " + sentence if current_chunk else sentence
            
            if len(test_chunk) <= self.config.chunk_size:
                current_chunk = test_chunk
            else:
                # Current chunk is full, start a new one
                if current_chunk:
                    chunks.append(current_chunk)
                
                # Handle overlap
                if len(chunks) > 0 and self.config.chunk_overlap > 0:
                    # Take last part of previous chunk for overlap
                    prev_chunk = chunks[-1]
                    overlap_words = prev_chunk.split()[-self.config.chunk_overlap:]
                    current_chunk = " ".join(overlap_words) + ". " + sentence
                else:
                    current_chunk = sentence
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    async def search(
        self, 
        query: str, 
        limit: Optional[int] = None, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for documents using semantic search.
        
        Args:
            query: Search query
            limit: Maximum number of results
            filters: Filter criteria
            
        Returns:
            List of search results
        """
        if not self.collection or not self.embedding_model:
            raise RuntimeError("RAG system not initialized")
        
        limit = limit or self.config.max_results
        
        logger.info(f"Searching for: {query}")
        
        # Record search in history
        search_record = {
            'query': query,
            'timestamp': time.time(),
            'filters': filters or {}
        }
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])[0]
            
            # Build where clause for filters
            where_clause = self._build_where_clause(filters)
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=limit,
                where=where_clause if where_clause else None
            )
            
            # Process results
            formatted_results = []
            if results['documents'][0]:  # Check if we have results
                for i in range(len(results['documents'][0])):
                    result = {
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i],
                        'relevance_score': max(0, 1 - results['distances'][0][i])  # Ensure non-negative relevance
                    }
                    
                    # Always include results for now (disable threshold filtering)
                    formatted_results.append(result)
            
            # Update search history
            search_record['results_found'] = len(formatted_results)
            search_record['top_result_score'] = formatted_results[0]['relevance_score'] if formatted_results else 0
            self.search_history.append(search_record)
            
            # Keep only recent search history
            if len(self.search_history) > 100:
                self.search_history = self.search_history[-100:]
            
            logger.info(f"Found {len(formatted_results)} relevant results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
            search_record['error'] = str(e)
            self.search_history.append(search_record)
            return []
    
    def _build_where_clause(self, filters: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Build ChromaDB where clause from filters."""
        if not filters:
            return None
        
        where_clause = {}
        
        # Handle common filters
        if 'language' in filters:
            where_clause['language'] = filters['language']
        
        if 'framework' in filters:
            # This would need to be handled with contains or similar
            pass
        
        if 'source' in filters:
            where_clause['url'] = {"$contains": filters['source']}
        
        if 'content_type' in filters:
            where_clause['content_type'] = filters['content_type']
        
        if 'file_type' in filters:
            where_clause['file_type'] = filters['file_type']
        
        return where_clause if where_clause else None
    
    async def get_indexed_documents(self) -> List[Dict[str, Any]]:
        """Get list of indexed documents."""
        return self.indexed_documents.copy()
    
    async def get_search_history(self) -> List[Dict[str, Any]]:
        """Get search history."""
        return self.search_history.copy()
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        if not self.collection:
            return {}
        
        try:
            count = self.collection.count()
            return {
                'total_documents': count,
                'indexed_documents': len(self.indexed_documents),
                'search_queries': len(self.search_history),
                'collection_name': self.config.chroma_collection_name
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}
    
    async def clear_collection(self):
        """Clear all documents from the collection."""
        if not self.collection:
            return
        
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(self.config.chroma_collection_name)
            self.collection = self.client.create_collection(
                name=self.config.chroma_collection_name,
                metadata={"description": "GitScribe documentation collection"}
            )
            
            # Clear tracking lists
            self.indexed_documents.clear()
            self.search_history.clear()
            
            logger.info("Collection cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up RAG system...")
        
        # Save search history if needed
        if self.search_history:
            try:
                history_file = Path(self.config.chroma_persist_directory) / "search_history.json"
                with open(history_file, 'w') as f:
                    json.dump(self.search_history, f, indent=2)
                logger.info(f"Search history saved to {history_file}")
            except Exception as e:
                logger.warning(f"Could not save search history: {e}")
        
        # ChromaDB client cleanup is automatic
        logger.info("RAG system cleanup completed")
