import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from PyPDF2 import PdfReader
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    """PDF processing class for extracting and structuring PDF content"""
    
    def __init__(self):
        self.supported_extensions = ['.pdf']
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        # Normalize line breaks
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)
        
        return text.strip()
    
    def extract_metadata(self, pdf_reader: PdfReader) -> Dict[str, Any]:
        """Extract metadata from PDF"""
        metadata = {
            "num_pages": len(pdf_reader.pages),
            "file_info": {}
        }
        
        # Try to get document info
        if pdf_reader.metadata:
            info = pdf_reader.metadata
            metadata["file_info"] = {
                "title": info.get('/Title', ''),
                "author": info.get('/Author', ''),
                "subject": info.get('/Subject', ''),
                "creator": info.get('/Creator', ''),
                "producer": info.get('/Producer', ''),
                "creation_date": info.get('/CreationDate', ''),
                "modification_date": info.get('/ModDate', '')
            }
        
        return metadata
    
    def extract_text_by_pages(self, pdf_reader: PdfReader) -> List[Dict[str, Any]]:
        """Extract text from each page with page numbers"""
        pages = []
        
        for page_num, page in enumerate(pdf_reader.pages, 1):
            try:
                text = page.extract_text()
                cleaned_text = self.clean_text(text)
                
                if cleaned_text:  # Only add pages with content
                    page_data = {
                        "page_number": page_num,
                        "content": cleaned_text,
                        "word_count": len(cleaned_text.split()),
                        "character_count": len(cleaned_text)
                    }
                    pages.append(page_data)
                    
            except Exception as e:
                logger.warning(f"Error extracting text from page {page_num}: {e}")
                continue
        
        return pages
    
    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Main method to process PDF and return structured JSON"""
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if pdf_path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"Unsupported file format: {pdf_path.suffix}")
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                
                # Extract metadata
                metadata = self.extract_metadata(pdf_reader)
                
                # Extract text by pages
                pages = self.extract_text_by_pages(pdf_reader)
                
                # Create structured output
                structured_data = {
                    "file_name": pdf_path.name,
                    "file_path": str(pdf_path.absolute()),
                    "file_size_bytes": pdf_path.stat().st_size,
                    "processing_timestamp": str(pdf_path.stat().st_mtime),
                    "metadata": metadata,
                    "pages": pages,
                    "total_pages_with_content": len(pages),
                    "total_words": sum(page["word_count"] for page in pages),
                    "total_characters": sum(page["character_count"] for page in pages)
                }
                
                return structured_data
                
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            raise
    
    def save_to_json(self, structured_data: Dict[str, Any], output_path: str) -> None:
        """Save structured data to JSON file"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Structured data saved to: {output_path}")
    
    def process_and_save(self, pdf_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Process PDF and save to JSON file"""
        structured_data = self.process_pdf(pdf_path)
        
        if output_path is None:
            pdf_path_obj = Path(pdf_path)
            output_path = pdf_path_obj.parent / f"{pdf_path_obj.stem}_processed.json"
        
        self.save_to_json(structured_data, output_path)
        return structured_data


def pdf_process(pdf_path):
    """Example usage of PDFProcessor"""
    processor = PDFProcessor()
    
    # Example usage
    try:
        # Replace with your PDF path
        result = processor.process_and_save(pdf_path)
        print(f"Successfully processed {pdf_path}")
        print(f"Total pages: {result['total_pages_with_content']}")
        print(f"Total words: {result['total_words']}")
        
    except Exception as e:
        print(f"Error: {e}")

