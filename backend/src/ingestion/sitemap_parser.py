# Sitemap parser for MOSDAC portal
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
import logging
from pathlib import Path
import json
import sys
import os

# Add utils to path for absolute imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.config import settings

logger = logging.getLogger(__name__)


class SitemapParser:
    """Parser for extracting URLs from MOSDAC portal sitemap"""
    
    def __init__(self, base_url: str = "https://www.mosdac.gov.in"):
        self.base_url = base_url
        self.sitemap_urls = [
            f"{base_url}/sitemap.xml",
            f"{base_url}/sitemap_index.xml"
        ]
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.scraping_user_agent
        })
    
    def fetch_sitemap(self, sitemap_url: str) -> Optional[str]:
        """Fetch sitemap content from URL"""
        try:
            logger.info(f"Fetching sitemap: {sitemap_url}")
            response = self.session.get(sitemap_url, timeout=settings.scraping_timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch sitemap {sitemap_url}: {e}")
            return None
    
    def parse_sitemap_xml(self, xml_content: str) -> List[Dict[str, str]]:
        """Parse XML sitemap content and extract URLs"""
        urls = []
        try:
            root = ET.fromstring(xml_content)
            
            # Handle sitemap index (contains references to other sitemaps)
            if root.tag.endswith('sitemapindex'):
                for sitemap in root:
                    loc_elem = sitemap.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc_elem is not None:
                        sitemap_url = loc_elem.text
                        # Recursively parse sub-sitemaps
                        sub_content = self.fetch_sitemap(sitemap_url)
                        if sub_content:
                            urls.extend(self.parse_sitemap_xml(sub_content))
            
            # Handle regular sitemap (contains URLs)
            elif root.tag.endswith('urlset'):
                for url in root:
                    url_data = {}
                    
                    loc_elem = url.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc_elem is not None:
                        url_data['url'] = loc_elem.text
                    
                    lastmod_elem = url.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
                    if lastmod_elem is not None:
                        url_data['lastmod'] = lastmod_elem.text
                    
                    priority_elem = url.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}priority')
                    if priority_elem is not None:
                        url_data['priority'] = priority_elem.text
                    
                    if url_data.get('url'):
                        urls.append(url_data)
            
        except ET.ParseError as e:
            logger.error(f"Failed to parse XML content: {e}")
        
        return urls
    
    def categorize_urls(self, urls: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
        """Categorize URLs by content type for targeted scraping"""
        categories = {
            'static_pages': [],
            'data_products': [],
            'documentation': [],
            'apis': [],
            'pdfs': [],
            'other': []
        }
        
        for url_data in urls:
            url = url_data['url']
            parsed_url = urlparse(url)
            path = parsed_url.path.lower()
            
            # Categorize based on URL patterns
            if any(keyword in path for keyword in ['faq', 'about', 'mission', 'policy', 'contact']):
                categories['static_pages'].append(url_data)
            elif any(keyword in path for keyword in ['data', 'product', 'catalog', 'archive']):
                categories['data_products'].append(url_data)
            elif any(keyword in path for keyword in ['doc', 'manual', 'guide', 'tutorial']):
                categories['documentation'].append(url_data)
            elif any(keyword in path for keyword in ['api', 'service', 'wms', 'wfs']):
                categories['apis'].append(url_data)
            elif path.endswith('.pdf'):
                categories['pdfs'].append(url_data)
            else:
                categories['other'].append(url_data)
        
        return categories
    
    def extract_urls(self) -> Dict[str, List[Dict[str, str]]]:
        """Extract and categorize all URLs from sitemaps"""
        all_urls = []
        
        for sitemap_url in self.sitemap_urls:
            content = self.fetch_sitemap(sitemap_url)
            if content:
                urls = self.parse_sitemap_xml(content)
                all_urls.extend(urls)
        
        logger.info(f"Extracted {len(all_urls)} URLs from sitemaps")
        
        # Categorize URLs
        categorized_urls = self.categorize_urls(all_urls)
        
        # Log category counts
        for category, urls in categorized_urls.items():
            logger.info(f"{category}: {len(urls)} URLs")
        
        return categorized_urls
    
    def save_urls(self, categorized_urls: Dict[str, List[Dict[str, str]]], output_file: str = None):
        """Save categorized URLs to JSON file"""
        if output_file is None:
            output_file = Path(settings.raw_data_directory) / "sitemap_urls.json"
        
        # Ensure directory exists
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(categorized_urls, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved categorized URLs to {output_file}")
        return output_file


if __name__ == "__main__":
    # Example usage
    parser = SitemapParser()
    urls = parser.extract_urls()
    parser.save_urls(urls)
