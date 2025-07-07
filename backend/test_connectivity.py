#!/usr/bin/env python3
import requests
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_basic_connectivity():
    """Test basic connectivity to MOSDAC"""
    base_url = "https://www.mosdac.gov.in"
    
    # Create session with headers
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    })
    
    test_urls = [
        f"{base_url}/",
        f"{base_url}/missions",
        f"{base_url}/sitemap.xml"
    ]
    
    for url in test_urls:
        try:
            logger.info(f"Testing: {url}")
            start_time = time.time()
            response = session.get(url, timeout=10)
            elapsed = time.time() - start_time
            
            logger.info(f"✓ Status: {response.status_code}, Size: {len(response.content)}, Time: {elapsed:.2f}s")
            
            # Show first 200 chars to see if we get content
            if response.content:
                preview = response.text[:200].replace('\n', ' ')
                logger.info(f"   Preview: {preview}...")
            
        except Exception as e:
            logger.error(f"✗ Failed: {e}")
        
        time.sleep(1)

if __name__ == "__main__":
    test_basic_connectivity()
