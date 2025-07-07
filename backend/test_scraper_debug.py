#!/usr/bin/env python3
import sys
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from scraper import UltraComprehensiveMOSDACParser

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scraper_debug.log')
    ]
)
logger = logging.getLogger(__name__)

def test_limited_scraping():
    """Test scraping with very limited parameters to isolate hanging issues"""
    logger.info("🔍 Starting limited scraping test...")
    
    # Create parser with very conservative settings
    parser = UltraComprehensiveMOSDACParser()
    parser.max_total_pages = 5  # Very limited
    parser.delay = 1  # Faster delay
    
    try:
        logger.info("Testing sitemap discovery...")
        
        # Test just the sitemap parsing first
        sitemaps = [
            f"{parser.base_url}/sitemap.xml",
            f"{parser.base_url}/robots.txt"
        ]
        
        for sitemap_url in sitemaps:
            try:
                logger.info(f"Testing sitemap: {sitemap_url}")
                response = parser.session.get(sitemap_url, timeout=10)
                logger.info(f"Response status: {response.status_code}")
                logger.info(f"Content length: {len(response.content)}")
                break
            except Exception as e:
                logger.error(f"Sitemap failed: {e}")
        
        logger.info("Testing individual page scraping...")
        
        # Test scraping just a few key pages
        test_urls = [
            f"{parser.base_url}/",
            f"{parser.base_url}/missions",
            f"{parser.base_url}/insat-3d"
        ]
        
        scraped_content = []
        for i, url in enumerate(test_urls):
            logger.info(f"Testing URL {i+1}/{len(test_urls)}: {url}")
            try:
                content = parser.scrape_page_content(url, depth=0)
                if content:
                    scraped_content.append(content)
                    logger.info(f"✓ Successfully scraped: {len(content['content'])} chars")
                else:
                    logger.info("✗ No content extracted")
            except Exception as e:
                logger.error(f"✗ Error: {e}")
        
        logger.info(f"Test completed. Scraped {len(scraped_content)} pages successfully.")
        return scraped_content
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        return []

if __name__ == "__main__":
    result = test_limited_scraping()
    print(f"\nTest completed. Scraped {len(result)} pages.")
