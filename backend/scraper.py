#!/usr/bin/env python3
"""
Ultra-Comprehensive MOSDAC Data Scraper

This version goes beyond the current comprehensive scraper by:
1. Using the sitemap to discover ALL available pages
2. Following links within each scraped page recursively
3. Categorizing pages more intelligently
4. Handling multiple languages and dynamic content
5. Creating a much larger, richer knowledge base
"""

import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import time
import json
import logging
import subprocess
from pathlib import Path
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set
import re
from collections import defaultdict
import os
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UltraComprehensiveMOSDACParser:
    """Ultra-comprehensive MOSDAC parser with deep link following and intelligent categorization"""
    
    def __init__(self, base_url: str = "https://www.mosdac.gov.in"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.scraped_urls = set()
        self.discovered_urls = set()
        self.max_total_pages = 75  # Increased limit
        self.max_depth = 3  # Recursive depth for link following
        self.delay = 1.2  # Respectful delay
        
        # Enhanced categorization patterns for comprehensive mission coverage
        self.category_patterns = {
            'homepage': ['/^$', 'home', 'index'],
            'missions': [
                'mission', 'satellite', 'spacecraft',
                # INSAT family
                'insat', 'kalpana',
                # Ocean satellites
                'oceansat', 'scatsat', 'altimeter', 'scatterometer',
                # Land observation
                'resourcesat', 'cartosat', 'irs-',
                # Radar satellites
                'risat', 'radar', 'sar',
                # Climate & atmospheric
                'megha', 'tropiques', 'saral', 'climate',
                # Scientific missions
                'astrosat', 'chandrayaan', 'mars', 'aditya', 'mangalyaan',
                # Mission sub-pages
                'introduction', 'objectives', 'payloads', 'spacecraft', 'references'
            ],
            'data_products': ['product', 'data', 'catalog', 'archive', 'level', 'download', 'browse'],
            'services': ['service', 'access', 'order', 'api', 'distribution'],
            'tools': ['tool', 'live', 'portal', 'visuali', 'interactive'],
            'forecasts': ['forecast', 'nowcast', 'weather', 'cyclone', 'monsoon', 'prediction'],
            'documentation': ['help', 'doc', 'manual', 'guide', 'faq', 'tutorial'],
            'galleries': ['gallery', 'image', 'animation', 'video'],
            'research': ['research', 'publication', 'paper', 'study'],
            'news': ['news', 'event', 'announcement', 'update']
        }
    
    def fetch_sitemap(self, sitemap_url: str) -> str:
        """Fetch sitemap content from URL"""
        try:
            logger.info(f"Fetching sitemap: {sitemap_url}")
            response = self.session.get(sitemap_url, timeout=30)
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
            
            # Handle sitemap index
            if root.tag.endswith('sitemapindex'):
                for sitemap in root:
                    loc_elem = sitemap.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc_elem is not None:
                        sitemap_url = loc_elem.text
                        sub_content = self.fetch_sitemap(sitemap_url)
                        if sub_content:
                            urls.extend(self.parse_sitemap_xml(sub_content))
            
            # Handle regular sitemap
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
                        url_data['priority'] = float(priority_elem.text)
                    
                    if url_data.get('url'):
                        urls.append(url_data)
            
        except ET.ParseError as e:
            logger.error(f"Failed to parse XML content: {e}")
        
        return urls
    
    def intelligent_categorize_url(self, url: str) -> str:
        """Intelligently categorize URLs based on patterns and content"""
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        query = parsed_url.query.lower()
        
        # Check each category pattern
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if pattern in path or pattern in query:
                    return category
        
        return 'other'
    
    def extract_page_links(self, soup: BeautifulSoup, base_url: str) -> Set[str]:
        """Extract all relevant links from a page"""
        links = set()
        
        # Find all links
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href:
                # Convert relative URLs to absolute
                full_url = urljoin(base_url, href)
                
                # Only include MOSDAC domain links
                if 'mosdac.gov.in' in full_url:
                    # Filter out unwanted links
                    if not any(skip in full_url.lower() for skip in [
                        'javascript:', 'mailto:', '#', 'logout', 'login', 
                        'signup', '.pdf', '.doc', '.xls', 'print'
                    ]):
                        # Remove fragments and normalize
                        clean_url = full_url.split('#')[0].split('?')[0].rstrip('/')
                        if clean_url and clean_url != base_url.rstrip('/'):
                            links.add(clean_url)
        
        return links
    
    def scrape_page_content(self, url: str, depth: int = 0) -> Dict[str, any]:
        """Enhanced page scraping with recursive link following"""
        try:
            if url in self.scraped_urls or len(self.scraped_urls) >= self.max_total_pages:
                return None
            
            logger.info(f"Scraping (depth {depth}): {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            self.scraped_urls.add(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title with better handling
            title_elem = soup.find('title')
            title = title_elem.get_text().strip() if title_elem else "Untitled"
            
            # Clean and enhance title
            title = re.sub(r'\s+', ' ', title)
            if len(title) > 100:
                title = title[:100] + "..."
            
            # Enhanced content extraction with multiple strategies
            content_text = self.extract_enhanced_content(soup)
            
            # Extract metadata
            meta_description = ""
            meta_elem = soup.find('meta', attrs={'name': 'description'})
            if meta_elem:
                meta_description = meta_elem.get('content', '')
            
            # Discover more links for future processing
            if depth < self.max_depth and len(self.scraped_urls) < self.max_total_pages:
                additional_links = self.extract_page_links(soup, url)
                self.discovered_urls.update(additional_links)
            
            # Determine category
            category = self.intelligent_categorize_url(url)
            
            if len(content_text) > 200:  # Minimum content threshold
                return {
                    'url': url,
                    'title': title,
                    'content': content_text[:4000],  # Increased content length
                    'meta_description': meta_description,
                    'category': category,
                    'length': len(content_text),
                    'depth': depth,
                    'additional_links_found': len(additional_links) if 'additional_links' in locals() else 0
                }
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
        
        return None
    
    def extract_enhanced_content(self, soup: BeautifulSoup) -> str:
        """Enhanced content extraction with multiple strategies"""
        content_strategies = [
            # Strategy 1: Main content selectors
            ['main', '.main-content', '.content', '.page-content', 'article'],
            # Strategy 2: Container selectors
            ['.container', '.wrapper', '.body-content', '#content'],
            # Strategy 3: Specific MOSDAC selectors (if they exist)
            ['.data-content', '.mission-content', '.service-content'],
            # Strategy 4: Fallback to body
            ['body']
        ]
        
        content_text = ""
        
        for strategy in content_strategies:
            for selector in strategy:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Remove unwanted elements
                    for unwanted in content_elem.find_all([
                        'script', 'style', 'nav', 'footer', 'header', 
                        '.menu', '.navigation', '.sidebar', '.ads'
                    ]):
                        unwanted.decompose()
                    
                    # Extract text with better formatting
                    content_text = content_elem.get_text(separator=' ', strip=True)
                    
                    if len(content_text) > 300:  # Good content found
                        break
            
            if len(content_text) > 300:
                break
        
        # Clean up content
        content_text = re.sub(r'\s+', ' ', content_text)
        content_text = content_text.strip()
        
        return content_text
    
    def extract_ultra_comprehensive_content(self):
        """Extract ultra-comprehensive content using advanced techniques"""
        logger.info("Starting ultra-comprehensive MOSDAC data extraction...")
        
        # Phase 0: Generate/Load comprehensive mission URLs
        self.generate_mission_urls_if_needed()
        comprehensive_mission_urls = self.load_comprehensive_mission_urls()
        
        # Phase 1: Get all URLs from sitemap
        sitemap_urls = [
            f"{self.base_url}/sitemap.xml",
            f"{self.base_url}/sitemap_index.xml"
        ]
        
        all_urls = []
        for sitemap_url in sitemap_urls:
            content = self.fetch_sitemap(sitemap_url)
            if content:
                urls = self.parse_sitemap_xml(content)
                all_urls.extend(urls)
                if urls:
                    break  # Success
        
        # Phase 1.5: Add comprehensive mission URLs to ensure complete coverage
        mission_url_data = [{'url': url, 'priority': 0.9} for url in comprehensive_mission_urls]
        all_urls.extend(mission_url_data)
        logger.info(f"Added {len(comprehensive_mission_urls)} comprehensive mission URLs")
        
        # Add manually discovered important URLs
        if not all_urls:
            logger.warning("No sitemap found, using comprehensive fallback URLs")
            fallback_urls = [
                f"{self.base_url}/",
                f"{self.base_url}/missions",
                f"{self.base_url}/catalog",
                f"{self.base_url}/services",
                f"{self.base_url}/data-access",
                f"{self.base_url}/help",
                f"{self.base_url}/tools",
                f"{self.base_url}/forecasts"
            ]
            all_urls = [{'url': url, 'priority': 1.0} for url in fallback_urls]
        
        logger.info(f"Found {len(all_urls)} URLs from sitemap")
        
        # Phase 2: Prioritize URLs by category and priority
        categorized_urls = defaultdict(list)
        for url_data in all_urls:
            category = self.intelligent_categorize_url(url_data['url'])
            categorized_urls[category].append(url_data)
        
        # Sort by priority within each category
        for category in categorized_urls:
            categorized_urls[category].sort(
                key=lambda x: x.get('priority', 0.5), 
                reverse=True
            )
        
        # Log category distribution
        for category, urls in categorized_urls.items():
            logger.info(f"{category}: {len(urls)} URLs")
        
        # Phase 3: Scrape with intelligent prioritization
        scraped_content = []
        
        # Priority order for categories
        priority_categories = [
            'homepage', 'missions', 'data_products', 'services', 
            'tools', 'forecasts', 'documentation'
        ]
        secondary_categories = [
            'galleries', 'research', 'news', 'other'
        ]
        
        # Process priority categories first
        for category in priority_categories:
            if category in categorized_urls:
                logger.info(f"Processing priority category: {category}")
                urls_to_process = categorized_urls[category][:20]  # Limit per category
                
                for url_data in urls_to_process:
                    content = self.scrape_page_content(url_data['url'], depth=0)
                    if content:
                        scraped_content.append(content)
                    
                    time.sleep(self.delay)
        
        # Phase 4: Follow discovered links recursively
        logger.info(f"Phase 4: Processing {len(self.discovered_urls)} discovered links...")
        discovered_list = list(self.discovered_urls)[:30]  # Limit discovered links
        
        for url in discovered_list:
            if url not in self.scraped_urls and len(scraped_content) < self.max_total_pages:
                content = self.scrape_page_content(url, depth=1)
                if content:
                    scraped_content.append(content)
                
                time.sleep(self.delay)
        
        # Phase 5: Process secondary categories if space allows
        for category in secondary_categories:
            if category in categorized_urls and len(scraped_content) < self.max_total_pages:
                logger.info(f"Processing secondary category: {category}")
                urls_to_process = categorized_urls[category][:10]
                
                for url_data in urls_to_process:
                    if len(scraped_content) >= self.max_total_pages:
                        break
                    
                    content = self.scrape_page_content(url_data['url'], depth=0)
                    if content:
                        scraped_content.append(content)
                    
                    time.sleep(self.delay)
        
        logger.info(f"Successfully scraped {len(scraped_content)} pages")
        
        # Show statistics
        categories = defaultdict(int)
        total_length = 0
        for item in scraped_content:
            categories[item['category']] += 1
            total_length += item['length']
        
        logger.info(f"Category distribution:")
        for cat, count in categories.items():
            logger.info(f"  {cat}: {count} documents")
        
        logger.info(f"Average content length: {total_length // len(scraped_content) if scraped_content else 0} characters")
        
        return scraped_content
    
    def load_comprehensive_mission_urls(self) -> Set[str]:
        """Load comprehensive mission URLs from the generated list"""
        try:
            with open('comprehensive_mission_urls.json', 'r') as f:
                data = json.load(f)
                urls = set(data.get('urls', []))
                logger.info(f"📋 Loaded {len(urls)} comprehensive mission URLs")
                return urls
        except FileNotFoundError:
            logger.warning("📋 Comprehensive mission URLs file not found, using basic discovery")
            return set()
    
    def generate_mission_urls_if_needed(self):
        """Generate comprehensive mission URLs if file doesn't exist"""
        if not os.path.exists('comprehensive_mission_urls.json'):
            logger.info("🚀 Generating comprehensive mission URLs...")
            # Import and run the generator
            import subprocess
            result = subprocess.run([sys.executable, 'generate_mission_urls.py'], 
                                    capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✅ Successfully generated comprehensive mission URLs")
            else:
                logger.warning(f"⚠️ Failed to generate mission URLs: {result.stderr}")
    
def create_ultra_embeddings(content_list):
    """Create embeddings from ultra-comprehensive content"""
    logger.info(f"Creating ultra embeddings for {len(content_list)} documents...")
    
    try:
        from sentence_transformers import SentenceTransformer
        import faiss
        import numpy as np
        
        # Initialize model
        # Import the configuration to get the embedding model
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        from src.utils.config import settings
        
        logger.info(f"Using embedding model: {settings.embedding_model}")
        model = SentenceTransformer(settings.embedding_model)
        
        # Prepare documents with enhanced metadata
        documents = []
        metadatas = []
        
        for item in content_list:
            # Create comprehensive document text
            doc_text = f"{item['title']} {item.get('meta_description', '')} {item['content']}"
            documents.append(doc_text)
            metadatas.append({
                'title': item['title'],
                'url': item['url'],
                'category': item['category'],
                'length': item.get('length', len(item['content'])),
                'depth': item.get('depth', 0),
                'meta_description': item.get('meta_description', '')
            })
        
        # Create embeddings
        embeddings = model.encode(documents)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        
        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)
        index.add(embeddings.astype('float32'))
        
        logger.info(f"Created ultra FAISS index with {index.ntotal} documents")
        
        # Enhanced testing with more diverse queries
        test_queries = [
            "What is MOSDAC and its services?",
            "INSAT satellite weather monitoring capabilities",
            "SCATSAT-1 ocean wind data measurement",
            "Oceansat satellite missions and instruments",
            "How to download satellite data products",
            "Weather forecasting tools and services",
            "Ocean color monitoring applications",
            "Satellite data processing levels and formats",
            "Tropical cyclone monitoring and prediction",
            "MOSDAC data access methods and APIs"
        ]
        
        for query in test_queries:
            logger.info(f"\nTesting: '{query}'")
            
            query_embedding = model.encode([query])
            faiss.normalize_L2(query_embedding)
            
            k = min(3, len(documents))
            scores, indices = index.search(query_embedding.astype('float32'), k)
            
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(metadatas):
                    meta = metadatas[idx]
                    logger.info(f"  {i+1}. {meta['title'][:60]}... (score: {score:.3f}, {meta['category']})")
        
        # Save everything with enhanced metadata
        embeddings_dir = Path("data/embeddings")
        embeddings_dir.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(index, str(embeddings_dir / "mosdac.faiss"))
        
        # Save enhanced metadata
        with open(embeddings_dir / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadatas, f, indent=2, ensure_ascii=False)
        
        # Save original content
        with open(embeddings_dir / "content.json", 'w', encoding='utf-8') as f:
            json.dump(content_list, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Ultra-comprehensive embeddings saved to {embeddings_dir}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating ultra embeddings: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting ULTRA-COMPREHENSIVE MOSDAC data collection...")
    
    # Create ultra parser
    parser = UltraComprehensiveMOSDACParser()
    
    # Extract ultra-comprehensive content
    content = parser.extract_ultra_comprehensive_content()
    
    if content:
        logger.info(f"\n📊 Ultra Extraction Summary:")
        logger.info(f"Total documents: {len(content)}")
        
        # Show category distribution
        categories = defaultdict(int)
        for item in content:
            categories[item.get('category', 'unknown')] += 1
        
        for cat, count in sorted(categories.items()):
            logger.info(f"  {cat}: {count} documents")
        
        # Create ultra embeddings
        success = create_ultra_embeddings(content)
        
        if success:
            logger.info("\n🎉 ULTRA SUCCESS! Comprehensive MOSDAC database populated!")
            logger.info(f"📚 Indexed {len(content)} ultra-detailed documents")
            logger.info("🚀 Ready for advanced testing with enhanced coverage!")
        else:
            logger.error("Failed to create ultra embeddings")
    else:
        logger.error("No content collected")
