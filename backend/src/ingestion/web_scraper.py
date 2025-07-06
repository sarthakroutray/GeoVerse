# Web scraper for static HTML content from MOSDAC portal
import requests
from bs4 import BeautifulSoup
import time
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from urllib.parse import urljoin, urlparse
import re

from ..utils.config import settings

logger = logging.getLogger(__name__)


class WebScraper:
    """Scraper for extracting text content from static HTML pages"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.scraping_user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def extract_text_content(self, html: str, url: str) -> Dict[str, str]:
        """Extract clean text content from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Extract title
        title = ""
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
        
        # Extract main content
        # Try to find main content area
        main_content = None
        for selector in ['main', '[role="main"]', '.content', '.main-content', '#content']:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if not main_content:
            # Fallback to body
            main_content = soup.find('body')
        
        if not main_content:
            main_content = soup
        
        # Extract text
        text = main_content.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Extract metadata
        meta_description = ""
        meta_keywords = ""
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            meta_description = meta_desc.get('content', '')
        
        meta_kw = soup.find('meta', attrs={'name': 'keywords'})
        if meta_kw:
            meta_keywords = meta_kw.get('content', '')
        
        # Extract headings for structure
        headings = []
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            headings.append({
                'level': heading.name,
                'text': heading.get_text().strip()
            })
        
        return {
            'url': url,
            'title': title,
            'content': text,
            'meta_description': meta_description,
            'meta_keywords': meta_keywords,
            'headings': headings,
            'word_count': len(text.split()),
            'char_count': len(text)
        }
    
    def scrape_page(self, url: str) -> Optional[Dict[str, str]]:
        """Scrape a single page and extract content"""
        try:
            logger.info(f"Scraping: {url}")
            
            response = self.session.get(url, timeout=settings.scraping_timeout)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                logger.warning(f"Skipping non-HTML content: {url}")
                return None
            
            content_data = self.extract_text_content(response.text, url)
            
            # Add scraping metadata
            content_data.update({
                'scraped_at': time.time(),
                'status_code': response.status_code,
                'content_type': content_type,
                'content_hash': hashlib.md5(content_data['content'].encode()).hexdigest()
            })
            
            # Rate limiting
            time.sleep(settings.scraping_delay)
            
            return content_data
            
        except requests.RequestException as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {e}")
            return None
    
    def scrape_urls(self, urls: List[Dict[str, str]], max_pages: int = None) -> List[Dict[str, str]]:
        """Scrape multiple URLs and return content"""
        scraped_content = []
        
        if max_pages:
            urls = urls[:max_pages]
        
        total_urls = len(urls)
        logger.info(f"Starting to scrape {total_urls} URLs")
        
        for i, url_data in enumerate(urls, 1):
            url = url_data.get('url')
            if not url:
                continue
            
            logger.info(f"Progress: {i}/{total_urls} - {url}")
            
            content = self.scrape_page(url)
            if content:
                # Add original URL metadata
                content.update({
                    'priority': url_data.get('priority'),
                    'lastmod': url_data.get('lastmod')
                })
                scraped_content.append(content)
            
            # Progress logging
            if i % 10 == 0:
                logger.info(f"Scraped {len(scraped_content)} pages out of {i} attempted")
        
        logger.info(f"Successfully scraped {len(scraped_content)} pages out of {total_urls}")
        return scraped_content
    
    def save_scraped_content(self, content: List[Dict[str, str]], category: str):
        """Save scraped content to JSON file"""
        output_dir = Path(settings.raw_data_directory) / "scraped_content"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"{category}_content.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(content)} scraped pages to {output_file}")
        return output_file
    
    def load_urls_from_sitemap(self, sitemap_file: str = None) -> Dict[str, List[Dict[str, str]]]:
        """Load URLs from sitemap JSON file"""
        if sitemap_file is None:
            sitemap_file = Path(settings.raw_data_directory) / "sitemap_urls.json"
        
        try:
            with open(sitemap_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Sitemap file not found: {sitemap_file}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse sitemap JSON: {e}")
            return {}


def scrape_category(category: str, max_pages: int = None):
    """Scrape a specific category of URLs"""
    scraper = WebScraper()
    
    # Load URLs from sitemap
    categorized_urls = scraper.load_urls_from_sitemap()
    
    if category not in categorized_urls:
        logger.error(f"Category '{category}' not found in sitemap")
        return
    
    urls = categorized_urls[category]
    logger.info(f"Found {len(urls)} URLs in category '{category}'")
    
    # Scrape the URLs
    content = scraper.scrape_urls(urls, max_pages)
    
    # Save the content
    scraper.save_scraped_content(content, category)
    
    return content


if __name__ == "__main__":
    # Example usage - scrape static pages first
    scrape_category("static_pages", max_pages=50)
