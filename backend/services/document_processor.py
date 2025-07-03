import os
import re
from typing import List, Optional
import PyPDF2
import docx
import tiktoken
from io import BytesIO

class DocumentProcessor:
    """Service for processing and chunking documents"""
    
    def __init__(self):
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.chunk_size = 1000  # tokens
        self.chunk_overlap = 200  # tokens
    
    def process_document(self, file_path: str, filename: str) -> str:
        """Process a document and extract text content"""
        try:
            file_extension = os.path.splitext(filename)[1].lower()
            
            if file_extension == '.pdf':
                return self._process_pdf(file_path)
            elif file_extension == '.txt':
                return self._process_txt(file_path)
            elif file_extension == '.docx':
                return self._process_docx(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
                
        except Exception as e:
            raise Exception(f"Error processing document: {str(e)}")
    
    def _process_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
            
            return self._clean_text(text)
            
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
    
    def _process_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            return self._clean_text(text)
            
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    text = file.read()
                return self._clean_text(text)
            except Exception as e:
                raise Exception(f"Error reading text file: {str(e)}")
        except Exception as e:
            raise Exception(f"Error processing TXT: {str(e)}")
    
    def _process_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return self._clean_text(text)
            
        except Exception as e:
            raise Exception(f"Error processing DOCX: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def create_chunks(self, text: str) -> List[str]:
        """Split text into chunks with overlap"""
        try:
            if not text or not text.strip():
                return []
            
            # Tokenize the text
            tokens = self.encoding.encode(text)
            
            chunks = []
            start = 0
            
            while start < len(tokens):
                # Calculate end position
                end = min(start + self.chunk_size, len(tokens))
                
                # Extract chunk tokens
                chunk_tokens = tokens[start:end]
                
                # Decode back to text
                chunk_text = self.encoding.decode(chunk_tokens)
                
                # Only add non-empty chunks
                if chunk_text.strip():
                    chunks.append(chunk_text.strip())
                
                # Move start position with overlap
                start = end - self.chunk_overlap
                
                # Break if we've reached the end
                if end >= len(tokens):
                    break
            
            return chunks
            
        except Exception as e:
            raise Exception(f"Error creating chunks: {str(e)}")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        try:
            return len(self.encoding.encode(text))
        except Exception:
            return 0
    
    def is_ready(self) -> bool:
        """Check if document processor is ready"""
        return True
