#!/usr/bin/env python3
"""
Enhanced Mission Link Scraper
Specifically designed to find and follow all sub-links within mission pages
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from urllib.parse import urljoin, urlparse
from typing import Set, List, Dict
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MissionLinkDiscoverer:
    """Discover all mission-related links by following sub-pages"""
    
    def __init__(self, base_url: str = "https://www.mosdac.gov.in"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.discovered_links = set()
        self.processed_links = set()
        self.delay = 1.0
    
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
            f"{self.base_url}/insat-2a", f"{self.base_url}/insat-2b",
            f"{self.base_url}/insat-2c", f"{self.base_url}/insat-2d", f"{self.base_url}/insat-2e",
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
            f"{self.base_url}/risat-2br1", f"{self.base_url}/risat-2br2",
            
            # IRS Family (Indian Remote Sensing) - Historical Satellites
            f"{self.base_url}/irs", f"{self.base_url}/irs-1a", f"{self.base_url}/irs-1b",
            f"{self.base_url}/irs-1c", f"{self.base_url}/irs-1d",
            f"{self.base_url}/irs-p2", f"{self.base_url}/irs-p3", f"{self.base_url}/irs-p4",
            f"{self.base_url}/irs-p5", f"{self.base_url}/irs-p6",
            
            # Climate & Atmospheric Missions - International Collaborations
            f"{self.base_url}/meghatropiques", f"{self.base_url}/megha-tropiques",
            f"{self.base_url}/saral-altika", f"{self.base_url}/saral",
            f"{self.base_url}/tropiques",
            
            # Scientific Missions - Space Exploration
            f"{self.base_url}/astrosat",
            f"{self.base_url}/chandrayaan", f"{self.base_url}/chandrayaan-1", 
            f"{self.base_url}/chandrayaan-2", f"{self.base_url}/chandrayaan-3",
            f"{self.base_url}/mars", f"{self.base_url}/mangalyaan", f"{self.base_url}/mom",
            f"{self.base_url}/aditya", f"{self.base_url}/aditya-l1",
            
            # Navigation & Communication Satellites
            f"{self.base_url}/navic", f"{self.base_url}/irnss", f"{self.base_url}/gagan",
            f"{self.base_url}/gsat", f"{self.base_url}/inmarsat",
            
            # Hyperspectral & Advanced Technology
            f"{self.base_url}/hypersat", f"{self.base_url}/hyperspectral",
            
            # Data Products & Services - All Categories
            f"{self.base_url}/data-products", f"{self.base_url}/data-access",
            f"{self.base_url}/services", f"{self.base_url}/tools",
            f"{self.base_url}/forecasts", f"{self.base_url}/galleries",
            f"{self.base_url}/applications", f"{self.base_url}/algorithms",
            f"{self.base_url}/instruments", f"{self.base_url}/payloads"
        ]
        return mission_urls
    
    def extract_mission_links(self, url: str, max_depth: int = 2, current_depth: int = 0) -> Set[str]:
        """Extract all mission-related links from a page"""
        if current_depth >= max_depth or url in self.processed_links:
            return set()
        
        try:
            logger.info(f"Exploring (depth {current_depth}): {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            self.processed_links.add(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            links = set()
            
            # Find all links
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href:
                    full_url = urljoin(url, href)
                    
                    # Only MOSDAC domain
                    if 'mosdac.gov.in' in full_url:
                        # Filter for mission-related patterns
                        if self.is_mission_related(full_url):
                            clean_url = full_url.split('#')[0].split('?')[0].rstrip('/')
                            links.add(clean_url)
            
            # Recursively follow mission links for deeper discovery
            if current_depth < max_depth - 1:
                for link in list(links):
                    if link not in self.processed_links:
                        deeper_links = self.extract_mission_links(link, max_depth, current_depth + 1)
                        links.update(deeper_links)
                        time.sleep(self.delay)
            
            return links
            
        except Exception as e:
            logger.error(f"Error processing {url}: {e}")
            return set()
    
    def is_mission_related(self, url: str) -> bool:
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
    
    def discover_all_mission_links(self) -> Set[str]:
        """Discover all mission-related links using multiple strategies"""
        logger.info("🔍 Starting ultra-comprehensive mission link discovery...")
        
        all_links = set()
        
        # Strategy 1: Start from known mission pages and crawl
        starting_points = self.get_mission_starting_points()
        for start_url in starting_points:
            logger.info(f"Exploring from: {start_url}")
            links = self.extract_mission_links(start_url, max_depth=3)
            all_links.update(links)
            time.sleep(self.delay)
        
        # Strategy 2: Systematic sub-link generation for all missions
        logger.info("🔧 Generating systematic sub-links for all missions...")
        missions = self.get_comprehensive_mission_list()
        for mission in missions:
            systematic_links = self.generate_systematic_sublinks(mission)
            # Check which ones actually exist
            for link in systematic_links:
                try:
                    response = self.session.head(link, timeout=10, allow_redirects=True)
                    if response.status_code == 200:
                        all_links.add(link)
                        logger.info(f"✅ Found systematic link: {link}")
                except:
                    pass  # Link doesn't exist, that's ok
                time.sleep(0.2)  # Faster checking for systematic links
        
        # Strategy 3: Try to discover from sitemap
        try:
            sitemap_url = f"{self.base_url}/sitemap.xml"
            response = self.session.get(sitemap_url, timeout=30)
            if response.status_code == 200:
                logger.info("Found sitemap, extracting mission URLs...")
                soup = BeautifulSoup(response.content, 'xml')
                for loc in soup.find_all('loc'):
                    url = loc.get_text()
                    if self.is_mission_related(url):
                        all_links.add(url)
        except:
            logger.info("No sitemap found or accessible")
        
        logger.info(f"🎯 Discovered {len(all_links)} unique mission-related URLs")
        return all_links
    
    def save_discovered_links(self, links: Set[str], filename: str = "discovered_mission_links.json"):
        """Save discovered links for analysis"""
        links_list = sorted(list(links))
        
        # Categorize links
        categorized = {
            'insat': [],
            'oceansat': [],
            'scatsat': [],
            'other_satellites': [],
            'data_products': [],
            'instruments': [],
            'services': [],
            'general': []
        }
        
        for url in links_list:
            url_lower = url.lower()
            if 'insat' in url_lower:
                categorized['insat'].append(url)
            elif 'oceansat' in url_lower:
                categorized['oceansat'].append(url)
            elif 'scatsat' in url_lower:
                categorized['scatsat'].append(url)
            elif any(sat in url_lower for sat in ['kalpana', 'megha', 'saral', 'resourcesat']):
                categorized['other_satellites'].append(url)
            elif any(term in url_lower for term in ['product', 'data', 'level', 'catalog']):
                categorized['data_products'].append(url)
            elif any(term in url_lower for term in ['instrument', 'payload', 'sensor', 'imager']):
                categorized['instruments'].append(url)
            elif any(term in url_lower for term in ['service', 'access', 'api']):
                categorized['services'].append(url)
            else:
                categorized['general'].append(url)
        
        # Save results
        results = {
            'total_links': len(links_list),
            'discovery_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'categorized_links': categorized,
            'all_links': links_list
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Print summary
        logger.info(f"\n📊 Discovery Summary:")
        logger.info(f"Total unique URLs: {len(links_list)}")
        for category, urls in categorized.items():
            if urls:
                logger.info(f"  {category}: {len(urls)} URLs")
        
        logger.info(f"\n🔗 Sample URLs by category:")
        for category, urls in categorized.items():
            if urls:
                logger.info(f"\n{category.upper()}:")
                for url in urls[:3]:  # Show first 3
                    logger.info(f"  - {url}")
                if len(urls) > 3:
                    logger.info(f"  ... and {len(urls) - 3} more")
        
        return results

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

def main():
    """Run mission link discovery"""
    discoverer = MissionLinkDiscoverer()
    
    # Discover all mission links
    links = discoverer.discover_all_mission_links()
    
    # Save results
    results = discoverer.save_discovered_links(links)
    
    logger.info(f"\n✅ Discovery complete!")
    logger.info(f"📁 Results saved to: discovered_mission_links.json")
    logger.info(f"🎯 Found {len(links)} mission-related URLs")
    
    # Compare with current database
    try:
        with open('data/embeddings/content.json', 'r', encoding='utf-8') as f:
            current_data = json.load(f)
        
        current_urls = {item['url'] for item in current_data}
        new_urls = links - current_urls
        
        logger.info(f"\n📈 Comparison with current database:")
        logger.info(f"  Current URLs in database: {len(current_urls)}")
        logger.info(f"  Newly discovered URLs: {len(new_urls)}")
        
        if new_urls:
            logger.info(f"\n🆕 Some newly discovered URLs:")
            for url in list(new_urls)[:10]:
                logger.info(f"  - {url}")
                
    except Exception as e:
        logger.info(f"Could not compare with current database: {e}")

if __name__ == "__main__":
    main()
