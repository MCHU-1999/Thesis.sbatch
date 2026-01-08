"""
A script to download files using Selenium with Chromium browser
Designed for UrbanScene3D dataset download from Synology NAS (no GUI available)
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


class FileDownloader:
    def __init__(self, download_dir=None, headless=True):
        """
        Initialize the file downloader
        
        Args:
            download_dir (str): Directory to save downloaded files
            headless (bool): Run browser in headless mode
        """
        self.download_dir = download_dir or os.path.join(os.getcwd(), "downloads")
        self.headless = headless
        self.driver = None
        
        # Ensure download directory exists
        os.makedirs(self.download_dir, exist_ok=True)
    
    def setup_driver(self):
        """Setup Chrome driver with appropriate options"""
        chrome_options = Options()
        
        # Set download preferences
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # Additional options for remote/HPC environments
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print(f"Chrome driver initialized. Downloads will be saved to: {self.download_dir}")
        except Exception as e:
            print(f"Failed to initialize Chrome driver: {e}")
            raise
    
    def download_file(self, url, download_btn_xpath="//*[@id='ext-comp-1038']", wait_timeout=30):
        """
        Download file from given URL by clicking download button
        
        Args:
            url (str): URL to navigate to
            download_btn_xpath (str): XPath of the download button
            wait_timeout (int): Maximum time to wait for elements
        """
        if not self.driver:
            self.setup_driver()
        
        try:
            print(f"Navigating to: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, wait_timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Take screenshot before clicking (for debugging)
            screenshot_path = os.path.join(self.download_dir, "before_download.png")
            self.driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved: {screenshot_path}")
            
            # Find and click download button
            print(f"Looking for download button with XPath: {download_btn_xpath}")
            download_btn = WebDriverWait(self.driver, wait_timeout).until(
                EC.element_to_be_clickable((By.XPATH, download_btn_xpath))
            )
            
            print("Download button found, clicking...")
            
            # Get initial file count before download
            initial_files = set(os.listdir(self.download_dir)) if os.path.exists(self.download_dir) else set()
            
            download_btn.click()
            
            # Wait and check for new files or .crdownload files
            print("Checking for download initiation...")
            for i in range(10):  # Check for 10 seconds
                time.sleep(1)
                current_files = set(os.listdir(self.download_dir)) if os.path.exists(self.download_dir) else set()
                new_files = current_files - initial_files
                crdownload_files = [f for f in current_files if f.endswith('.crdownload')]
                
                if new_files or crdownload_files:
                    if crdownload_files:
                        print(f"Download started! Detected partial download file(s): {crdownload_files}")
                    if new_files:
                        print(f"New file(s) detected: {list(new_files)}")
                    return True
            
            # If no files detected, check browser downloads via JavaScript
            try:
                # This works in newer Chrome versions
                downloads = self.driver.execute_script("return chrome.downloads ? chrome.downloads.query({}) : []")
                if downloads:
                    print(f"Browser reports {len(downloads)} download(s) in progress")
                    return True
            except:
                pass
            
            print("WARNING: No download activity detected - download may have failed or already completed")
            return False
            
        except TimeoutException:
            print(f"Timeout: Could not find download button within {wait_timeout} seconds")
            return False
        except NoSuchElementException:
            print("Download button not found")
            return False
        except Exception as e:
            print(f"Error during download: {e}")
            return False
    
    def get_download_status(self):
        """
        Get detailed download status information
        
        Returns:
            dict: Download status information
        """
        status = {
            'active_downloads': 0,
            'completed_files': [],
            'in_progress_files': [],
            'file_sizes': {},
            'total_size': 0
        }
        
        if not os.path.exists(self.download_dir):
            return status
        
        for filename in os.listdir(self.download_dir):
            filepath = os.path.join(self.download_dir, filename)
            
            if filename.endswith('.crdownload'):
                # Chrome partial download file
                original_name = filename[:-11]  # Remove .crdownload extension
                file_size = os.path.getsize(filepath)
                status['in_progress_files'].append({
                    'name': original_name,
                    'temp_file': filename,
                    'current_size': file_size,
                    'size_mb': round(file_size / (1024*1024), 2)
                })
                status['active_downloads'] += 1
                status['total_size'] += file_size
                
            elif os.path.isfile(filepath):
                # Completed file
                file_size = os.path.getsize(filepath)
                status['completed_files'].append({
                    'name': filename,
                    'size': file_size,
                    'size_mb': round(file_size / (1024*1024), 2)
                })
                status['total_size'] += file_size
        
        return status
    
    def monitor_download_progress(self, check_interval=5):
        """
        Monitor download progress with detailed information
        
        Args:
            check_interval (int): Seconds between progress checks
        """
        print("Starting download monitoring...")
        last_sizes = {}
        
        while True:
            status = self.get_download_status()
            
            if status['active_downloads'] == 0:
                if status['completed_files']:
                    print("\nAll downloads completed!")
                    for file_info in status['completed_files']:
                        print(f"   {file_info['name']} ({file_info['size_mb']} MB)")
                    return True
                else:
                    print("No active downloads detected yet...")
            else:
                print(f"\nActive downloads: {status['active_downloads']}")
                
                for file_info in status['in_progress_files']:
                    filename = file_info['name']
                    current_size = file_info['current_size']
                    current_mb = file_info['size_mb']
                    
                    # Calculate download speed
                    if filename in last_sizes:
                        bytes_downloaded = current_size - last_sizes[filename]['size']
                        time_elapsed = time.time() - last_sizes[filename]['time']
                        if time_elapsed > 0:
                            speed_bps = bytes_downloaded / time_elapsed
                            speed_mbps = speed_bps / (1024*1024)
                            print(f"   {filename}: {current_mb} MB (Speed: {speed_mbps:.2f} MB/s)")
                        else:
                            print(f"   {filename}: {current_mb} MB (Calculating speed...)")
                    else:
                        print(f"   {filename}: {current_mb} MB (Starting...)")
                    
                    last_sizes[filename] = {
                        'size': current_size,
                        'time': time.time()
                    }
            
            time.sleep(check_interval)
    
    def wait_for_download_completion(self, timeout=3600, detailed_monitoring=True):
        """
        Wait for download to complete with optional detailed monitoring
        
        Args:
            timeout (int): Maximum time to wait in seconds
            detailed_monitoring (bool): Use detailed progress monitoring
        """
        if detailed_monitoring:
            print("Using detailed download monitoring...")
            start_time = time.time()
            
            try:
                while time.time() - start_time < timeout:
                    status = self.get_download_status()
                    
                    if status['active_downloads'] == 0 and status['completed_files']:
                        print("\nDownload completed!")
                        return True
                    
                    if status['active_downloads'] > 0:
                        print(f"\nMonitoring {status['active_downloads']} active download(s):")
                        for file_info in status['in_progress_files']:
                            print(f"   {file_info['name']}: {file_info['size_mb']} MB")
                        
                        # Start detailed monitoring
                        self.monitor_download_progress()
                        return True
                    
                    # print("Waiting for download to start...")
                    time.sleep(5)
                    
            except KeyboardInterrupt:
                print("\nDownload monitoring interrupted by user")
                return False
        else:
            # Original simple method
            print("Waiting for download to complete...")
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                crdownload_files = [f for f in os.listdir(self.download_dir) if f.endswith('.crdownload')]
                
                if not crdownload_files:
                    print("Download completed!")
                    return True
                
                print(f"Download in progress... ({len(crdownload_files)} files)")
                time.sleep(10)
        
        print("Download timeout reached")
        return False
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            print("Browser closed")


def main():
    """Main function to demonstrate usage"""
    # Configuration
    # Replace with actual URL
    DOWNLOAD_URL = "https://syn4-rs3yjlbkqq3nv33cc6bsalm25e-103-40-249-227.szuvccnas.direct.quickconnect.to:5001/d/s/lT61obCnx48mOc1FrPtUiuZ8eNCOrEQd/27C8eKMNd1YBpLxJTbYY-jMWU7vRHhbs-5bHAJ9227Ag"
    # Replace with your desired path
    DOWNLOAD_DIR = "/tudelft.net/staff-umbrella/Deep3D/mingchiehhu" 
    # The XPath to the download btn
    DOWNLOAD_BUTTON_XPATH = "//*[@id='ext-comp-1038']"
    
    # Create downloader instance
    downloader = FileDownloader(download_dir=DOWNLOAD_DIR, headless=True)
    
    try:
        # Download the file
        success = downloader.download_file(
            url=DOWNLOAD_URL,
            download_btn_xpath=DOWNLOAD_BUTTON_XPATH,
            wait_timeout=60
        )
        
        if success:
            # Wait for download to complete
            downloader.wait_for_download_completion(timeout=7200)  # 2 hours timeout
        else:
            print("Failed to initiate download")
    
    except KeyboardInterrupt:
        print("\nDownload interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        downloader.close()


if __name__ == "__main__":
    main()