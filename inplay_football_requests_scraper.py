#!/usr/bin/env python3
"""
InPlay Football Scraper - Requests-Based (Railway Compatible)
No browser required - works 100% on Railway containers
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
import json

# Railway-compatible libraries (no browser required)
import requests
from bs4 import BeautifulSoup
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

class RailwayCompatibleScraper:
    """
    Railway-compatible scraper using requests + BeautifulSoup
    No Chrome/Selenium - works 100% on Railway containers
    """
    
    def __init__(self):
        """Initialize with Railway-compatible configuration"""
        self.session = requests.Session()
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
        
        # Setup session headers to mimic real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
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
        
        logger.info(f"🚀 Railway-Compatible Scraper initialized - Production: {self.is_production}")

    def setup_supabase(self) -> None:
        """Initialize Supabase client"""
        try:
            logger.info("🔧 Setting up Supabase client...")
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            logger.info("✅ Supabase client initialized")
        except Exception as e:
            logger.error(f"❌ Supabase setup failed: {e}")
            raise

    def login(self) -> bool:
        """Login using requests session"""
        try:
            logger.info("🔐 Logging into InPlay Football Tips...")
            
            # Get login page to extract any CSRF tokens or form data
            login_page = self.session.get(self.login_url, timeout=30)
            login_page.raise_for_status()
            
            soup = BeautifulSoup(login_page.content, 'html.parser')
            
            # Find login form
            form = soup.find('form')
            if not form:
                logger.error("❌ Could not find login form")
                return False
            
            # Prepare login data
            login_data = {
                'username': self.username,
                'password': self.password
            }
            
            # Extract any hidden fields (CSRF tokens, etc.)
            hidden_inputs = form.find_all('input', type='hidden')
            for hidden in hidden_inputs:
                name = hidden.get('name')
                value = hidden.get('value', '')
                if name:
                    login_data[name] = value
            
            # Submit login form
            login_response = self.session.post(self.login_url, data=login_data, timeout=30)
            login_response.raise_for_status()
            
            # Check if login was successful (redirect or no login form on response)
            if 'login' not in login_response.url.lower() or 'dashboard' in login_response.url.lower():
                logger.info("✅ Successfully logged in")
                return True
            else:
                # Check response content for success indicators
                soup = BeautifulSoup(login_response.content, 'html.parser')
                if not soup.find('form') or 'welcome' in soup.get_text().lower():
                    logger.info("✅ Successfully logged in")
                    return True
                else:
                    logger.error("❌ Login failed - still on login page")
                    return False
                
        except Exception as e:
            logger.error(f"❌ Login failed: {e}")
            return False

    def get_fulltime_page(self) -> Optional[BeautifulSoup]:
        """Get the full-time page content"""
        try:
            logger.info("🏈 Getting full-time page...")
            response = self.session.get(self.fulltime_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.info("✅ Successfully retrieved full-time page")
            return soup
            
        except Exception as e:
            logger.error(f"❌ Failed to get full-time page: {e}")
            return None

    def extract_table_data(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract table data from the full-time page"""
        try:
            logger.info("📊 Extracting table data...")
            
            # Find the Full-Time Model Raw table
            # Try different selectors to find the table
            table = None
            table_selectors = [
                '#fulltimemodelraw',
                'table#fulltimemodelraw',
                '.tab-content table',
                'table'
            ]
            
            for selector in table_selectors:
                table = soup.select_one(selector)
                if table:
                    logger.info(f"✅ Found table with selector: {selector}")
                    break
            
            if not table:
                logger.error("❌ Could not find table")
                return []
            
            # Extract table rows
            rows = table.find('tbody')
            if not rows:
                rows = table
            
            data_rows = rows.find_all('tr')
            logger.info(f"📋 Found {len(data_rows)} rows")
            
            scraped_data = []
            
            for row_index, row in enumerate(data_rows):
                try:
                    cells = row.find_all(['td', 'th'])
                    
                    # Skip header rows
                    if not cells or len(cells) < len(self.columns):
                        continue
                    
                    # Extract cell data
                    row_data = {}
                    for col_index, (column, cell) in enumerate(zip(self.columns, cells)):
                        try:
                            cell_text = cell.get_text(strip=True)
                            
                            # Handle empty cells
                            if cell_text == '' or cell_text == '-':
                                cell_text = None
                            
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
            
            logger.info(f"✅ Successfully extracted {len(scraped_data)} rows")
            return scraped_data
            
        except Exception as e:
            logger.error(f"❌ Table extraction failed: {e}")
            return []

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

    def save_to_supabase(self, data: List[Dict[str, Any]]) -> bool:
        """Save data to Supabase with upsert handling"""
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
        """Main scraper execution - Railway compatible"""
        try:
            logger.info("🚀 Starting Railway-compatible scraper...")
            
            # Setup components
            self.setup_supabase()
            
            # Execute scraping workflow
            if not self.login():
                return False
            
            # Get page content
            soup = self.get_fulltime_page()
            if not soup:
                return False
            
            # Extract data
            scraped_data = self.extract_table_data(soup)
            if not scraped_data:
                logger.error("❌ No data extracted")
                return False
            
            # Clean and save data
            cleaned_data = self.clean_and_convert_data(scraped_data)
            success = self.save_to_supabase(cleaned_data)
            
            if success:
                logger.info("🎉 Scraper completed successfully!")
                return True
            else:
                logger.error("❌ Failed to save data to Supabase")
                return False
            
        except Exception as e:
            logger.error(f"💥 Scraper execution failed: {e}")
            return False

def main():
    """Main execution function"""
    scraper = RailwayCompatibleScraper()
    success = scraper.run_scraper()
    
    if success:
        logger.info("✅ Scraper execution completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ Scraper execution failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
