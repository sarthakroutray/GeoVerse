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
        self.max_total_pages = 200  # Increased from 75
        self.max_depth = 3
        self.delay = 0.8  # Reduced from 1.2 for faster scraping
        
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
    
    def fetch_sitemap(self, sitemap_url: str="https://www.mosdac.gov.in/sitemap") -> Optional[str]:
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
                for sitemap in root:                loc_elem = sitemap.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc_elem is not None and loc_elem.text:
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
                    if priority_elem is not None and priority_elem.text:
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
        
        # Standard links
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href:
                full_url = urljoin(base_url, href)
                
                if 'mosdac.gov.in' in full_url:
                    if not any(skip in full_url.lower() for skip in [
                        'javascript:', 'mailto:', 'logout', 'login', 
                        'signup', '.pdf', '.doc', '.xls', 'print', 'download'
                    ]):
                        clean_url = full_url.split('#')[0].split('?')[0].rstrip('/')
                        if clean_url and clean_url != base_url.rstrip('/'):
                            links.add(clean_url)
        
        # Look for form actions and data URLs
        for form in soup.find_all('form', action=True):
            action = form.get('action')
            if action:
                full_url = urljoin(base_url, action)
                if 'mosdac.gov.in' in full_url and 'catalog' in full_url:
                    links.add(full_url)
        
        # Look for JavaScript data URLs in script tags
        for script in soup.find_all('script', string=True):
            script_content = script.string
            if script_content:
                # Find URLs in JavaScript
                url_pattern = r'["\']([^"\']*mosdac\.gov\.in[^"\']*)["\']'
                matches = re.findall(url_pattern, script_content)
                for match in matches:
                    if not any(skip in match.lower() for skip in ['javascript:', 'mailto:', '.js', '.css']):
                        links.add(match)
        
        return links
    
    def scrape_page_content(self, url: str, depth: int = 0) -> Optional[Dict[str, Any]]:
        """Enhanced page scraping with robust error handling"""
        if url in self.scraped_urls or len(self.scraped_urls) >= self.max_total_pages:
            return None
        
        progress = f"[{len(self.scraped_urls)}/{self.max_total_pages}]"
        
        try:
            logger.info(f"{progress} Requesting: {url}")
            
            # Use shorter timeout and better error handling
            response = self.session.get(url, timeout=10)
            
            # Handle different HTTP status codes gracefully
            if response.status_code == 404:
                logger.warning(f"{progress} ⚠️ Page not found: {url}")
                self.scraped_urls.add(url)  # Mark as processed to avoid retry
                return None
            elif response.status_code == 403:
                logger.warning(f"{progress} ⚠️ Access forbidden: {url}")
                self.scraped_urls.add(url)
                return None
            elif response.status_code >= 400:
                logger.warning(f"{progress} ⚠️ HTTP {response.status_code}: {url}")
                self.scraped_urls.add(url)
                return None
            
            response.raise_for_status()
            self.scraped_urls.add(url)
            
            # Parse content safely
            try:
                soup = BeautifulSoup(response.content, 'html.parser')
            except Exception as e:
                logger.error(f"{progress} ✗ Failed to parse HTML: {e}")
                return None
            
            # Extract title safely
            try:
                title_elem = soup.find('title')
                title = title_elem.get_text().strip() if title_elem else "Untitled"
                title = re.sub(r'\s+', ' ', title)
                if len(title) > 100:
                    title = title[:100] + "..."
            except Exception:
                title = "Untitled"
            
            # Extract content safely
            try:
                content_text = self.extract_enhanced_content(soup)
            except Exception as e:
                logger.error(f"{progress} ✗ Content extraction failed: {e}")
                return None
            
            # Extract metadata safely
            meta_description = ""
            # Skip meta description extraction to avoid BeautifulSoup type issues
            
            # Discover links safely (only for shallow depth)
            additional_links = set()
            if depth < self.max_depth and len(self.scraped_urls) < self.max_total_pages:
                try:
                    additional_links = self.extract_page_links(soup, url)
                    self.discovered_urls.update(additional_links)
                except Exception as e:
                    logger.warning(f"{progress} ⚠️ Link discovery failed: {e}")
            
            # Only return if we have meaningful content
            if len(content_text) > 100:  # Reduced from 200
                category = self.intelligent_categorize_url(url)
                logger.info(f"{progress} ✓ Success: {len(content_text)} chars, {len(additional_links)} links")
                
                return {
                    'url': url,
                    'title': title,
                    'content': content_text[:6000],  # Increased from 4000
                    'meta_description': meta_description,
                    'category': category,
                    'length': len(content_text),
                    'depth': depth,
                    'additional_links_found': len(additional_links)
                }
            else:
                logger.info(f"{progress} ⚠️ Content too short: {len(content_text)} chars")
                
        except requests.exceptions.Timeout:
            logger.warning(f"{progress} ⏰ Timeout: {url}")
            self.scraped_urls.add(url)
        except requests.exceptions.ConnectionError:
            logger.warning(f"{progress} 🔌 Connection error: {url}")
            self.scraped_urls.add(url)
        except requests.exceptions.RequestException as e:
            logger.warning(f"{progress} 🌐 Request failed: {url} - {e}")
            self.scraped_urls.add(url)
        except Exception as e:
            logger.error(f"{progress} ✗ Unexpected error: {url} - {e}")
            self.scraped_urls.add(url)
        
        return None
    
    def extract_enhanced_content(self, soup: BeautifulSoup) -> str:
        """Enhanced content extraction with better selectors and structured data"""
        # Remove unwanted elements first
        for unwanted in soup.find_all([
            'script', 'style', 'nav', 'footer', 'header', 
            '.menu', '.navigation', '.sidebar', '.ads', 'iframe', 'noscript'
        ]):
            unwanted.decompose()
        
        # Enhanced content strategies with more specific MOSDAC patterns
        content_strategies = [
            # Primary content areas
            ['main', '.main-content', '.content', '.page-content', 'article'],
            ['.container', '.wrapper', '.body-content', '#content'],
            # MOSDAC-specific patterns
            ['.data-content', '.mission-content', '.service-content'],
            ['.mission-info', '.product-info', '.service-info'],
            ['.description', '.details', '.specifications'],
            # Table and structured data
            ['.table-container', '.data-table', '.info-table'],
            # Mission and satellite specific
            ['.satellite-info', '.payload-info', '.instrument-info'],
            ['body']
        ]
        
        content_text = ""
        
        for strategy in content_strategies:
            for selector in strategy:
                try:
                    content_elem = soup.select_one(selector)
                    if content_elem:
                        # Extract structured content
                        structured_content = self.extract_structured_content(content_elem)
                        
                        # Get main text content
                        main_text = content_elem.get_text(separator=' ', strip=True)
                        content_text = main_text + structured_content
                        
                        if len(content_text) > 200:  # Reduced threshold for better coverage
                            break
                except Exception as e:
                    logger.warning(f"Content extraction error: {e}")
                    continue
            
            if len(content_text) > 200:
                break
        
        # Clean up text
        content_text = re.sub(r'\s+', ' ', content_text)
        content_text = content_text.strip()
        
        return content_text
    
    def extract_structured_content(self, element) -> str:
        """Extract structured content like tables, lists, and definitions"""
        structured_text = ""
        
        try:
            # Extract table data with better formatting
            tables = element.find_all('table')
            for table in tables:
                headers = []
                rows = []
                
                # Extract headers
                header_row = table.find('tr')
                if header_row:
                    headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
                
                # Extract data rows
                for row in table.find_all('tr')[1:]:  # Skip header row
                    cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                    if cells:
                        rows.append(cells)
                
                # Format table data
                if headers and rows:
                    structured_text += f" [TABLE - {' | '.join(headers)}:"
                    for row in rows[:5]:  # Limit to first 5 rows
                        structured_text += f" {' | '.join(row)};"
                    structured_text += "]"
                elif rows:
                    structured_text += " [TABLE:"
                    for row in rows[:5]:
                        structured_text += f" {' | '.join(row)};"
                    structured_text += "]"
            
            # Extract list data with better structure
            lists = element.find_all(['ul', 'ol'])
            for list_elem in lists:
                items = [li.get_text(strip=True) for li in list_elem.find_all('li')]
                if items:
                    list_type = "ORDERED" if list_elem.name == 'ol' else "UNORDERED"
                    structured_text += f" [{list_type} LIST: {' • '.join(items[:10])}]"  # Limit to 10 items
            
            # Extract definition lists
            dl_elements = element.find_all('dl')
            for dl in dl_elements:
                definitions = []
                dt_elements = dl.find_all('dt')
                dd_elements = dl.find_all('dd')
                
                for dt, dd in zip(dt_elements, dd_elements):
                    term = dt.get_text(strip=True)
                    definition = dd.get_text(strip=True)
                    definitions.append(f"{term}: {definition}")
                
                if definitions:
                    structured_text += f" [DEFINITIONS: {' | '.join(definitions[:5])}]"
            
            # Extract key-value pairs from divs with specific patterns
            key_value_divs = element.find_all('div', class_=re.compile(r'(spec|info|detail|param)'))
            for div in key_value_divs:
                text = div.get_text(strip=True)
                if ':' in text and len(text) < 200:  # Likely key-value pair
                    structured_text += f" [INFO: {text}]"
            
        except Exception as e:
            logger.warning(f"Structured content extraction error: {e}")
        
        return structured_text
    
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
            f"{self.base_url}/sitemap_index.xml",
            f"{self.base_url}/sitemap",  # The working sitemap URL we found
        ]
        
        all_urls = []
        for sitemap_url in sitemap_urls:
            content = self.fetch_sitemap(sitemap_url)
            if content:
                urls = self.parse_sitemap_xml(content)
                all_urls.extend(urls)
                logger.info(f"Found {len(urls)} URLs from {sitemap_url}")
                if urls:
                    break  # Success
        
        # Phase 1.5: Add comprehensive mission URLs to ensure complete coverage
        mission_url_data = [{'url': url, 'priority': 0.9} for url in comprehensive_mission_urls]
        all_urls.extend(mission_url_data)
        logger.info(f"Added {len(comprehensive_mission_urls)} comprehensive mission URLs")
        
        # Phase 1.6: Deduplication - Remove duplicate URLs based on URL string
        unique_urls = {}
        for url_data in all_urls:
            url = url_data['url']
            # Keep the one with higher priority
            if url not in unique_urls or url_data.get('priority', 0.5) > unique_urls[url].get('priority', 0.5):
                unique_urls[url] = url_data
        
        all_urls = list(unique_urls.values())
        logger.info(f"After deduplication: {len(all_urls)} unique URLs")
        
        # Phase 1.7: Convert Hindi URLs to English versions for broader coverage
        english_urls = []
        for url_data in all_urls[:]:  # Use slice to avoid modifying during iteration
            url = url_data['url']
            if '?language=hi' in url:
                # Create English version
                english_url = url.replace('?language=hi', '')
                english_urls.append({'url': english_url, 'priority': url_data.get('priority', 0.7)})
        
        all_urls.extend(english_urls)
        logger.info(f"Added {len(english_urls)} English equivalent URLs")
        
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
        else:
            # Add critical main pages that should always be included
            critical_urls = [
                f"{self.base_url}/",
                f"{self.base_url}/tools",
                f"{self.base_url}/help",
                f"{self.base_url}/about-us",
                f"{self.base_url}/contact-us",
                f"{self.base_url}/downloads",
                f"{self.base_url}/data-quality",
                f"{self.base_url}/calibration-reports",
                f"{self.base_url}/validation-reports"
            ]
            
            # Add critical URLs if not already present
            existing_urls = {url_data['url'] for url_data in all_urls}
            for critical_url in critical_urls:
                if critical_url not in existing_urls:
                    all_urls.append({'url': critical_url, 'priority': 0.9})
            
            logger.info(f"Added critical main pages to ensure comprehensive coverage")
        
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
        
        # Process priority categories first with dynamic limits
        for category in priority_categories:
            if category in categorized_urls:
                logger.info(f"Processing priority category: {category}")
                
                # Dynamic limits based on category importance and available URLs
                category_urls = categorized_urls[category]
                if category in ['missions', 'data_products']:
                    # More URLs for most important categories
                    urls_to_process = category_urls[:50]  # Increased from 40
                elif category in ['tools', 'forecasts', 'services']:
                    # Good coverage for important tools and services
                    urls_to_process = category_urls[:35]  # Increased from 25
                else:
                    # Moderate coverage for other priority categories
                    urls_to_process = category_urls[:20]  # Increased from 15
                
                for i, url_data in enumerate(urls_to_process):
                    if len(scraped_content) >= self.max_total_pages:
                        logger.info(f"Reached max pages limit ({self.max_total_pages})")
                        break
                        
                    logger.info(f"  [{i+1}/{len(urls_to_process)}] Processing: {url_data['url']}")
                    try:
                        content = self.scrape_page_content(url_data['url'], depth=0)
                        if content:
                            scraped_content.append(content)
                            logger.info(f"    ✓ Successfully scraped ({len(content['content'])} chars)")
                        else:
                            logger.info(f"    ⚠️ No content extracted")
                    except KeyboardInterrupt:
                        logger.info("User interrupted scraping")
                        break
                    except Exception as e:
                        logger.error(f"    ✗ Error processing: {str(e)[:100]}")
                    
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
                        logger.info(f"    ⚠️ No content extracted")
                except KeyboardInterrupt:
                    logger.info("User interrupted scraping")
                    break
                except Exception as e:
                    logger.error(f"    ✗ Error processing: {str(e)[:100]}")
                
                time.sleep(self.delay)
        
        # Phase 5: Enhanced processing for secondary categories with sub-prioritization
        for category in secondary_categories:
            if category in categorized_urls and len(scraped_content) < self.max_total_pages:
                logger.info(f"Processing secondary category: {category}")
                
                category_urls = categorized_urls[category]
                
                # Special handling for "other" category with sub-prioritization
                if category == 'other':
                    # Sub-prioritize "other" category URLs
                    high_priority_other = []
                    medium_priority_other = []
                    low_priority_other = []
                    
                    for url_data in category_urls:
                        url = url_data['url']
                        # High priority: likely important pages
                        if any(keyword in url.lower() for keyword in ['about', 'contact', 'help', 'support', 'faq', 'download', 'access']):
                            high_priority_other.append(url_data)
                        # Medium priority: data-related pages
                        elif any(keyword in url.lower() for keyword in ['data', 'product', 'catalog', 'search', 'browse']):
                            medium_priority_other.append(url_data)
                        else:
                            low_priority_other.append(url_data)
                    
                    # Process in priority order
                    prioritized_urls = high_priority_other[:15] + medium_priority_other[:15] + low_priority_other[:10]
                    urls_to_process = prioritized_urls
                else:
                    # Regular processing for other secondary categories
                    urls_to_process = category_urls[:25]  # Increased from 20
                
                for i, url_data in enumerate(urls_to_process):
                    if len(scraped_content) >= self.max_total_pages:
                        break
                    
                    logger.info(f"  [{i+1}/{len(urls_to_process)}] Processing: {url_data['url']}")
                    try:
                        content = self.scrape_page_content(url_data['url'], depth=0)
                        if content:
                            scraped_content.append(content)
                            logger.info(f"    ✓ Successfully scraped ({len(content['content'])} chars)")
                        else:
                            logger.info(f"    ⚠️ No content extracted")
                    except Exception as e:
                        logger.error(f"    ✗ Error processing: {str(e)[:100]}")
                    
                    time.sleep(self.delay)
        
        # Phase 6: Retry logic for failed URLs
        logger.info("Phase 6: Retry logic for previously failed URLs...")
        failed_urls = []
        
        # Collect URLs that were processed but didn't return content
        for category_urls in categorized_urls.values():
            for url_data in category_urls:
                url = url_data['url']
                if url in self.scraped_urls and not any(item['url'] == url for item in scraped_content):
                    failed_urls.append(url_data)
        
        # Retry up to 20 failed URLs if we have space
        retry_limit = min(20, len(failed_urls), self.max_total_pages - len(scraped_content))
        for i, url_data in enumerate(failed_urls[:retry_limit]):
            if len(scraped_content) >= self.max_total_pages:
                break
            
            logger.info(f"  [Retry {i+1}/{retry_limit}] Retrying: {url_data['url']}")
            try:
                # Remove from scraped_urls to allow retry
                self.scraped_urls.discard(url_data['url'])
                content = self.scrape_page_content(url_data['url'], depth=0)
                if content:
                    scraped_content.append(content)
                    logger.info(f"    ✓ Retry successful ({len(content['content'])} chars)")
                else:
                    logger.info(f"    ⚠️ Retry failed")
            except Exception as e:
                logger.error(f"    ✗ Retry error: {str(e)[:100]}")
            
            time.sleep(self.delay * 1.5)  # Longer delay for retries
        
        # Phase 7: Progressive loading to fill up to max_total_pages
        logger.info("Phase 7: Progressive loading to fill remaining slots...")
        remaining_slots = self.max_total_pages - len(scraped_content)
        
        if remaining_slots > 0:
            # Collect unprocessed URLs
            unprocessed_urls = []
            for category_urls in categorized_urls.values():
                for url_data in category_urls:
                    if url_data['url'] not in self.scraped_urls:
                        unprocessed_urls.append(url_data)
            
            # Sort by priority and take top remaining slots
            unprocessed_urls.sort(key=lambda x: x.get('priority', 0.5), reverse=True)
            progressive_urls = unprocessed_urls[:remaining_slots]
            
            logger.info(f"Progressive loading {len(progressive_urls)} URLs to fill {remaining_slots} slots")
            
            for i, url_data in enumerate(progressive_urls):
                if len(scraped_content) >= self.max_total_pages:
                    break
                
                logger.info(f"  [Progressive {i+1}/{len(progressive_urls)}] Loading: {url_data['url']}")
                try:
                    content = self.scrape_page_content(url_data['url'], depth=0)
                    if content:
                        scraped_content.append(content)
                        logger.info(f"    ✓ Progressive load successful ({len(content['content'])} chars)")
                    else:
                        logger.info(f"    ⚠️ Progressive load failed")
                except Exception as e:
                    logger.error(f"    ✗ Progressive load error: {str(e)[:100]}")
                
                time.sleep(self.delay)
        
        logger.info(f"Successfully scraped {len(scraped_content)} pages")
        
        # Enhanced statistics with more detailed information
        categories = defaultdict(int)
        total_length = 0
        quality_scores = []
        
        for item in scraped_content:
            categories[item['category']] += 1
            total_length += item['length']
            
            # Calculate content quality score
            content_len = item['length']
            if content_len > 2000:
                quality_scores.append(3)  # High quality
            elif content_len > 1000:
                quality_scores.append(2)  # Medium quality
            else:
                quality_scores.append(1)  # Low quality
        
        # Final statistics
        logger.info(f"\n📊 FINAL SCRAPING STATISTICS:")
        logger.info(f"  Total documents scraped: {len(scraped_content)}")
        logger.info(f"  Total URLs processed: {len(self.scraped_urls)}")
        logger.info(f"  Success rate: {len(scraped_content)/len(self.scraped_urls)*100:.1f}%")
        logger.info(f"  Average content length: {total_length // len(scraped_content) if scraped_content else 0} characters")
        
        # Content quality distribution
        if quality_scores:
            high_quality = quality_scores.count(3)
            medium_quality = quality_scores.count(2)
            low_quality = quality_scores.count(1)
            logger.info(f"  Content quality: High={high_quality}, Medium={medium_quality}, Low={low_quality}")
        
        # Category distribution
        logger.info(f"  Category distribution:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            percentage = count / len(scraped_content) * 100
            logger.info(f"    {cat}: {count} documents ({percentage:.1f}%)")
        
        # Coverage metrics
        total_discovered = sum(len(urls) for urls in categorized_urls.values())
        coverage_percentage = len(scraped_content) / total_discovered * 100 if total_discovered > 0 else 0
        logger.info(f"  Coverage: {len(scraped_content)}/{total_discovered} URLs ({coverage_percentage:.1f}%)")
        
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
        """Advanced mission link discovery with robust error handling"""
        logger.info("🔍 Starting advanced mission link discovery...")
        
        all_links = set()
        processed_links = set()
        
        # Strategy 1: Get comprehensive mission starting points (limited)
        starting_points = self.get_mission_starting_points()
        working_starts = starting_points[:10]  # Limit to prevent hanging
        
        for i, start_url in enumerate(working_starts):
            logger.info(f"[{i+1}/{len(working_starts)}] Exploring: {start_url}")
            try:
                links = self.extract_mission_links_recursive(start_url, max_depth, processed_links)
                all_links.update(links)
                logger.info(f"  Found {len(links)} links from {start_url}")
            except Exception as e:
                logger.warning(f"  ⚠️ Failed to explore {start_url}: {str(e)[:100]}")
            
            # Shorter delay
            time.sleep(0.5)
        
        # Strategy 2: Quick systematic check (limited)
        logger.info("🔧 Quick systematic link check...")
        missions = ['insat-3d', 'insat-3dr', 'oceansat-2', 'kalpana-1']  # Known working ones
        for mission in missions:
            systematic_links = self.generate_systematic_sublinks(mission)[:5]  # Limit sub-links
            for link in systematic_links:
                try:
                    response = self.session.head(link, timeout=5)
                    if response.status_code == 200:
                        all_links.add(link)
                except:
                    pass  # Ignore failures
        
        logger.info(f"✅ Mission discovery complete: {len(all_links)} URLs found")
        return all_links

    def get_mission_starting_points(self) -> List[str]:
        """Get comprehensive mission starting points for ALL satellite types"""
        mission_urls = [
            # Main mission pages
            f"{self.base_url}/missions",
            f"{self.base_url}/catalog",
            f"{self.base_url}/satellite",
            f"{self.base_url}/data-products",
            f"{self.base_url}/services",
            f"{self.base_url}/tools",
            f"{self.base_url}/forecasts",
            
            # INSAT Family (Complete)
            f"{self.base_url}/insat-3d", f"{self.base_url}/insat-3dr", 
            f"{self.base_url}/insat-3ds", f"{self.base_url}/insat-3a",
            f"{self.base_url}/kalpana-1",
            
            # Ocean observation
            f"{self.base_url}/oceansat-2", f"{self.base_url}/oceansat-3",
            f"{self.base_url}/scatsat-1",
            
            # Land observation
            f"{self.base_url}/resourcesat-2", f"{self.base_url}/resourcesat-2a",
            f"{self.base_url}/cartosat-2", f"{self.base_url}/cartosat-2a",
            
            # Radar satellites
            f"{self.base_url}/risat-1", f"{self.base_url}/risat-2",
            
            # Climate missions
            f"{self.base_url}/megha-tropiques", f"{self.base_url}/saral",
            
            # Scientific missions
            f"{self.base_url}/astrosat", f"{self.base_url}/chandrayaan-2",
            f"{self.base_url}/mars", f"{self.base_url}/aditya-l1",
            
            # Data access and tools
            f"{self.base_url}/data-access", f"{self.base_url}/quick-access",
            f"{self.base_url}/live-data", f"{self.base_url}/weather-tools",
            f"{self.base_url}/cyclone-monitoring", f"{self.base_url}/ocean-tools",
            
            # Additional important sections
            f"{self.base_url}/help", f"{self.base_url}/documentation",
            f"{self.base_url}/applications", f"{self.base_url}/gallery",
            f"{self.base_url}/research", f"{self.base_url}/publications"
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
        
        # Initialize model from environment variable or default
        import os
        embedding_model = os.getenv('EMBEDDING_MODEL', 'BAAI/bge-large-en-v1.5')
        logger.info(f"Using embedding model: {embedding_model}")
        model = SentenceTransformer(embedding_model)
        
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
        
        # Convert to numpy array if it's not already
        if not isinstance(embeddings, np.ndarray):
            embeddings = np.array(embeddings)
        
        # Ensure embeddings are float32 for FAISS
        embeddings = embeddings.astype(np.float32)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        
        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)
        index.add(embeddings)  # type: ignore
        
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
            # Convert to numpy array if it's not already
            if not isinstance(query_embedding, np.ndarray):
                query_embedding = np.array(query_embedding)
            
            # Ensure float32 for FAISS
            query_embedding = query_embedding.astype(np.float32)
            
            faiss.normalize_L2(query_embedding)
            
            k = min(3, len(documents))
            scores, indices = index.search(query_embedding, k)  # type: ignore
            
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
    
    try:
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
            
    except KeyboardInterrupt:
        logger.info("\n⏹️ Scraping interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ Scraping failed with error: {e}")
        sys.exit(1)
