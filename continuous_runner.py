#!/usr/bin/env python3
"""
Continuous Runner for InPlay Football Scraper
Alternative to server.js - runs the scraper continuously with no delays
"""

import time
import subprocess
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('continuous_runner.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_scraper_continuously():
    """Run the scraper continuously with no delays between runs"""
    run_count = 0
    
    logger.info("🚀 Starting InPlay Football Scraper - Continuous Mode")
    logger.info("⚡ Mode: Instant restart after completion")
    logger.info("🔄 Press Ctrl+C to stop")
    
    while True:
        run_count += 1
        start_time = datetime.now()
        
        try:
            logger.info(f"🎯 Starting scraper run #{run_count} at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Run the scraper with real-time output
            process = subprocess.Popen(
                ['python3', 'inplay_football_scraper.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Stream output in real-time
            stdout_lines = []
            stderr_lines = []
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(f"📊 {output.strip()}")
                    stdout_lines.append(output)
            
            # Get any remaining output
            remaining_stdout, remaining_stderr = process.communicate()
            if remaining_stdout:
                stdout_lines.append(remaining_stdout)
            if remaining_stderr:
                stderr_lines.append(remaining_stderr)
            
            # Create result object
            class Result:
                def __init__(self, returncode, stdout, stderr):
                    self.returncode = returncode
                    self.stdout = ''.join(stdout)
                    self.stderr = ''.join(stderr)
            
            result = Result(process.returncode, stdout_lines, stderr_lines)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if result.returncode == 0:
                logger.info(f"✅ Run #{run_count} completed successfully in {duration:.1f} seconds")
                # Log last few lines of output for monitoring
                if result.stdout:
                    last_lines = result.stdout.strip().split('\n')[-3:]
                    for line in last_lines:
                        if line.strip():
                            logger.info(f"📊 {line.strip()}")
            else:
                logger.error(f"❌ Run #{run_count} failed with code {result.returncode} after {duration:.1f} seconds")
                if result.stderr:
                    logger.error(f"Error: {result.stderr.strip()}")
                
                # Wait 30 seconds on error before retrying
                logger.info("⏳ Waiting 30 seconds before retry...")
                time.sleep(30)
                continue
            
            # Instant restart (1 second delay to prevent overlap)
            logger.info("🔄 Restarting immediately...")
            time.sleep(1)
            
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ Run #{run_count} timed out after 10 minutes")
            time.sleep(30)
            continue
            
        except KeyboardInterrupt:
            logger.info("🛑 Received interrupt signal - stopping continuous runner")
            break
            
        except Exception as e:
            logger.error(f"❌ Unexpected error in run #{run_count}: {e}")
            time.sleep(30)
            continue

if __name__ == "__main__":
    try:
        run_scraper_continuously()
    except KeyboardInterrupt:
        logger.info("✅ Continuous runner stopped")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
