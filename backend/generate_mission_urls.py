#!/usr/bin/env python3
"""
Quick Mission URL Generator
Systematically generates all mission-related URLs based on discovered patterns.
"""

import logging
from typing import List, Set
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MissionURLGenerator:
    def __init__(self):
        self.base_url = "https://www.mosdac.gov.in"
        
    def get_all_mission_urls(self) -> Set[str]:
        """Generate all possible mission URLs based on confirmed patterns"""
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
        
        return urls

def main():
    """Generate comprehensive mission URL list"""
    logger.info("🚀 Generating comprehensive mission URL list...")
    
    generator = MissionURLGenerator()
    urls = generator.get_all_mission_urls()
    
    # Save to file
    url_list = sorted(list(urls))
    
    result = {
        "total_urls": len(url_list),
        "generation_method": "systematic_pattern_based",
        "mission_families": [
            "INSAT (insat-3a, insat-3d, insat-3dr, insat-3ds)",
            "Kalpana (kalpana-1)", 
            "Oceansat (oceansat-2, oceansat-3)",
            "ScatSat (scatsat-1)",
            "Climate (megha-tropiques, saral-altika)",
            "Mars & RISAT (mars, risat-1)",
            "Internal catalogs and special pages"
        ],
        "sub_page_patterns": [
            "Base mission page",
            "-introduction (mission overview)",
            "-objectives (mission goals)",
            "-payloads (instruments)",
            "-spacecraft (satellite details)",
            "-references (documentation)",
            "-mission (mission details)",
            "-products (data products)"
        ],
        "urls": url_list
    }
    
    with open('comprehensive_mission_urls.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    logger.info(f"✅ Generated {len(url_list)} comprehensive mission URLs")
    logger.info(f"📁 Saved to: comprehensive_mission_urls.json")
    
    # Show sample URLs by category
    insat_urls = [url for url in url_list if 'insat' in url.lower()]
    ocean_urls = [url for url in url_list if any(x in url.lower() for x in ['oceansat', 'scatsat'])]
    climate_urls = [url for url in url_list if any(x in url.lower() for x in ['megha', 'saral'])]
    
    logger.info(f"\n📊 URL breakdown:")
    logger.info(f"  🛰️  INSAT family: {len(insat_urls)} URLs")
    logger.info(f"  🌊 Ocean satellites: {len(ocean_urls)} URLs") 
    logger.info(f"  🌍 Climate satellites: {len(climate_urls)} URLs")
    
    return url_list

if __name__ == "__main__":
    main()
