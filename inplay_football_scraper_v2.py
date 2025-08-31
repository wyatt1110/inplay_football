#!/usr/bin/env python3
"""
InPlay Football Scraper - Production Grade
Industry-standard web scraping with undetected Chrome and advanced stability
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
import json

# Industry-standard scraping libraries
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    StaleElementReferenceException,
    WebDriverException
)
from selenium_stealth import stealth

# Data processing
import pandas as pd
from supabase import create_client, Client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ProductionInPlayScraper:
    """
    Production-grade InPlay Football scraper using industry best practices:
    - Undetected ChromeDriver for anti-detection
    - Selenium Stealth for fingerprint masking
    - Robust element handling with retry mechanisms
    - Memory-efficient batch processing
    - Enterprise-grade error handling
    """
    
    def __init__(self):
        """Initialize with production configuration"""
        self.driver: Optional[uc.Chrome] = None
        self.supabase: Optional[Client] = None
        self.is_production = os.getenv('RAILWAY_ENVIRONMENT_NAME') is not None
        
        # Credentials
        self.username = "Wyatt1110"
        self.password = "Wiggers10"
        
        # URLs
        self.login_url = "https://inplayfootballtips.co.uk/login"
        self.fulltime_url = "https://inplayfootballtips.co.uk/full-time"
        
        # Supabase configuration
        self.supabase_url = os.getenv('SUPABASE_URL', 'https://gwvnmzflxttdlhrkejmy.supabase.co')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not self.supabase_key:
            logger.error("❌ SUPABASE_SERVICE_KEY environment variable not set")
            sys.exit(1)
        
        # Table columns (exact lowercase names from PostgreSQL)
        self.columns = [
            'timeupdated', 'league', 'hometeam', 'awayteam', 'min', 'score', 'modsup',
            'hdp1', 'hprice', 'aprice', 'homehdp1', 'awayhdp1', 'homehdp2', 'awayhdp2',
            'homehdp3', 'awayhdp3', 'homehdp4', 'awayhdp4', 'homehdp5', 'awayhdp5',
            'homehdp6', 'awayhdp6', 'homehdp7', 'awayhdp7', 'homehdp8', 'awayhdp8',
            'homehdp9', 'awayhdp9', 'homehdp10', 'awayhdp10', 'homehdp11', 'awayhdp11',
            'homehdp12', 'awayhdp12', 'homehdp13', 'awayhdp13', 'homehdp14', 'awayhdp14',
            'homehdp15', 'awayhdp15', 'homehdp16', 'awayhdp16', 'homehdp17', 'awayhdp17',
            'homehdp18', 'awayhdp18', 'homehdp19', 'awayhdp19', 'homehdp20', 'awayhdp20',
            'analysis'
        ]
        
        logger.info(f"🏈 Production InPlay Football Scraper initialized - Production: {self.is_production}")

    def setup_driver(self) -> None:
        """Setup undetected ChromeDriver with production configuration"""
        try:
            logger.info("🔧 Setting up undetected ChromeDriver...")
            
            # Production Chrome options
            options = uc.ChromeOptions()
            
            if self.is_production:
                # Railway production configuration
                options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--disable-web-security")
                options.add_argument("--disable-features=VizDisplayCompositor")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--disable-extensions")
                options.add_argument("--disable-plugins")
                options.add_argument("--disable-images")  # Speed optimization
                options.add_argument("--disable-javascript")  # We don't need JS for table scraping
                
                # Memory optimization for 32GB container
                options.add_argument("--memory-pressure-off")
                options.add_argument("--max_old_space_size=8192")  # Use 8GB of available memory
                
                # Set binary path for Railway
                options.binary_location = "/usr/bin/chromium-browser"
            
            # Initialize undetected ChromeDriver
            self.driver = uc.Chrome(
                options=options,
                version_main=None,  # Auto-detect Chrome version
                driver_executable_path="/usr/bin/chromedriver" if self.is_production else None
            )
            
            # Apply selenium-stealth for anti-detection
            stealth(
                self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Linux",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
            )
            
            # Set production timeouts
            self.driver.implicitly_wait(20)
            self.driver.set_page_load_timeout(180)
            self.driver.set_script_timeout(120)
            
            logger.info("✅ Undetected ChromeDriver setup complete with stealth mode")
            
        except Exception as e:
            logger.error(f"❌ ChromeDriver setup failed: {e}")
            raise

    def setup_supabase(self) -> None:
        """Initialize Supabase client"""
        try:
            logger.info("🔧 Setting up Supabase client...")
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            logger.info("✅ Supabase client initialized")
        except Exception as e:
            logger.error(f"❌ Supabase setup failed: {e}")
            raise

    def robust_element_interaction(self, locator: tuple, action: str = "click", 
                                 text: str = None, max_retries: int = 5) -> Any:
        """
        Industry-standard robust element interaction with retry mechanism
        
        Args:
            locator: Tuple of (By.METHOD, "selector")
            action: "click", "send_keys", "get_text", "get_attribute"
            text: Text to send (for send_keys action)
            max_retries: Maximum retry attempts
            
        Returns:
            Result of the action or None if failed
        """
        wait = WebDriverWait(self.driver, 30)
        
        for attempt in range(max_retries):
            try:
                # Wait for element to be present and interactable
                if action == "click":
                    element = wait.until(EC.element_to_be_clickable(locator))
                    element.click()
                    return True
                    
                elif action == "send_keys":
                    element = wait.until(EC.presence_of_element_located(locator))
                    element.clear()
                    element.send_keys(text)
                    return True
                    
                elif action == "get_text":
                    element = wait.until(EC.presence_of_element_located(locator))
                    return element.text.strip()
                    
                elif action == "get_attribute":
                    element = wait.until(EC.presence_of_element_located(locator))
                    return element.get_attribute(text)  # text parameter is attribute name
                    
                else:
                    raise ValueError(f"Unknown action: {action}")
                    
            except (StaleElementReferenceException, TimeoutException, WebDriverException) as e:
                if attempt < max_retries - 1:
                    logger.warning(f"⚠️ Element interaction failed (attempt {attempt + 1}): {e}")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    logger.error(f"❌ Element interaction failed after {max_retries} attempts: {e}")
                    raise
                    
        return None

    def login(self) -> bool:
        """Login with robust error handling"""
        try:
            logger.info("🔐 Logging into InPlay Football Tips...")
            self.driver.get(self.login_url)
            
            # Wait for page load
            time.sleep(3)
            
            # Enter credentials with robust interaction
            self.robust_element_interaction((By.NAME, "username"), "send_keys", self.username)
            self.robust_element_interaction((By.NAME, "password"), "send_keys", self.password)
            
            # Click login button
            self.robust_element_interaction((By.CSS_SELECTOR, "input[type='submit'], button[type='submit']"), "click")
            
            # Wait for login to complete
            time.sleep(5)
            
            # Verify login success
            current_url = self.driver.current_url
            if "login" not in current_url.lower():
                logger.info("✅ Successfully logged in")
                return True
            else:
                logger.error("❌ Login failed - still on login page")
                return False
                
        except Exception as e:
            logger.error(f"❌ Login failed: {e}")
            return False

    def navigate_to_fulltime_page(self) -> bool:
        """Navigate to full-time page"""
        try:
            logger.info("🏈 Navigating to full-time page...")
            self.driver.get(self.fulltime_url)
            time.sleep(3)
            logger.info("✅ Successfully navigated to full-time page")
            return True
        except Exception as e:
            logger.error(f"❌ Navigation failed: {e}")
            return False

    def click_fulltime_raw_tab(self) -> bool:
        """Click the Full-Time Model Raw tab with robust handling"""
        try:
            logger.info("🎯 Clicking 'Full-Time Model Raw' tab...")
            
            # Multiple selectors to try
            selectors = [
                (By.ID, "two-tab"),
                (By.CSS_SELECTOR, "label[for='two']"),
                (By.XPATH, "//label[contains(text(), 'Full-Time Model Raw')]"),
                (By.CSS_SELECTOR, "label.tab[id='two-tab']")
            ]
            
            for selector in selectors:
                try:
                    success = self.robust_element_interaction(selector, "click")
                    if success:
                        time.sleep(3)  # Wait for tab content to load
                        logger.info("✅ Successfully clicked 'Full-Time Model Raw' tab")
                        return True
                except Exception:
                    continue
            
            logger.error("❌ Failed to click Full-Time Model Raw tab with all selectors")
            return False
            
        except Exception as e:
            logger.error(f"❌ Tab click failed: {e}")
            return False

    def scrape_table_data_robust(self) -> List[Dict[str, Any]]:
        """
        Industry-standard table scraping with robust element handling
        """
        logger.info("📊 Starting robust table data scraping...")
        scraped_data = []
        
        try:
            # Wait for table to be present
            wait = WebDriverWait(self.driver, 60)
            table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#fulltimemodelraw")))
            
            # Wait for table rows to load
            rows_locator = (By.CSS_SELECTOR, "#fulltimemodelraw tbody tr")
            wait.until(lambda driver: len(driver.find_elements(*rows_locator)) > 0)
            
            # Get all rows
            rows = self.driver.find_elements(*rows_locator)
            total_rows = len(rows)
            logger.info(f"📋 Found {total_rows} rows to process")
            
            if total_rows == 0:
                logger.warning("⚠️ No rows found in table")
                return []
            
            # Process in batches for memory efficiency
            batch_size = 5  # Smaller batches for stability
            
            for batch_start in range(0, total_rows, batch_size):
                batch_end = min(batch_start + batch_size, total_rows)
                logger.info(f"🔄 Processing batch {batch_start + 1}-{batch_end} of {total_rows} rows...")
                
                for row_index in range(batch_start, batch_end):
                    try:
                        # Re-fetch rows for this iteration to avoid stale references
                        current_rows = self.driver.find_elements(*rows_locator)
                        
                        if row_index >= len(current_rows):
                            logger.warning(f"⚠️ Row {row_index + 1} no longer available")
                            continue
                        
                        row = current_rows[row_index]
                        cells = row.find_elements(By.TAG_NAME, "td")
                        
                        if len(cells) != len(self.columns):
                            logger.warning(f"⚠️ Row {row_index + 1}: Expected {len(self.columns)} columns, found {len(cells)}")
                            continue
                        
                        # Extract data with robust cell handling
                        row_data = {}
                        for col_index, (column, cell) in enumerate(zip(self.columns, cells)):
                            try:
                                # Robust cell text extraction
                                cell_text = self.extract_cell_text_robust(cell, row_index + 1, col_index + 1)
                                row_data[column] = cell_text
                            except Exception as cell_error:
                                logger.warning(f"⚠️ Error reading cell {col_index + 1} in row {row_index + 1}: {cell_error}")
                                row_data[column] = None
                        
                        scraped_data.append(row_data)
                        
                        # Progress logging
                        if (row_index + 1) % 10 == 0:
                            logger.info(f"📈 Processed {row_index + 1} rows so far...")
                        
                    except Exception as row_error:
                        logger.warning(f"⚠️ Error processing row {row_index + 1}: {row_error}")
                        continue
                
                # Memory cleanup between batches
                if batch_end < total_rows:
                    logger.debug(f"🧹 Batch {batch_start + 1}-{batch_end} complete, brief pause...")
                    time.sleep(1)
            
            logger.info(f"✅ Successfully scraped {len(scraped_data)} rows")
            return scraped_data
            
        except Exception as e:
            logger.error(f"❌ Table scraping failed: {e}")
            return []

    def extract_cell_text_robust(self, cell, row_num: int, col_num: int, max_retries: int = 3) -> Optional[str]:
        """
        Robust cell text extraction with retry mechanism
        """
        for attempt in range(max_retries):
            try:
                text = cell.text.strip()
                
                # Handle empty cells
                if text == '' or text == '-' or text is None:
                    return None
                
                return text
                
            except StaleElementReferenceException:
                if attempt < max_retries - 1:
                    logger.debug(f"🔄 Stale element in cell {col_num}, row {row_num}, retry {attempt + 1}")
                    time.sleep(0.5)
                    
                    # Re-find the cell
                    try:
                        rows = self.driver.find_elements(By.CSS_SELECTOR, "#fulltimemodelraw tbody tr")
                        if row_num - 1 < len(rows):
                            cells = rows[row_num - 1].find_elements(By.TAG_NAME, "td")
                            if col_num - 1 < len(cells):
                                cell = cells[col_num - 1]
                                continue
                    except Exception:
                        pass
                else:
                    logger.warning(f"⚠️ Persistent stale element in cell {col_num}, row {row_num}")
                    return None
            except Exception as e:
                logger.warning(f"⚠️ Unexpected error extracting cell text: {e}")
                return None
        
        return None

    def clean_and_convert_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and convert scraped data for database insertion"""
        logger.info("🧹 Cleaning and converting scraped data...")
        cleaned_data = []
        
        for row in data:
            try:
                cleaned_row = {}
                
                for column, value in row.items():
                    if column == 'timeupdated' and value:
                        # Convert datetime format: "29/08/2025, 18:44:35" -> ISO format
                        try:
                            dt = datetime.strptime(value, "%d/%m/%Y, %H:%M:%S")
                            cleaned_row[column] = dt.isoformat()
                        except ValueError:
                            cleaned_row[column] = value
                    elif column in ['min'] and value:
                        # Convert to integer
                        try:
                            cleaned_row[column] = int(value)
                        except (ValueError, TypeError):
                            cleaned_row[column] = None
                    elif column in ['modsup', 'hdp1', 'hprice', 'aprice'] + [f'homehdp{i}' for i in range(1, 21)] + [f'awayhdp{i}' for i in range(1, 21)] and value:
                        # Convert to float
                        try:
                            cleaned_row[column] = float(value)
                        except (ValueError, TypeError):
                            cleaned_row[column] = None
                    else:
                        # Keep as string or None
                        cleaned_row[column] = value if value else None
                
                cleaned_data.append(cleaned_row)
                
            except Exception as e:
                logger.warning(f"⚠️ Error cleaning row data: {e}")
                continue
        
        logger.info(f"✅ Cleaned {len(cleaned_data)} rows")
        return cleaned_data

    def save_to_supabase_robust(self, data: List[Dict[str, Any]]) -> bool:
        """
        Save data to Supabase with robust upsert handling
        """
        if not data:
            logger.warning("⚠️ No data to save")
            return False
        
        logger.info(f"💾 Saving {len(data)} records to Supabase with upsert...")
        
        try:
            success_count = 0
            error_count = 0
            
            for record in data:
                try:
                    # Create unique identifier from timeupdated date and hometeam
                    time_updated = record.get('timeupdated')
                    home_team = record.get('hometeam')
                    
                    if not time_updated or not home_team:
                        logger.warning("⚠️ Missing timeupdated or hometeam, skipping record")
                        error_count += 1
                        continue
                    
                    # Extract date part for duplicate checking
                    try:
                        if 'T' in time_updated:  # ISO format
                            date_part = time_updated.split('T')[0]
                        else:
                            date_part = time_updated.split(',')[0] if ',' in time_updated else time_updated
                    except Exception:
                        date_part = time_updated
                    
                    # Check for existing record
                    existing = self.supabase.table('inplay_football').select('id').eq('hometeam', home_team).like('timeupdated', f'{date_part}%').execute()
                    
                    if existing.data:
                        # Update existing record
                        record_id = existing.data[0]['id']
                        result = self.supabase.table('inplay_football').update(record).eq('id', record_id).execute()
                        logger.debug(f"🔄 Updated existing record for {home_team}")
                    else:
                        # Insert new record
                        result = self.supabase.table('inplay_football').insert(record).execute()
                        logger.debug(f"➕ Inserted new record for {home_team}")
                    
                    success_count += 1
                    
                except Exception as record_error:
                    logger.warning(f"⚠️ Error processing record for {record.get('hometeam', 'unknown')}: {record_error}")
                    error_count += 1
                    continue
            
            logger.info(f"✅ Successfully processed {success_count} out of {len(data)} records")
            logger.info(f"❌ Failed to process {error_count} records")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"❌ Supabase save failed: {e}")
            return False

    def run_scraper(self) -> bool:
        """
        Main scraper execution with comprehensive error handling
        """
        try:
            logger.info("🚀 Starting InPlay Football scraper...")
            
            # Setup components
            self.setup_driver()
            self.setup_supabase()
            
            # Execute scraping workflow
            if not self.login():
                return False
            
            if not self.navigate_to_fulltime_page():
                return False
            
            if not self.click_fulltime_raw_tab():
                return False
            
            # Scrape data
            scraped_data = self.scrape_table_data_robust()
            if not scraped_data:
                logger.error("❌ No data scraped")
                return False
            
            # Clean and save data
            cleaned_data = self.clean_and_convert_data(scraped_data)
            success = self.save_to_supabase_robust(cleaned_data)
            
            if success:
                logger.info("🎉 Scraper completed successfully!")
                return True
            else:
                logger.error("❌ Failed to save data to Supabase")
                return False
            
        except Exception as e:
            logger.error(f"💥 Scraper execution failed: {e}")
            return False
        
        finally:
            # Cleanup
            if self.driver:
                try:
                    self.driver.quit()
                    logger.info("🧹 ChromeDriver cleaned up")
                except Exception:
                    pass

def main():
    """Main execution function"""
    scraper = ProductionInPlayScraper()
    success = scraper.run_scraper()
    
    if success:
        logger.info("✅ Scraper execution completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ Scraper execution failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
