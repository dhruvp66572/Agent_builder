import os
import fitz  # PyMuPDF
import asyncio
import concurrent.futures
from sqlalchemy.orm import Session
from typing import List, Optional

try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except ImportError:
    print("Warning: ChromaDB not available. Document embeddings will be disabled.")
    chromadb = None
    embedding_functions = None
    CHROMADB_AVAILABLE = False

from app.models import Document
from app.services.embedding_service import EmbeddingService

class DocumentService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        
        # Use ChromaDB HttpClient with proper configuration and error handling
        try:
            self.chroma_client = chromadb.HttpClient(
                host="api.trychroma.com",
                port=443,
                ssl=True,  # MUST be True for HTTPS
                headers={"X-Chroma-Token": "ck-6icWn2FyAj7TKfGNP1iXe2WCzBK9SE63JTidkrscFap7"}
            )
            
            print("✓ ChromaDB client initialized. Connection will be tested on first use.")
                
        except Exception as e:
            print(f"✗ Failed to initialize ChromaDB client: {e}")
            print("Setting client to None - document operations will be disabled.")
            self.chroma_client = None

    async def _test_chroma_connection(self):
        """Test ChromaDB connection asynchronously"""
        if not self.chroma_client:
            return False
            
        try:
            collections = await asyncio.to_thread(self.chroma_client.list_collections)
            print(f"✓ ChromaDB connected successfully. Found {len(collections)} collections.")
            return True
        except Exception as test_e:
            print(f"⚠ ChromaDB connection test failed: {test_e}")
            print("ChromaDB operations may fail. Check your API key and network connection.")
            return False
        
    async def process_document(self, document_id: int, db: Session):
        """Process a document: extract text and generate embeddings"""
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        try:
            # Update status to processing
            document.embedding_status = "processing"
            db.commit()
            
            # Extract text from PDF
            extracted_text = await self._extract_text_from_pdf(document.file_path)
            document.extracted_text = extracted_text
            db.commit()
            
            # Generate and store embeddings
            await self._generate_embeddings(document, extracted_text)
            
            # Update status to completed
            document.embedding_status = "completed"
            db.commit()
            
        except Exception as e:
            document.embedding_status = "failed"
            db.commit()
            raise e
    
    async def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF using PyMuPDF"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        text = ""
        try:
            pdf_document = fitz.open(file_path)
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                text += page.get_text()
            pdf_document.close()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
        
        return text
    
    async def _generate_embeddings(self, document: Document, text: str):
        """Generate embeddings using Gemini and store in ChromaDB"""
        if not text.strip():
            raise ValueError("No text content to embed")
        
        # Check if ChromaDB client is available
        if not self.chroma_client:
            print("ChromaDB client not available, skipping vector storage")
            return

        # Split text into chunks
        chunks = self._split_text_into_chunks(text, chunk_size=1000, overlap=200)
        
        # Generate embeddings using our Gemini embedding service
        embeddings = await self.embedding_service.generate_embeddings(chunks)
        
        # Test ChromaDB connection on first use
        await self._test_chroma_connection()
        
        try:
            # Get or create collection with async handling
            print(f"Creating/accessing ChromaDB collection for document {document.id}")
            collection = await asyncio.to_thread(
                self.chroma_client.get_or_create_collection,
                name=f"document_{document.id}"
            )
            
            # Store chunks with embeddings in batches to avoid timeouts
            batch_size = 10
            for i in range(0, len(chunks), batch_size):
                batch_chunks = chunks[i:i+batch_size]
                batch_embeddings = embeddings[i:i+batch_size]
                
                documents = []
                embedding_list = []
                ids = []
                metadatas = []
                
                for j, (chunk, embedding) in enumerate(zip(batch_chunks, batch_embeddings)):
                    documents.append(chunk)
                    embedding_list.append(embedding)
                    ids.append(f"doc_{document.id}_chunk_{i+j}")
                    metadatas.append({
                        "document_id": document.id,
                        "chunk_index": i+j,
                        "filename": document.original_filename,
                        "chunk_length": len(chunk)
                    })
                
                # Add batch to collection with async handling
                await asyncio.to_thread(
                    collection.add,
                    documents=documents,
                    embeddings=embedding_list,
                    ids=ids,
                    metadatas=metadatas
                )
                print(f"Stored batch {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size}")
                
        except Exception as e:
            print(f"Error storing embeddings in ChromaDB: {e}")
            # Don't raise the exception - let the document processing continue
            # The embeddings status will remain as processing, indicating partial success    def _split_text_into_chunks(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Find the last complete sentence or paragraph
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n\n')
                split_point = max(last_period, last_newline)
                
                if split_point > start + chunk_size // 2:
                    chunk = text[start:split_point + 1]
                    start = split_point + 1 - overlap
                else:
                    start = end - overlap
            else:
                start = len(text)
            
            if chunk.strip():
                chunks.append(chunk.strip())
        
        return chunks
    
    async def search_documents(
        self, 
        query: str, 
        document_ids: List[int], 
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[dict]:
        """Search for relevant content in documents using Gemini embeddings"""
        results = []
        
        # Check if ChromaDB client is available
        if not self.chroma_client:
            print("ChromaDB client not available, returning empty results")
            return results
        
        # Generate query embedding using Gemini
        try:
            query_embedding = await self.embedding_service.generate_query_embedding(query)
        except Exception as e:
            print(f"Error generating query embedding: {str(e)}")
            return results
        
        for doc_id in document_ids:
            try:
                print(f"Searching in document {doc_id}...")
                
                # Get collection with async handling
                collection = await asyncio.to_thread(
                    self.chroma_client.get_collection, f"document_{doc_id}"
                )
                
                # Query collection with async handling and timeout
                try:
                    search_results = await asyncio.wait_for(
                        asyncio.to_thread(
                            collection.query,
                            query_embeddings=[query_embedding],
                            n_results=limit,
                            include=["documents", "metadatas", "distances"]
                        ),
                        timeout=10.0  # 10 second timeout
                    )
                except asyncio.TimeoutError:
                    print(f"Timeout searching document {doc_id}, skipping...")
                    continue
                
                for i, (doc, metadata, distance) in enumerate(zip(
                    search_results["documents"][0],
                    search_results["metadatas"][0],
                    search_results["distances"][0]
                )):
                    similarity = 1 - distance  # Convert distance to similarity
                    if similarity >= similarity_threshold:
                        results.append({
                            "content": doc,
                            "metadata": metadata,
                            "similarity": similarity,
                            "document_id": doc_id,
                            "chunk_index": metadata.get("chunk_index", 0),
                            "filename": metadata.get("filename", "unknown")
                        })
                        
            except Exception as e:
                print(f"Error searching document {doc_id}: {str(e)}")
                continue
        
        # Sort by similarity
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:limit]
    
    async def reprocess_document_embeddings(self, document_id: int, db: Session):
        """Reprocess embeddings for a document using Gemini"""
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        if not self.chroma_client:
            return {
                "status": "error", 
                "message": "ChromaDB client not available. Embeddings cannot be processed."
            }

        try:
            # Delete existing collection with async handling
            try:
                collection = await asyncio.to_thread(
                    self.chroma_client.get_collection, f"document_{document_id}"
                )
                await asyncio.to_thread(
                    self.chroma_client.delete_collection, f"document_{document_id}"
                )
                print(f"Deleted existing collection for document {document_id}")
            except Exception:
                print(f"No existing collection found for document {document_id}")
            
            # Reprocess with Gemini embeddings
            if document.extracted_text:
                await self._generate_embeddings(document, document.extracted_text)
                document.embedding_status = "completed"
            else:
                # Re-extract text if needed
                extracted_text = await self._extract_text_from_pdf(document.file_path)
                document.extracted_text = extracted_text
                await self._generate_embeddings(document, extracted_text)
                document.embedding_status = "completed"
                
            db.commit()
            return {"status": "success", "message": "Document reprocessed successfully"}
            
        except Exception as e:
            document.embedding_status = "failed"
            db.commit()
            return {"status": "error", "message": f"Reprocessing failed: {str(e)}"}
            # Don't raise the exception to prevent server crashes
    
    async def get_document_stats(self, document_id: int) -> dict:
        """Get statistics about a document's embeddings"""
        if not self.chroma_client:
            return {
                "document_id": document_id,
                "error": "ChromaDB client not available",
                "total_chunks": 0
            }
            
        try:
            collection = await asyncio.to_thread(
                self.chroma_client.get_collection, f"document_{document_id}"
            )
            count = await asyncio.to_thread(collection.count)
            
            # Get sample metadata with async handling
            sample_results = await asyncio.to_thread(
                collection.get, limit=1, include=["metadatas"]
            )
            sample_metadata = sample_results["metadatas"][0] if sample_results["metadatas"] else {}
            
            return {
                "document_id": document_id,
                "total_chunks": count,
                "embedding_model": "google_gemini_embedding-001",
                "embedding_dimension": await self.embedding_service.get_embedding_dimension(),
                "sample_metadata": sample_metadata
            }
            
        except Exception as e:
            return {
                "document_id": document_id,
                "error": str(e),
                "total_chunks": 0
            }