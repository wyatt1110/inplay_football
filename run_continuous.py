#!/usr/bin/env python3
"""
Simple Continuous Runner for InPlay Football Scraper
Runs the scraper directly in a loop with instant restart
"""

import time
import logging
from datetime import datetime
from inplay_football_scraper import InPlayFootballScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('continuous_scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_continuously():
    """Run the scraper continuously with instant restart"""
    run_count = 0
    
    logger.info("🚀 InPlay Football Scraper - Direct Continuous Mode")
    logger.info("⚡ Mode: Instant restart after completion")
    logger.info("🔄 Press Ctrl+C to stop")
    logger.info("=" * 60)
    
    while True:
        run_count += 1
        start_time = datetime.now()
        
        try:
            logger.info(f"🎯 Starting scraper run #{run_count} at {start_time.strftime('%H:%M:%S')}")
            
            # Create and run scraper directly
            scraper = InPlayFootballScraper()
            success = scraper.run_scraper()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if success:
                logger.info(f"✅ Run #{run_count} completed successfully in {duration:.1f} seconds")
            else:
                logger.error(f"❌ Run #{run_count} failed after {duration:.1f} seconds")
                logger.info("⏳ Waiting 30 seconds before retry...")
                time.sleep(30)
                continue
            
            # Instant restart (1 second delay)
            logger.info("🔄 Restarting in 1 second...")
            logger.info("-" * 60)
            time.sleep(1)
            
        except KeyboardInterrupt:
            logger.info("🛑 Received interrupt signal - stopping continuous runner")
            break
            
        except Exception as e:
            logger.error(f"❌ Unexpected error in run #{run_count}: {e}")
            logger.info("⏳ Waiting 30 seconds before retry...")
            time.sleep(30)
            continue

if __name__ == "__main__":
    try:
        run_continuously()
    except KeyboardInterrupt:
        logger.info("✅ Continuous runner stopped")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
