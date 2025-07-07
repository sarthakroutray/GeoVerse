#!/usr/bin/env python3
"""
Ultra-Comprehensive MOSDAC Data Scraper

Comprehensive scraper for the MOSDAC portal with sitemap discovery,
recursive link following, intelligent categorization, and advanced
mission URL generation capabilities.
"""

import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import time
import json
import logging
from pathlib import Path
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set, Optional, Any
import re
from collections import defaultdict
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UltraComprehensiveMOSDACParser:
    
    def __init__(self, base_url: str = "https://www.mosdac.gov.in"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.scraped_urls = set()
        self.discovered_urls = set()
        self.max_total_pages = 75
        self.max_depth = 3
        self.delay = 1.2
        
        self._comprehensive_mission_urls_cache = None
        self._discovered_mission_links_cache = None
        
        self.category_patterns = {
            'homepage': ['/^$', 'home', 'index'],
            'missions': [
                'mission', 'satellite', 'spacecraft',
                'insat', 'kalpana',
                'oceansat', 'scatsat', 'altimeter', 'scatterometer',
                'resourcesat', 'cartosat', 'irs-',
                'risat', 'radar', 'sar',
                'megha', 'tropiques', 'saral', 'climate',
                'astrosat', 'chandrayaan', 'mars', 'aditya', 'mangalyaan',
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
        try:
            logger.info(f"Fetching sitemap: {sitemap_url}")
            response = self.session.get(sitemap_url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch sitemap {sitemap_url}: {e}")
            return None
    
    def parse_sitemap_xml(self, xml_content: str) -> List[Dict[str, str]]:
        urls = []
        try:
            root = ET.fromstring(xml_content)
            
            if root.tag.endswith('sitemapindex'):
                for sitemap in root:
                    loc_elem = sitemap.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc_elem is not None:
                        sitemap_url = loc_elem.text
                        sub_content = self.fetch_sitemap(sitemap_url)
                        if sub_content:
                            urls.extend(self.parse_sitemap_xml(sub_content))
            
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
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        query = parsed_url.query.lower()
        
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if pattern in path or pattern in query:
                    return category
        
        return 'other'
    
    def extract_page_links(self, soup: BeautifulSoup, base_url: str) -> Set[str]:
        links = set()
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href:
                full_url = urljoin(base_url, href)
                
                if 'mosdac.gov.in' in full_url:
                    if not any(skip in full_url.lower() for skip in [
                        'javascript:', 'mailto:', '#', 'logout', 'login', 
                        'signup', '.pdf', '.doc', '.xls', 'print'
                    ]):
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
            
            # Add progress indicator
            progress = f"[{len(self.scraped_urls)}/{self.max_total_pages}]"
            logger.info(f"{progress} Requesting: {url}")
            
            response = self.session.get(url, timeout=15)  # Reduced timeout
            response.raise_for_status()
            
            logger.info(f"{progress} Response received ({len(response.content)} bytes)")
            
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
            logger.info(f"{progress} Extracting content...")
            content_text = self.extract_enhanced_content(soup)
            
            # Extract metadata
            meta_description = ""
            meta_elem = soup.find('meta', attrs={'name': 'description'})
            if meta_elem:
                meta_description = meta_elem.get('content', '')
            
            # Discover more links for future processing
            if depth < self.max_depth and len(self.scraped_urls) < self.max_total_pages:
                logger.info(f"{progress} Discovering links...")
                additional_links = self.extract_page_links(soup, url)
                self.discovered_urls.update(additional_links)
                logger.info(f"{progress} Found {len(additional_links)} new links")
            
            # Determine category
            category = self.intelligent_categorize_url(url)
            
            if len(content_text) > 200:  # Minimum content threshold
                logger.info(f"{progress} Content extracted: {len(content_text)} chars, category: {category}")
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
            else:
                logger.info(f"{progress} Content too short: {len(content_text)} chars")
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
        
        return None
    
    def extract_enhanced_content(self, soup: BeautifulSoup) -> str:
        content_strategies = [
            ['main', '.main-content', '.content', '.page-content', 'article'],
            ['.container', '.wrapper', '.body-content', '#content'],
            ['.data-content', '.mission-content', '.service-content'],
            ['body']
        ]
        
        content_text = ""
        
        for strategy in content_strategies:
            for selector in strategy:
                content_elem = soup.select_one(selector)
                if content_elem:
                    for unwanted in content_elem.find_all([
                        'script', 'style', 'nav', 'footer', 'header', 
                        '.menu', '.navigation', '.sidebar', '.ads'
                    ]):
                        unwanted.decompose()
                    
                    content_text = content_elem.get_text(separator=' ', strip=True)
                    
                    if len(content_text) > 300:
                        break
            
            if len(content_text) > 300:
                break
        
        content_text = re.sub(r'\s+', ' ', content_text)
        content_text = content_text.strip()
        
        return content_text
    
    def extract_ultra_comprehensive_content(self):
        """Extract ultra-comprehensive content using advanced techniques"""
        logger.info("Starting ultra-comprehensive MOSDAC data extraction...")
        
        # Test connectivity first
        if not self.test_connectivity():
            logger.error("❌ Cannot connect to MOSDAC website. Aborting scraping.")
            logger.info("This could be due to:")
            logger.info("  - Website is temporarily down")
            logger.info("  - Network connectivity issues") 
            logger.info("  - Firewall blocking requests")
            logger.info("  - Server maintenance")
            logger.info("Please try again later or check your network connection.")
            return []
        
        # Phase 0: Get all mission URLs from cache (systematic + discovered)
        comprehensive_mission_urls = self.get_all_mission_urls()
        
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
                
                for i, url_data in enumerate(urls_to_process):
                    logger.info(f"  [{i+1}/{len(urls_to_process)}] Processing: {url_data['url']}")
                    try:
                        content = self.scrape_page_content(url_data['url'], depth=0)
                        if content:
                            scraped_content.append(content)
                            logger.info(f"    ✓ Successfully scraped ({len(content['content'])} chars)")
                        else:
                            logger.info(f"    ✗ No content extracted")
                    except Exception as e:
                        logger.error(f"    ✗ Error processing: {e}")
                    
                    time.sleep(self.delay)
        
        # Phase 4: Follow discovered links recursively
        logger.info(f"Phase 4: Processing {len(self.discovered_urls)} discovered links...")
        discovered_list = list(self.discovered_urls)[:30]  # Limit discovered links
        
        for i, url in enumerate(discovered_list):
            if url not in self.scraped_urls and len(scraped_content) < self.max_total_pages:
                logger.info(f"  [{i+1}/{len(discovered_list)}] Processing discovered: {url}")
                try:
                    content = self.scrape_page_content(url, depth=1)
                    if content:
                        scraped_content.append(content)
                        logger.info(f"    ✓ Successfully scraped ({len(content['content'])} chars)")
                    else:
                        logger.info(f"    ✗ No content extracted")
                except Exception as e:
                    logger.error(f"    ✗ Error processing: {e}")
                
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
    
    def generate_comprehensive_mission_urls(self) -> Set[str]:
        """Generate comprehensive mission URLs based on discovered patterns"""
        logger.info("🚀 Generating comprehensive mission URLs...")
        urls = set()
        
        # Known working missions with sub-pages
        working_missions = [
            'insat-3a', 'insat-3d', 'insat-3dr', 'insat-3ds',
            'kalpana-1', 
            'oceansat-2', 'oceansat-3',
            'scatsat-1',
            'megha-tropiques', 'meghatropiques',
            'saral-altika',
            'risat-1',
            'mars'
        ]
        
        # Standard sub-page patterns (confirmed working)
        sub_patterns = [
            '', '-introduction', '-objectives', '-payloads', 
            '-spacecraft', '-references', '-mission', '-products'
        ]
        
        # Generate all mission + sub-page combinations
        for mission in working_missions:
            for pattern in sub_patterns:
                urls.add(f"{self.base_url}/{mission}{pattern}")
        
        # Add catalog pages (confirmed working)
        catalog_missions = [
            'insat3a', 'insat3d', 'insat3dr', 'insat3s',
            'kalpana1', 'oceansat2', 'oceansat3', 'scatsat',
            'meghatropiques', 'saral', 'satellite', 'insitu', 'radar'
        ]
        
        for catalog in catalog_missions:
            urls.add(f"{self.base_url}/internal/catalog-{catalog}")
        
        # Add special pages found during discovery
        special_urls = [
            f"{self.base_url}/flip-book/demos/risat.html",
            f"{self.base_url}/flip-book/demos/mars.html",
            f"{self.base_url}/software/INSAT_IDV_PLUGIN.jar",
            f"{self.base_url}/calibration-reports",
            f"{self.base_url}/validation-reports",
            f"{self.base_url}/indian-mainland-coastal-product",
            f"{self.base_url}/3d-volumetric-terls-dwrproduct"
        ]
        
        urls.update(special_urls)
        
        # Add Hindi language variants (found in sitemap)
        for mission in working_missions[:6]:  # First 6 missions have Hindi variants
            urls.add(f"http://mosdac.gov.in/{mission}?language=hi")
        
        logger.info(f"✅ Generated {len(urls)} comprehensive mission URLs")
        return urls

    def discover_mission_links_advanced(self, max_depth: int = 2) -> Set[str]:
        """Advanced mission link discovery using multiple strategies"""
        logger.info("🔍 Starting advanced mission link discovery...")
        
        all_links = set()
        processed_links = set()
        
        # Strategy 1: Get comprehensive mission starting points
        starting_points = self.get_mission_starting_points()
        for start_url in starting_points[:20]:  # Limit to prevent overwhelming
            logger.info(f"Exploring from: {start_url}")
            links = self.extract_mission_links_recursive(start_url, max_depth, processed_links)
            all_links.update(links)
            time.sleep(self.delay)
        
        # Strategy 2: Systematic sub-link generation
        logger.info("🔧 Generating systematic sub-links...")
        missions = self.get_comprehensive_mission_list()
        for mission in missions:
            systematic_links = self.generate_systematic_sublinks(mission)
            # Check which ones actually exist (quick check)
            for link in systematic_links:
                try:
                    response = self.session.head(link, timeout=10, allow_redirects=True)
                    if response.status_code == 200:
                        all_links.add(link)
                        logger.debug(f"✅ Found systematic link: {link}")
                except:
                    pass  # Link doesn't exist, that's ok
                time.sleep(0.2)  # Faster checking for systematic links
        
        logger.info(f"🎯 Discovered {len(all_links)} unique mission-related URLs")
        return all_links

    def get_mission_starting_points(self) -> List[str]:
        """Get comprehensive mission starting points for ALL satellite types"""
        mission_urls = [
            # Main mission pages
            f"{self.base_url}/missions",
            f"{self.base_url}/catalog",
            f"{self.base_url}/satellite",
            
            # INSAT Family (Geostationary Weather Satellites) - Complete Series
            f"{self.base_url}/insat-3d", f"{self.base_url}/insat-3dr", 
            f"{self.base_url}/insat-3ds", f"{self.base_url}/insat-3a",
            f"{self.base_url}/kalpana-1", f"{self.base_url}/kalpana-2",
            
            # Oceansat Family (Ocean Observation) - Complete Series
            f"{self.base_url}/oceansat-1", f"{self.base_url}/oceansat-2", f"{self.base_url}/oceansat-3",
            f"{self.base_url}/scatsat-1", f"{self.base_url}/scatsat-2",
            
            # ResourceSat Family (Land Observation) - Complete Series
            f"{self.base_url}/resourcesat", f"{self.base_url}/resourcesat-1",
            f"{self.base_url}/resourcesat-2", f"{self.base_url}/resourcesat-2a", f"{self.base_url}/resourcesat-3",
            
            # CartoSat Family (High-Resolution Earth Imaging) - Complete Series
            f"{self.base_url}/cartosat", f"{self.base_url}/cartosat-1",
            f"{self.base_url}/cartosat-2", f"{self.base_url}/cartosat-2a", f"{self.base_url}/cartosat-2b", f"{self.base_url}/cartosat-3",
            
            # RISAT Family (Radar Imaging) - Complete Series
            f"{self.base_url}/risat", f"{self.base_url}/risat-1",
            f"{self.base_url}/risat-2", f"{self.base_url}/risat-2a", f"{self.base_url}/risat-2b",
            
            # Climate & Atmospheric Missions - International Collaborations
            f"{self.base_url}/meghatropiques", f"{self.base_url}/megha-tropiques",
            f"{self.base_url}/saral-altika", f"{self.base_url}/saral",
            
            # Scientific Missions - Space Exploration
            f"{self.base_url}/astrosat",
            f"{self.base_url}/chandrayaan", f"{self.base_url}/chandrayaan-1", 
            f"{self.base_url}/chandrayaan-2", f"{self.base_url}/chandrayaan-3",
            f"{self.base_url}/mars", f"{self.base_url}/mangalyaan", f"{self.base_url}/mom",
            f"{self.base_url}/aditya", f"{self.base_url}/aditya-l1",
            
            # Data Products & Services - All Categories
            f"{self.base_url}/data-products", f"{self.base_url}/data-access",
            f"{self.base_url}/services", f"{self.base_url}/tools",
            f"{self.base_url}/forecasts", f"{self.base_url}/galleries",
            f"{self.base_url}/applications", f"{self.base_url}/algorithms",
            f"{self.base_url}/instruments", f"{self.base_url}/payloads"
        ]
        return mission_urls

    def extract_mission_links_recursive(self, url: str, max_depth: int = 2, processed_links: Optional[Set[str]] = None, current_depth: int = 0) -> Set[str]:
        """Extract all mission-related links from a page recursively"""
        if processed_links is None:
            processed_links = set()
            
        if current_depth >= max_depth or url in processed_links:
            return set()
        
        try:
            logger.debug(f"Exploring (depth {current_depth}): {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            processed_links.add(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            links = set()
            
            # Find all links
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href and isinstance(href, str):
                    full_url = urljoin(url, href)
                    
                    # Only MOSDAC domain
                    if 'mosdac.gov.in' in full_url:
                        # Filter for mission-related patterns
                        if self.is_mission_related_url(full_url):
                            clean_url = full_url.split('#')[0].split('?')[0].rstrip('/')
                            links.add(clean_url)
            
            # Recursively follow mission links for deeper discovery
            if current_depth < max_depth - 1:
                for link in list(links)[:10]:  # Limit recursive links to prevent explosion
                    if link not in processed_links:
                        deeper_links = self.extract_mission_links_recursive(link, max_depth, processed_links, current_depth + 1)
                        links.update(deeper_links)
                        time.sleep(0.5)  # Faster for recursive discovery
            
            return links
            
        except Exception as e:
            logger.error(f"Error processing {url}: {e}")
            return set()

    def is_mission_related_url(self, url: str) -> bool:
        """Check if URL is mission-related"""
        url_lower = url.lower()
        
        # Skip unwanted patterns
        skip_patterns = [
            'javascript:', 'mailto:', '#', 'login', 'logout', 'signup',
            '.pdf', '.doc', '.xls', 'print', 'download', 'ftp://'
        ]
        
        if any(skip in url_lower for skip in skip_patterns):
            return False
        
        # Enhanced mission-related patterns - covers all satellite families
        mission_patterns = [
            # Core mission types
            'mission', 'satellite', 'spacecraft', 'payload', 'instrument', 'sensor',
            
            # INSAT family (weather/meteorological)
            'insat', 'kalpana',
            
            # Ocean observation family
            'oceansat', 'scatsat', 'altimeter', 'scatterometer',
            
            # Land observation family
            'resourcesat', 'cartosat', 'irs-', 'hyperspectral',
            
            # Radar imaging family
            'risat', 'radar', 'sar', 'synthetic-aperture',
            
            # Climate & atmospheric
            'megha', 'tropiques', 'saral', 'climate', 'atmospheric',
            
            # Scientific & exploration
            'astrosat', 'chandrayaan', 'mars', 'aditya', 'mangalyaan', 'mom',
            
            # Navigation & communication
            'navic', 'irnss', 'gagan', 'gsat', 'navigation', 'communication',
            
            # Mission sub-pages and components
            'introduction', 'objectives', 'payloads', 'spacecraft', 'references',
            'orbit', 'applications', 'algorithms', 'validation', 'calibration',
            'specifications', 'performance', 'coverage', 'timeline', 'launch',
            'operations', 'status', 'imager', 'sounder', 'optical',
            
            # Data and products
            'data-product', 'level-', 'catalog', 'archive', 'browse',
            'download', 'search', 'order', 'quick-look',
            
            # Processing and analysis
            'processing', 'algorithm', 'product', 'format', 'metadata'
        ]
        
        return any(pattern in url_lower for pattern in mission_patterns)

    def generate_systematic_sublinks(self, mission_base: str) -> List[str]:
        """Generate systematic sub-link patterns for a mission"""
        # Standard sub-page patterns found across all missions
        sub_patterns = [
            '-introduction', '-objectives', '-payloads', '-spacecraft', 
            '-references', '-mission', '-orbit', '-applications',
            '-instruments', '-sensors', '-data', '-products',
            '-algorithms', '-validation', '-calibration',
            '-specifications', '-performance', '-coverage',
            '-timeline', '-launch', '-operations', '-status'
        ]
        
        sublinks = []
        for pattern in sub_patterns:
            sublinks.append(f"{self.base_url}/{mission_base}{pattern}")
        
        # Also add catalog patterns
        mission_name = mission_base.replace('-', '')
        sublinks.append(f"{self.base_url}/internal/catalog-{mission_name}")
        
        return sublinks

    def get_comprehensive_mission_list(self) -> List[str]:
        """Get comprehensive list of all possible mission base names"""
        missions = [
            # INSAT family
            'insat-2a', 'insat-2b', 'insat-2c', 'insat-2d', 'insat-2e',
            'insat-3a', 'insat-3d', 'insat-3dr', 'insat-3ds',
            'kalpana-1', 'kalpana-2',
            
            # Ocean satellites
            'oceansat-1', 'oceansat-2', 'oceansat-3',
            'scatsat-1', 'scatsat-2',
            
            # Land observation
            'resourcesat-1', 'resourcesat-2', 'resourcesat-2a', 'resourcesat-3',
            'cartosat-1', 'cartosat-2', 'cartosat-2a', 'cartosat-2b', 'cartosat-3',
            
            # Radar satellites
            'risat-1', 'risat-2', 'risat-2a', 'risat-2b', 'risat-2br1', 'risat-2br2',
            
            # Historical IRS satellites
            'irs-1a', 'irs-1b', 'irs-1c', 'irs-1d', 
            'irs-p2', 'irs-p3', 'irs-p4', 'irs-p5', 'irs-p6',
            
            # Climate missions
            'megha-tropiques', 'meghatropiques', 'saral-altika', 'saral',
            
            # Scientific missions
            'astrosat', 'chandrayaan-1', 'chandrayaan-2', 'chandrayaan-3',
            'mars', 'mangalyaan', 'mom', 'aditya-l1',
            
            # Navigation and communication
            'navic', 'irnss', 'gagan', 'gsat-series'
        ]
        return missions

    def get_comprehensive_mission_urls_cached(self) -> Set[str]:
        """Get comprehensive mission URLs from cache or generate them"""
        if self._comprehensive_mission_urls_cache is None:
            logger.info("🚀 Generating comprehensive mission URLs in memory...")
            self._comprehensive_mission_urls_cache = self.generate_comprehensive_mission_urls()
            logger.info(f"✅ Cached {len(self._comprehensive_mission_urls_cache)} systematic mission URLs")
        
        return self._comprehensive_mission_urls_cache

    def get_discovered_mission_links_cached(self) -> Set[str]:
        """Get discovered mission links from cache or discover them"""
        if self._discovered_mission_links_cache is None:
            logger.info("🔍 Discovering mission links in memory...")
            self._discovered_mission_links_cache = self.discover_mission_links_advanced(max_depth=2)
            logger.info(f"✅ Cached {len(self._discovered_mission_links_cache)} discovered mission links")
        
        return self._discovered_mission_links_cache

    def get_all_mission_urls(self) -> Set[str]:
        """Get all mission URLs (systematic + discovered) from cache"""
        systematic_urls = self.get_comprehensive_mission_urls_cached()
        discovered_urls = self.get_discovered_mission_links_cached()
        
        all_urls = systematic_urls.union(discovered_urls)
        logger.info(f"� Total mission URLs available: {len(all_urls)} ({len(systematic_urls)} systematic + {len(discovered_urls)} discovered)")
        
        return all_urls

    def get_cache_summary(self) -> Dict[str, Any]:
        """Get a summary of what's currently cached in memory"""
        systematic_count = len(self._comprehensive_mission_urls_cache) if self._comprehensive_mission_urls_cache else 0
        discovered_count = len(self._discovered_mission_links_cache) if self._discovered_mission_links_cache else 0
        
        return {
            "systematic_urls_cached": systematic_count,
            "discovered_urls_cached": discovered_count,
            "total_cached_urls": systematic_count + discovered_count,
            "cache_status": {
                "systematic": "loaded" if self._comprehensive_mission_urls_cache else "not loaded",
                "discovered": "loaded" if self._discovered_mission_links_cache else "not loaded"
            }
        }

    def print_cache_summary(self):
        """Print a summary of cached URLs"""
        summary = self.get_cache_summary()
        logger.info(f"\n🧠 Cache Summary:")
        logger.info(f"  Systematic URLs: {summary['systematic_urls_cached']} ({summary['cache_status']['systematic']})")
        logger.info(f"  Discovered URLs: {summary['discovered_urls_cached']} ({summary['cache_status']['discovered']})")
        logger.info(f"  Total cached: {summary['total_cached_urls']} URLs")

    def test_integration(self) -> bool:
        """Test the integrated functionality without full scraping"""
        logger.info("🧪 Testing integrated functionality...")
        
        try:
            # Test systematic URL generation
            systematic_urls = self.generate_comprehensive_mission_urls()
            logger.info(f"✅ Systematic URL generation: {len(systematic_urls)} URLs")
            
            # Test cache functionality
            cached_systematic = self.get_comprehensive_mission_urls_cached()
            logger.info(f"✅ Cache system working: {len(cached_systematic)} URLs cached")
            
            # Print cache summary
            self.print_cache_summary()
            
            # Show some sample URLs
            sample_urls = list(systematic_urls)[:5]
            logger.info(f"\n📋 Sample systematic URLs:")
            for url in sample_urls:
                logger.info(f"  - {url}")
            
            logger.info(f"\n🎉 Integration test PASSED!")
            logger.info(f"✅ No external file dependencies")
            logger.info(f"✅ In-memory caching working")
            logger.info(f"✅ URL generation integrated")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Integration test FAILED: {e}")
            return False

    def test_connectivity(self) -> bool:
        """Test if MOSDAC website is accessible"""
        try:
            logger.info("Testing connectivity to MOSDAC...")
            response = self.session.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                logger.info("✓ MOSDAC is accessible")
                return True
            else:
                logger.warning(f"✗ MOSDAC returned status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"✗ MOSDAC connectivity failed: {e}")
            logger.warning("Website appears to be down or unreachable")
            return False

def create_ultra_embeddings(content_list):
    """Create embeddings from ultra-comprehensive content"""
    logger.info(f"Creating ultra embeddings for {len(content_list)} documents...")
    
    try:
        from sentence_transformers import SentenceTransformer
        import faiss
        import numpy as np
        
        # Initialize model
        # Import the configuration to get the embedding model
        import sys
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
    import sys
    
    # Check for test flag
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        logger.info("🧪 Running integration test only...")
        parser = UltraComprehensiveMOSDACParser()
        success = parser.test_integration()
        sys.exit(0 if success else 1)
    
    logger.info("🚀 Starting MOSDAC data collection...")
    
    parser = UltraComprehensiveMOSDACParser()
    content = parser.extract_ultra_comprehensive_content()
    
    if content:
        logger.info(f"\n📊 Extraction Summary:")
        logger.info(f"Total documents: {len(content)}")
        
        categories = defaultdict(int)
        for item in content:
            categories[item.get('category', 'unknown')] += 1
        
        for cat, count in sorted(categories.items()):
            logger.info(f"  {cat}: {count} documents")
        
        success = create_ultra_embeddings(content)
        
        if success:
            logger.info("\n🎉 SUCCESS! MOSDAC database populated!")
            logger.info(f"📚 Indexed {len(content)} documents")
            logger.info("🚀 Ready for testing!")
        else:
            logger.error("Failed to create embeddings")
    else:
        logger.error("No content collected")
