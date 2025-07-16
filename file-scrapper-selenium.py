import requests
import os
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def setup_driver():
    """Setup Chrome driver with appropriate options"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Remove this line if you want to see the browser
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        print("Make sure ChromeDriver is installed and in PATH")
        print("Install with: pip install webdriver-manager")
        return None

def get_all_filenames(url="https://cycling.data.tfl.gov.uk/"):
    """Extract all CSV filenames from the TfL cycling data website"""
    driver = setup_driver()
    if not driver:
        return []
    
    try:
        print("Loading TfL cycling data website...")
        driver.get(url)
        
        # Wait for the page to load and content to appear
        print("Waiting for content to load...")
        wait = WebDriverWait(driver, 60)  # Increased timeout
        
        # Wait for any links to appear
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "a")))
        
        # Give extra time for JavaScript to fully load the file list
        print("Waiting for file list to populate...")
        time.sleep(10)
        
        # Get all links
        links = driver.find_elements(By.TAG_NAME, "a")
        print(f"Found {len(links)} total links on page")
        
        # Extract CSV file information
        csv_files = []
        for link in links:
            try:
                href = link.get_attribute("href")
                text = link.text.strip()
                
                if href and href.endswith(".csv"):
                    filename = href.split("/")[-1]
                    csv_files.append({
                        'filename': filename,
                        'url': href,
                        'text': text
                    })
            except Exception as e:
                continue
        
        print(f"Found {len(csv_files)} CSV files")
        return csv_files
        
    except Exception as e:
        print(f"Error scraping website: {e}")
        return []
    finally:
        driver.quit()

def extract_file_number(filename):
    """
    Extract file number from filename based on different patterns
    This function tries to identify the sequential number in various filename formats
    """
    # Pattern 1: Look for numbers at the start (like 01a, 02a, etc.)
    match = re.search(r'^(\d+)[a-zA-Z]', filename)
    if match:
        return int(match.group(1))
    
    # Pattern 2: Look for numbers in the filename
    numbers = re.findall(r'\d+', filename)
    if numbers:
        # Try to identify which number might be the file sequence
        for num in numbers:
            num_int = int(num)
            if 1 <= num_int <= 1000:  # Reasonable range for file numbers
                return num_int
    
    return None

def filter_files_by_range(csv_files, start_num=246, end_num=386):
    """Filter files based on the number range (246-386)"""
    filtered_files = []
    
    print(f"\nAnalyzing filenames to find files {start_num}-{end_num}...")
    print("Sample filenames found:")
    for i, file_info in enumerate(csv_files[:10]):  # Show first 10 as sample
        file_num = extract_file_number(file_info['filename'])
        print(f"  {file_info['filename']} -> File number: {file_num}")
    
    print(f"\nFiltering files in range {start_num}-{end_num}...")
    
    for file_info in csv_files:
        file_num = extract_file_number(file_info['filename'])
        if file_num and start_num <= file_num <= end_num:
            file_info['file_number'] = file_num
            filtered_files.append(file_info)
    
    # Sort by file number
    filtered_files.sort(key=lambda x: x.get('file_number', 0))
    
    print(f"Found {len(filtered_files)} files in range {start_num}-{end_num}")
    
    return filtered_files

def download_file(file_info, download_dir="cycling_data"):
    """Download a single file"""
    filename = file_info['filename']
    url = file_info['url']
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(download_dir, exist_ok=True)
        
        # Check if file already exists
        file_path = os.path.join(download_dir, filename)
        if os.path.exists(file_path):
            print(f"✓ Already exists: {filename}")
            return True
        
        print(f"Downloading: {filename}")
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            file_size = len(response.content)
            print(f"✓ Downloaded: {filename} ({file_size:,} bytes)")
            return True
        else:
            print(f"✗ Failed: {filename} (HTTP {response.status_code})")
            return False
            
    except Exception as e:
        print(f"✗ Error downloading {filename}: {str(e)}")
        return False

def main():
    print("TfL Cycling Data Scraper")
    print("=" * 50)
    
    # Step 1: Get all filenames from the website
    print("\nStep 1: Scraping website for all CSV files...")
    csv_files = get_all_filenames()
    
    if not csv_files:
        print("No CSV files found. The website might be down or the structure changed.")
        return
    
    # Step 2: Show all files for inspection
    print(f"\nStep 2: Found {len(csv_files)} CSV files total")
    print("\nAll files found:")
    for i, file_info in enumerate(csv_files, 1):
        file_num = extract_file_number(file_info['filename'])
        print(f"{i:3d}. {file_info['filename']} (File #: {file_num})")
    
    # Step 3: Filter files by range
    start_range = int(input(f"\nEnter start file number (default 246): ") or "246")
    end_range = int(input(f"Enter end file number (default 386): ") or "386")
    
    filtered_files = filter_files_by_range(csv_files, start_range, end_range)
    
    if not filtered_files:
        print(f"No files found in range {start_range}-{end_range}")
        print("You might need to adjust the filtering logic based on the actual filename patterns.")
        return
    
    # Step 4: Show filtered files
    print(f"\nFiles to download ({len(filtered_files)} files):")
    for file_info in filtered_files:
        print(f"  {file_info['file_number']:3d}. {file_info['filename']}")
    
    # Step 5: Confirm and download
    confirm = input(f"\nDownload these {len(filtered_files)} files? (y/n): ").lower().strip()
    if confirm != 'y':
        print("Download cancelled.")
        return
    
    print(f"\nStep 6: Downloading {len(filtered_files)} files...")
    successful = 0
    failed = 0
    
    for i, file_info in enumerate(filtered_files, 1):
        print(f"\n[{i}/{len(filtered_files)}]", end=" ")
        if download_file(file_info):
            successful += 1
        else:
            failed += 1
        
        # Small delay to be respectful to the server
        time.sleep(1)
    
    # Summary
    print(f"\n" + "=" * 50)
    print(f"Download Complete!")
    print(f"✓ Successful: {successful}")
    print(f"✗ Failed: {failed}")
    print(f"Files saved to: ./cycling_data/")