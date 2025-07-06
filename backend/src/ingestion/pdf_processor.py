# PDF document processor for extracting text content
import PyMuPDF  # fitz
from pathlib import Path
import json
import hashlib
import logging
from typing import Dict, List, Optional
import requests
from urllib.parse import urlparse
import time

from ..utils.config import settings

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Processor for extracting text content from PDF documents"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.scraping_user_agent
        })
    
    def download_pdf(self, url: str, download_dir: str = None) -> Optional[str]:
        """Download PDF from URL and return local file path"""
        if download_dir is None:
            download_dir = Path(settings.raw_data_directory) / "pdfs"
        
        download_dir = Path(download_dir)
        download_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Generate filename from URL
            parsed_url = urlparse(url)
            filename = Path(parsed_url.path).name
            if not filename.endswith('.pdf'):
                filename = f"{hashlib.md5(url.encode()).hexdigest()}.pdf"
            
            file_path = download_dir / filename
            
            # Check if file already exists
            if file_path.exists():
                logger.info(f"PDF already exists: {file_path}")
                return str(file_path)
            
            logger.info(f"Downloading PDF: {url}")
            response = self.session.get(url, timeout=settings.scraping_timeout)
            response.raise_for_status()
            
            # Verify it's actually a PDF
            if response.headers.get('content-type', '').lower() != 'application/pdf':
                content_start = response.content[:10]
                if not content_start.startswith(b'%PDF'):
                    logger.warning(f"Downloaded file doesn't appear to be a PDF: {url}")
                    return None
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded PDF to: {file_path}")
            time.sleep(settings.scraping_delay)
            return str(file_path)
            
        except requests.RequestException as e:
            logger.error(f"Failed to download PDF {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading PDF {url}: {e}")
            return None
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, any]:
        """Extract text content from PDF file"""
        try:
            doc = PyMuPDF.open(pdf_path)
            
            text_content = []
            page_contents = []
            total_text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                
                if page_text.strip():
                    page_contents.append({
                        'page_number': page_num + 1,
                        'text': page_text.strip(),
                        'word_count': len(page_text.split())
                    })
                    total_text += page_text + "\n"
            
            doc.close()
            
            # Extract metadata
            doc = PyMuPDF.open(pdf_path)
            metadata = doc.metadata
            doc.close()
            
            result = {
                'file_path': pdf_path,
                'title': metadata.get('title', '') or Path(pdf_path).stem,
                'author': metadata.get('author', ''),
                'subject': metadata.get('subject', ''),
                'creator': metadata.get('creator', ''),
                'producer': metadata.get('producer', ''),
                'creation_date': metadata.get('creationDate', ''),
                'modification_date': metadata.get('modDate', ''),
                'total_pages': len(page_contents),
                'total_text': total_text.strip(),
                'pages': page_contents,
                'word_count': len(total_text.split()),
                'char_count': len(total_text),
                'content_hash': hashlib.md5(total_text.encode()).hexdigest()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to extract text from PDF {pdf_path}: {e}")
            return None
    
    def process_pdf_url(self, url: str) -> Optional[Dict[str, any]]:
        """Download and process a PDF from URL"""
        # Download the PDF
        pdf_path = self.download_pdf(url)
        if not pdf_path:
            return None
        
        # Extract text content
        content = self.extract_text_from_pdf(pdf_path)
        if content:
            content['source_url'] = url
            content['processed_at'] = time.time()
        
        return content
    
    def process_pdf_urls(self, urls: List[str], max_files: int = None) -> List[Dict[str, any]]:
        """Process multiple PDF URLs"""
        processed_content = []
        
        if max_files:
            urls = urls[:max_files]
        
        total_urls = len(urls)
        logger.info(f"Starting to process {total_urls} PDF URLs")
        
        for i, url in enumerate(urls, 1):
            logger.info(f"Progress: {i}/{total_urls} - {url}")
            
            content = self.process_pdf_url(url)
            if content:
                processed_content.append(content)
            
            # Progress logging
            if i % 5 == 0:
                logger.info(f"Processed {len(processed_content)} PDFs out of {i} attempted")
        
        logger.info(f"Successfully processed {len(processed_content)} PDFs out of {total_urls}")
        return processed_content
    
    def process_local_pdfs(self, pdf_directory: str) -> List[Dict[str, any]]:
        """Process all PDFs in a local directory"""
        pdf_dir = Path(pdf_directory)
        if not pdf_dir.exists():
            logger.error(f"PDF directory does not exist: {pdf_directory}")
            return []
        
        pdf_files = list(pdf_dir.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files in {pdf_directory}")
        
        processed_content = []
        
        for i, pdf_file in enumerate(pdf_files, 1):
            logger.info(f"Processing PDF {i}/{len(pdf_files)}: {pdf_file.name}")
            
            content = self.extract_text_from_pdf(str(pdf_file))
            if content:
                content['processed_at'] = time.time()
                processed_content.append(content)
        
        logger.info(f"Successfully processed {len(processed_content)} local PDFs")
        return processed_content
    
    def save_processed_content(self, content: List[Dict[str, any]], output_file: str = None):
        """Save processed PDF content to JSON file"""
        if output_file is None:
            output_dir = Path(settings.processed_data_directory) / "pdfs"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / "processed_pdfs.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(content)} processed PDFs to {output_file}")
        return output_file


if __name__ == "__main__":
    # Example usage
    processor = PDFProcessor()
    
    # Process PDFs from sitemap
    from .sitemap_parser import SitemapParser
    parser = SitemapParser()
    urls = parser.extract_urls()
    
    pdf_urls = [item['url'] for item in urls.get('pdfs', [])]
    if pdf_urls:
        content = processor.process_pdf_urls(pdf_urls, max_files=10)
        processor.save_processed_content(content)
