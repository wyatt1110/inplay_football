#!/usr/bin/env python3
"""
InPlay Football Tips Scraper
Professional scraper for inplayfootballtips.co.uk Full-Time Model Raw data
Stores data in Supabase with duplicate prevention
"""

import os
import time
import logging
import re
import requests
import json
from datetime import datetime
from typing import List, Dict, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.service import Service

from supabase import create_client, Client

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('inplay_scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class InPlayFootballScraper:
    def __init__(self):
        """Initialize the scraper with production configuration"""
        # Login credentials
        self.username = "Wyatt1110"
        self.password = "Wiggers10"
        self.login_url = "https://inplayfootballtips.co.uk/login"
        self.fulltime_url = "https://inplayfootballtips.co.uk/full-time"
        
                # Supabase configuration - use environment variables for Railway deployment
        self.supabase_url = os.getenv('SUPABASE_URL', 'https://gwvnmzflxttdlhrkejmy.supabase.co')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd3dm5temZseHR0ZGxocmtlam15Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMzkwODc5NSwiZXhwIjoyMDQ5NDg0Nzk1fQ.5FcuTSXJJLGhfnAVhOEKACTBGCxiDMdMIQeOR2n19eI')

        # Chrome configuration for cloud deployment
        self.is_production = os.getenv('NODE_ENV') == 'production' or os.getenv('RAILWAY_ENVIRONMENT_NAME') is not None
        
        # Always run headless
        self.debug_mode = False
        
        self.driver = None
        self.supabase_client = None
        
        # Column mapping for the table (49 columns from HTML)
        self.columns = [
            'timeupdated', 'league', 'hometeam', 'awayteam', 'min', 'score',
            'modsup', 'hdp1', 'hprice', 'aprice', 'homehdp1', 'awayhdp1',
            'tg1', 'over_price', 'under_price', 'overtg1', 'undertg1',
            'hdp1_hval', 'hdp1_aval', 'tg1_oval', 'tg1_uval',
            'hdp2', 'homehdp2', 'awayhdp2', 'hdp3', 'homehdp3', 'awayhdp3',
            'hdp4', 'homehdp4', 'awayhdp4', 'modhome', 'modaway',
            'homeperc', 'awayperc', 'modtgs', 'tg2', 'overtg2', 'undertg2',
            'tg3', 'overtg3', 'undertg3', 'tg4', 'overtg4', 'undertg4',
            'modover', 'modunder', 'overperc', 'underperc',
            'startline', 'start_tgs', 'analysis'
        ]
        
        logger.info(f"InPlay Football Scraper initialized - Production: {self.is_production}")

    def setup_driver(self) -> None:
        """Setup Chrome WebDriver - EXACT copy from working TELEGRAM_BOTS_UPLOAD service"""
        try:
            logger.info("🔧 Setting up Chrome WebDriver...")
            
            chrome_options = Options()
            
            # Configuration matching working service
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-extensions")
            
            # Set Chrome binary path for Railway deployment
            if self.is_production:
                chrome_options.binary_location = "/usr/bin/google-chrome"
                service = Service("/usr/local/bin/chromedriver")
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                self.driver = webdriver.Chrome(options=chrome_options)
            
            # Set timeouts
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(60)
            
            logger.info("✅ Chrome WebDriver setup complete")
            
        except Exception as e:
            logger.error(f"❌ Chrome setup failed: {e}")
            raise

    def setup_supabase(self) -> None:
        """Setup Supabase client"""
        try:
            if self.supabase_url and self.supabase_key:
                self.supabase_client: Client = create_client(self.supabase_url, self.supabase_key)
                logger.info("✅ Supabase client setup complete")
            else:
                logger.warning("⚠️ Supabase not configured - data will not be saved to database")
                self.supabase_client = None
        except Exception as e:
            logger.error(f"❌ Error setting up Supabase client: {e}")
            self.supabase_client = None

    def login(self) -> bool:
        """Login to the website"""
        try:
            logger.info("🔐 Navigating to login page...")
            self.driver.get(self.login_url)
            
            # Wait for page to load and find login form
            timeout = 40 if self.is_production else 20
            wait = WebDriverWait(self.driver, timeout)
            
            # Find username field and enter credentials
            try:
                username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
                username_field.clear()
                username_field.send_keys(self.username)
                logger.info("✅ Username entered successfully")
            except Exception as e:
                logger.error(f"❌ Failed to find/fill username field: {e}")
                return False
            
            # Find password field and enter credentials  
            try:
                password_field = self.driver.find_element(By.NAME, "password")
                password_field.clear()
                password_field.send_keys(self.password)
                logger.info("✅ Password entered successfully")
            except Exception as e:
                logger.error(f"❌ Failed to find/fill password field: {e}")
                return False
            
            # Find and click login button
            try:
                login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
                login_button.click()
                logger.info("✅ Login button clicked")
            except Exception as e:
                logger.error(f"❌ Failed to find/click login button: {e}")
                return False
            
            # Wait for successful login - check for redirect or dashboard elements
            time.sleep(5 if self.is_production else 3)
            
            # Check if login was successful by verifying we're no longer on login page
            current_url = self.driver.current_url
            logger.info(f"🔍 Current URL after login: {current_url}")
            
            if "login" not in current_url:
                logger.info("✅ Login successful!")
                return True
            else:
                # Check for error messages on the page
                try:
                    # Look for specific error elements
                    error_messages = self.driver.find_elements(By.CSS_SELECTOR, ".error, .alert, .message")
                    if error_messages:
                        for error in error_messages:
                            if error.is_displayed():
                                logger.error(f"❌ Login error message: {error.text}")
                    
                    # Check page title
                    page_title = self.driver.title
                    logger.info(f"📄 Page title: {page_title}")
                    
                    # Look for any validation messages
                    page_source = self.driver.page_source
                    if "invalid" in page_source.lower() or "incorrect" in page_source.lower():
                        logger.error("❌ Login failed - credentials may be incorrect")
                    elif "required" in page_source.lower():
                        logger.error("❌ Login failed - required fields may not be filled")
                    else:
                        logger.error("❌ Login failed - still on login page (unknown reason)")
                        # Save a screenshot for debugging if in debug mode
                        if self.debug_mode:
                            try:
                                self.driver.save_screenshot("login_failure.png")
                                logger.info("📸 Screenshot saved as login_failure.png")
                            except:
                                pass
                        
                except Exception as debug_error:
                    logger.error(f"❌ Error during login debugging: {debug_error}")
                    logger.error("❌ Login failed - still on login page")
                return False
                
        except TimeoutException:
            logger.error("❌ Timeout during login process")
            return False
        except Exception as e:
            logger.error(f"❌ Error during login: {e}")
            return False

    def navigate_to_fulltime_page(self) -> bool:
        """Navigate to the full-time model page"""
        try:
            logger.info("🌐 Navigating to full-time page...")
            self.driver.get(self.fulltime_url)
            
            # Wait for page to load
            timeout = 40 if self.is_production else 20
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            time.sleep(3 if self.is_production else 2)
            logger.info("✅ Successfully navigated to full-time page")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error navigating to full-time page: {e}")
            return False

    def click_fulltime_raw_tab(self) -> bool:
        """Click on the 'Full-Time Model Raw' tab"""
        try:
            logger.info("🎯 Looking for 'Full-Time Model Raw' tab...")
            timeout = 40 if self.is_production else 20
            wait = WebDriverWait(self.driver, timeout)
            
            # Find the tab using the provided HTML structure
            raw_tab = wait.until(EC.presence_of_element_located((By.ID, "two-tab")))
            
            # Scroll to the tab to ensure it's visible
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", raw_tab)
            time.sleep(2)
            
            # Try multiple methods to click the tab
            try:
                # Method 1: Standard click
                raw_tab.click()
                logger.info("✅ Tab clicked using standard click")
            except Exception as e1:
                logger.warning(f"⚠️ Standard click failed: {e1}")
                try:
                    # Method 2: JavaScript click
                    self.driver.execute_script("arguments[0].click();", raw_tab)
                    logger.info("✅ Tab clicked using JavaScript click")
                except Exception as e2:
                    logger.warning(f"⚠️ JavaScript click failed: {e2}")
                    try:
                        # Method 3: Click the associated input element (for label)
                        associated_input = self.driver.find_element(By.ID, "two")
                        associated_input.click()
                        logger.info("✅ Tab clicked via associated input element")
                    except Exception as e3:
                        logger.error(f"❌ All click methods failed: {e3}")
                        return False
            
            # Wait for content to load (longer in production for stability)
            time.sleep(5 if self.is_production else 3)
            
            logger.info("✅ Successfully clicked 'Full-Time Model Raw' tab")
            return True
            
        except TimeoutException:
            logger.error("❌ Timeout waiting for 'Full-Time Model Raw' tab")
            return False
        except Exception as e:
            logger.error(f"❌ Error clicking 'Full-Time Model Raw' tab: {e}")
            return False

    def scrape_table_data(self) -> List[Dict]:
        """Scrape all data from the DataTable - handles dynamic content"""
        try:
            logger.info("📊 Starting table data scraping...")
            
            # Wait longer for dynamic table to load completely
            timeout = 120 if self.is_production else 60
            wait = WebDriverWait(self.driver, timeout)
            
            # Wait for table to be present and visible
            table = wait.until(EC.presence_of_element_located((By.ID, "fulltimemodelraw")))
            
            # Additional wait for table content to load
            logger.info("⏳ Waiting for table content to load...")
            time.sleep(10 if self.is_production else 5)
            
            # Scroll to ensure all content is loaded
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            scraped_data = []
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    logger.info(f"📋 Attempt {attempt + 1} to scrape table data...")
                    
                    # Re-find table and tbody to avoid stale references
                    table = self.driver.find_element(By.ID, "fulltimemodelraw")
                    tbody = table.find_element(By.TAG_NAME, "tbody")
                    
                    # Use CSS selector to find all rows at once - more reliable
                    rows = self.driver.find_elements(By.CSS_SELECTOR, "#fulltimemodelraw tbody tr")
                    
                    logger.info(f"📋 Found {len(rows)} rows in attempt {attempt + 1}")
                    
                    if len(rows) == 0:
                        logger.warning("⚠️ No rows found, waiting and retrying...")
                        time.sleep(5)
                        continue
                    
                    # Process each row
                    for i in range(len(rows)):
                        try:
                            # Re-find the row to avoid stale reference
                            current_rows = self.driver.find_elements(By.CSS_SELECTOR, "#fulltimemodelraw tbody tr")
                            if i >= len(current_rows):
                                logger.warning(f"⚠️ Row {i+1} no longer available, skipping")
                                break
                            
                            row = current_rows[i]
                            cells = row.find_elements(By.TAG_NAME, "td")
                            
                            if len(cells) != len(self.columns):
                                logger.warning(f"⚠️ Row {i+1}: Expected {len(self.columns)} columns, found {len(cells)}")
                                continue
                            
                            # Extract data from each cell
                            row_data = {}
                            for j, (column, cell) in enumerate(zip(self.columns, cells)):
                                try:
                                    # Retry cell text extraction with stale element handling
                                    cell_text = None
                                    for cell_retry in range(3):
                                        try:
                                            cell_text = cell.text.strip()
                                            break
                                        except StaleElementReferenceException:
                                            if cell_retry < 2:
                                                logger.debug(f"🔄 Stale element in cell {j+1}, row {i+1}, retry {cell_retry + 1}")
                                                time.sleep(0.5)
                                                # Re-find the row and cell
                                                current_rows = self.driver.find_elements(By.CSS_SELECTOR, "#fulltimemodelraw tbody tr")
                                                if i < len(current_rows):
                                                    row = current_rows[i]
                                                    cells = row.find_elements(By.TAG_NAME, "td")
                                                    if j < len(cells):
                                                        cell = cells[j]
                                                    else:
                                                        break
                                                else:
                                                    break
                                            else:
                                                logger.warning(f"⚠️ Persistent stale element in cell {j+1}, row {i+1}")
                                                break
                                    
                                    # Handle empty cells
                                    if cell_text == '' or cell_text == '-' or cell_text is None:
                                        cell_text = None
                                    
                                    row_data[column] = cell_text
                                except Exception as cell_error:
                                    logger.warning(f"⚠️ Error reading cell {j+1} in row {i+1}: {cell_error}")
                                    row_data[column] = None
                            
                            scraped_data.append(row_data)
                            
                            # Log progress every 10 rows
                            if (i + 1) % 10 == 0:
                                logger.info(f"📈 Processed {i + 1} rows so far...")
                            
                        except Exception as row_error:
                            logger.warning(f"⚠️ Error processing row {i+1}: {row_error}")
                            # Continue with next row instead of failing completely
                            continue
                    
                    # If we got data, break out of retry loop
                    if scraped_data:
                        logger.info(f"✅ Successfully scraped {len(scraped_data)} rows on attempt {attempt + 1}")
                        return scraped_data
                    else:
                        logger.warning(f"⚠️ No data scraped on attempt {attempt + 1}")
                        
                except Exception as attempt_error:
                    logger.error(f"❌ Error on attempt {attempt + 1}: {attempt_error}")
                    if attempt < max_retries - 1:
                        logger.info("🔄 Retrying...")
                        time.sleep(5)
                        continue
                    else:
                        logger.error("❌ All attempts failed")
                        break
            
            # If we get here, all attempts failed
            if not scraped_data:
                logger.error("❌ Failed to scrape any data after all attempts")
                
            return scraped_data
            
        except TimeoutException:
            logger.error("❌ Timeout waiting for table to load")
            return []
        except Exception as e:
            logger.error(f"❌ Error scraping table data: {e}")
            return []

    def clean_and_convert_data(self, data: List[Dict]) -> List[Dict]:
        """Clean and convert data types for database insertion"""
        cleaned_data = []
        
        for row in data:
            cleaned_row = {}
            
            for column, value in row.items():
                if column == 'timeupdated':
                    # Handle timestamp conversion with specific format: 29/08/2025, 18:44:35
                    if value and value.strip():
                        try:
                            # Parse datetime and convert to ISO string for Supabase
                            dt_obj = datetime.strptime(value.strip(), "%d/%m/%Y, %H:%M:%S")
                            cleaned_row[column] = dt_obj.isoformat()
                        except ValueError:
                            try:
                                # Try alternative format without seconds
                                dt_obj = datetime.strptime(value.strip(), "%d/%m/%Y, %H:%M")
                                cleaned_row[column] = dt_obj.isoformat()
                            except ValueError:
                                logger.warning(f"Could not parse TimeUpdated: {value}")
                                cleaned_row[column] = None
                    else:
                        cleaned_row[column] = None
                        
                elif column in ['league', 'hometeam', 'awayteam', 'score', 'analysis']:
                    # Text fields - clean whitespace
                    cleaned_row[column] = value.strip() if value else None
                    
                elif column == 'min':
                    # Integer field - handle various formats
                    if value and str(value).strip():
                        try:
                            # Extract numeric part only (in case there's extra text)
                            numeric_value = ''.join(filter(str.isdigit, str(value)))
                            if numeric_value:
                                cleaned_row[column] = int(numeric_value)
                            else:
                                cleaned_row[column] = None
                        except ValueError:
                            cleaned_row[column] = None
                    else:
                        cleaned_row[column] = None
                        
                else:
                    # All other fields are numeric (DECIMAL)
                    if value and str(value).strip() and str(value).strip() not in ['-', '']:
                        try:
                            # Clean the value - remove any non-numeric characters except decimal point and minus
                            clean_value = str(value).strip()
                            # Handle negative values and decimals
                            if clean_value.replace('-', '').replace('.', '').isdigit():
                                cleaned_row[column] = float(clean_value)
                            else:
                                # Try to extract numeric value from string
                                numeric_match = re.search(r'-?\d+\.?\d*', clean_value)
                                if numeric_match:
                                    cleaned_row[column] = float(numeric_match.group())
                                else:
                                    cleaned_row[column] = None
                        except (ValueError, AttributeError):
                            cleaned_row[column] = None
                    else:
                        cleaned_row[column] = None
            
            cleaned_data.append(cleaned_row)
        
        return cleaned_data

    def save_to_supabase(self, data: List[Dict]) -> bool:
        """Save data to Supabase with upsert functionality based on date + home team"""
        if not self.supabase_client:
            logger.warning("⚠️ Supabase client not configured - skipping database save")
            return False
        
        try:
            logger.info(f"💾 Saving {len(data)} records to Supabase with upsert...")
            
            # Clean and convert data
            clean_data = self.clean_and_convert_data(data)
            
            # Filter out records with no TimeUpdated or HomeTeam (required for uniqueness)
            valid_data = []
            skipped_records = 0
            
            for record in clean_data:
                if record.get('timeupdated') and record.get('hometeam'):
                    valid_data.append(record)
                else:
                    skipped_records += 1
            
            if skipped_records > 0:
                logger.warning(f"⚠️ Skipped {skipped_records} records with missing timeupdated or hometeam")
            
            if not valid_data:
                logger.error("❌ No valid records to save after cleaning")
                return False
            
            logger.info(f"📤 Processing {len(valid_data)} valid records with upsert logic...")
            
            # Process each record individually for proper upsert
            successful_upserts = 0
            
            for record in valid_data:
                try:
                    # Extract date from timeupdated for matching
                    timeupdated_str = record['timeupdated']
                    if isinstance(timeupdated_str, str):
                        # Parse the ISO string to get date
                        from datetime import datetime
                        dt = datetime.fromisoformat(timeupdated_str.replace('Z', '+00:00'))
                        match_date = dt.date().isoformat()
                    else:
                        # If it's already a datetime object
                        match_date = timeupdated_str.date().isoformat()
                    
                    hometeam = record['hometeam']
                    
                    # Check if record exists (same home team on same date)
                    existing_query = self.supabase_client.table('inplay_football').select('id').eq('hometeam', hometeam).gte('timeupdated', f'{match_date}T00:00:00').lt('timeupdated', f'{match_date}T23:59:59')
                    
                    existing_result = existing_query.execute()
                    
                    if existing_result.data and len(existing_result.data) > 0:
                        # Update existing record
                        existing_id = existing_result.data[0]['id']
                        update_result = self.supabase_client.table('inplay_football').update(record).eq('id', existing_id).execute()
                        
                        if update_result.data:
                            logger.info(f"✅ Updated existing record for {hometeam} on {match_date}")
                            successful_upserts += 1
                        else:
                            logger.warning(f"⚠️ Update failed for {hometeam} on {match_date}")
                    else:
                        # Insert new record
                        insert_result = self.supabase_client.table('inplay_football').insert(record).execute()
                        
                        if insert_result.data:
                            logger.info(f"✅ Inserted new record for {hometeam} on {match_date}")
                            successful_upserts += 1
                        else:
                            logger.warning(f"⚠️ Insert failed for {hometeam} on {match_date}")
                            
                except Exception as record_error:
                    logger.error(f"❌ Error processing record for {record.get('hometeam', 'unknown')}: {record_error}")
                    continue
            
            logger.info(f"✅ Successfully processed {successful_upserts} out of {len(valid_data)} records")
            return successful_upserts > 0
                
        except Exception as e:
            logger.error(f"❌ Error saving to Supabase: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            return False

    def run_scraper(self) -> bool:
        """Main method to run the complete scraping process"""
        try:
            logger.info("=" * 60)
            logger.info("🚀 Starting InPlay Football scraping process...")
            logger.info(f"Environment: {'Production' if self.is_production else 'Development'}")
            logger.info("=" * 60)
            
            # Setup components
            self.setup_driver()
            self.setup_supabase()
            
            # Execute scraping workflow
            if not self.login():
                logger.error("❌ Failed to login - aborting scraping")
                return False
            
            if not self.navigate_to_fulltime_page():
                logger.error("❌ Failed to navigate to full-time page - aborting scraping")
                return False
            
            if not self.click_fulltime_raw_tab():
                logger.error("❌ Failed to click Full-Time Model Raw tab - aborting scraping")
                return False
            
            # Scrape data
            scraped_data = self.scrape_table_data()
            
            if not scraped_data:
                logger.error("❌ No data scraped - aborting")
                return False
            
            logger.info(f"✅ Successfully scraped {len(scraped_data)} rows")
            
            # Save to database
            success = self.save_to_supabase(scraped_data)
            
            if success:
                logger.info("=" * 60)
                logger.info("🎉 Scraping process completed successfully!")
                logger.info("=" * 60)
                return True
            else:
                logger.error("❌ Failed to save data to database")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error in scraping process: {e}")
            return False
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                    logger.info("🛑 WebDriver closed")
                except:
                    pass

def main():
    """Main function to run the scraper"""
    import sys
    
    try:
        scraper = InPlayFootballScraper()
        success = scraper.run_scraper()
        
        if success:
            logger.info("✅ InPlay Football scraper completed successfully!")
            sys.exit(0)
        else:
            logger.error("❌ InPlay Football scraper failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Scraper interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
