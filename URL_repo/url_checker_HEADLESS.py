import csv
import time
import random
import os
import pickle
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
from seleniumwire import webdriver






# user agents to each process a different quarter of the csv file 
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.55'
]

# split csv file into 4 parts 
def split_csv(input_file, num_parts):
    with open(input_file, 'r', newline='', encoding='utf-8-sig') as infile:
        reader = csv.reader(infile)
        rows = list(reader)
    
    header = rows[0] if len(rows) > 0 else []
    data_rows = rows[1:] if len(rows) > 0 else []
    
    rows_per_part = len(data_rows) // num_parts
    
    for i in range(num_parts):
        start_idx = i * rows_per_part
        end_idx = (i + 1) * rows_per_part if i < num_parts - 1 else len(data_rows)
        
        output_file = f"{os.path.splitext(input_file)[0]}_part{i+1}.csv"
        
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(header)
            for row in data_rows[start_idx:end_idx]:
                writer.writerow(row)
        
        print(f"Created {output_file} with {end_idx - start_idx} rows")
    pass 


def setup_driver_with_profile(profile_directory=None, use_wire=True):
    """
    Set up Chrome WebDriver with comprehensive anti-detection techniques.
    
    Args:
        profile_directory (str, optional): Directory for Chrome user profile
        use_wire (bool, optional): Use seleniumwire for more advanced request handling
    
    Returns:
        WebDriver: Configured Chrome WebDriver
    """
    # Select a random user agent from the predefined list
    user_agent = random.choice(USER_AGENTS)
    
    # Configure Chrome options
    if use_wire:
        # Using seleniumwire for more advanced request interception
        chrome_options = webdriver.ChromeOptions()
    else:
        # Fallback to standard Selenium options
        chrome_options = Options()
    
    # Essential anti-detection settings
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(f'--user-agent={user_agent}')
    
    # Set up user profile directory
    if profile_directory:
        chrome_options.add_argument(f'--user-data-dir={profile_directory}')
    else:
        user_data_dir = os.path.join(os.getcwd(), 'chrome_profile')
        os.makedirs(user_data_dir, exist_ok=True)
        chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
        print(f"Using Chrome profile at: {user_data_dir}")
    
    # Additional browser fingerprinting bypass techniques
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Create the WebDriver
    if use_wire:
        # Seleniumwire driver with more advanced request interception
        driver = webdriver.Chrome(options=chrome_options)
        
        # Header manipulation interceptor
        def interceptor(request):
            # Modify headers to make headless state less detectable
            if 'Sec-WebDriver' in request.headers:
                del request.headers['Sec-WebDriver']
            
            # Add common headers to mimic a real browser
            request.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
            request.headers['Accept-Language'] = 'en-US,en;q=0.5'
            request.headers['Accept-Encoding'] = 'gzip, deflate, br'
            request.headers['Connection'] = 'keep-alive'
            request.headers['Upgrade-Insecure-Requests'] = '1'
        
        # Apply request interceptor
        driver.request_interceptor = interceptor
    else:
        # Standard Selenium driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Set a consistent window size to mimic a real browser
    driver.set_window_size(1080, 800)
    
    # Advanced stealth techniques
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": user_agent
    })
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    print("WebDriver set up with comprehensive anti-detection techniques")
    return driver

def save_cookies(driver, filename='cookies.pkl'):
    """Save browser cookies to file"""
    with open(filename, 'wb') as file:
        pickle.dump(driver.get_cookies(), file)
    print(f"Cookies saved to {filename}")

    pass 

def load_cookies(driver, filename='/root/scraping_project/cookies.pkl'):
    """Load cookies from file into browser session"""
    if os.path.exists(filename):
        with open(filename, 'rb') as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                # Handle domain issues that might arise when loading cookies
                try:
                    driver.add_cookie(cookie)
                except Exception as e:
                    print(f"Error loading cookie: {e}")
        print(f"Cookies loaded from {filename}")
        return True
    return False
    pass

def handle_cookie_consent(driver):
    """
    Handle the Equibase cookie consent dialog by clicking the 'Consent' button.
    Returns True if consent dialog was found and handled, False otherwise.
    """
    try:
        # Look for the consent dialog by its content or button text
        consent_indicators = [
            "Equibase asks for your consent to use your personal data",
            "Consent", 
            "Manage options"
        ]
        
        page_source = driver.page_source
        if any(indicator in page_source for indicator in consent_indicators):
            print("Cookie consent dialog detected!")
            
            # Try to find and click the Consent button
            try:
                # First try by text
                consent_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Consent')]")
                if consent_buttons:
                    consent_buttons[0].click()
                    print("Clicked Consent button by text")
                    time.sleep(2)
                    return True
                
                # Try by class/id that might contain 'consent' (case insensitive)
                consent_elements = driver.find_elements(By.XPATH, "//*[contains(translate(@class, 'CONSENT', 'consent'), 'consent') or contains(translate(@id, 'CONSENT', 'consent'), 'consent')]")
                if consent_elements:
                    for element in consent_elements:
                        if element.is_displayed() and element.is_enabled():
                            element.click()
                            print("Clicked consent element by class/id")
                            time.sleep(2)
                            return True
                
                # Last resort - try to find buttons within the dialog
                buttons = driver.find_elements(By.TAG_NAME, "button")
                for button in buttons:
                    if button.is_displayed() and button.is_enabled():
                        if "Consent" in button.text:
                            button.click()
                            print("Clicked Consent button found in button list")
                            time.sleep(2)
                            return True
                
                print("Could not find Consent button to click automatically")
            except Exception as e:
                print(f"Error clicking consent button: {e}")
            
            return False
        
        return False
    except Exception as e:
        print(f"Error handling cookie consent: {e}")
        return False
    
    pass 

# MODIFY THIS FUNCTION to avoid manual intervention
def login_and_setup_session(driver, base_url="https://www.equibase.com"):
    """
    Modified to avoid manual intervention - uses uploaded cookies instead
    """
    try:
        # Check if cookies file exists and load it
        if os.path.exists('/root/scraping_project/cookies.pkl'):
            # First navigate to the base domain before loading cookies
            driver.get(base_url)
            time.sleep(3)
            
            # Load the cookies
            cookies_loaded = load_cookies(driver)
            
            if cookies_loaded:
                print("Cookies loaded successfully")
                
                # Refresh the page to use the cookies
                driver.refresh()
                time.sleep(3)
                
                # Handle cookie consent if needed
                if handle_cookie_consent(driver):
                    print("Cookie consent dialog handled during session setup")
                
                # Check for CAPTCHA
                if "captcha" in driver.page_source.lower() or "robot" in driver.page_source.lower():
                    print("WARNING: CAPTCHA detected after loading cookies. Session may not be valid.")
                    print("Trying to proceed anyway...")
                else:
                    print("Session established successfully without CAPTCHA")
                
                return True
            else:
                print("Failed to load cookies")
                return False
        else:
            print("No cookies file found at 'cookies.pkl'")
            print("Please run the cookie generation script locally first, then upload the cookies.pkl file")
            return False
    except Exception as e:
        print(f"Error during session setup: {e}")
        return False

def add_random_behavior(driver):
    """Add random human-like behavior to the browser session"""
    # Random scrolling
    scroll_amount = random.randint(100, 500)
    driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
    time.sleep(random.uniform(0.5, 1.5))
    
    
    # Sometimes scroll back up
    if random.random() < 0.3:
        driver.execute_script(f"window.scrollBy(0, -{random.randint(50, 200)});")
        time.sleep(random.uniform(0.5, 1.0))
    
    pass 

    # Occasionally move mouse (this requires pyautogui, you'd need to pip install pyautogui)
    # Uncomment if you have pyautogui installed
    
    if random.random() < 0.2:
        try:
            import pyautogui 
            screen_width, screen_height = pyautogui.size()
            pyautogui.moveTo(
                random.randint(0, screen_width),
                random.randint(0, screen_height),
                duration=random.uniform(0.5, 1.0)
            )
        except:
            pass
    

def check_url_with_selenium(url, driver, debug=False, manual_captcha=False):
    """
    Check if a URL contains the specific error message using Selenium browser.
    Returns True if data is present (no error message) and False if the error message is found.
    """
    # Define the error message to look for
    error_message = "The Graded Stakes Profile you were searching for could not be found"
    
    try:
        # Navigate to the URL
        driver.get(url)
        
        # Add realistic wait time
        time.sleep(random.uniform(3, 5))
        
        # Check for and handle cookie consent dialog
        if handle_cookie_consent(driver):
            print("Cookie consent dialog handled successfully")
            # After consent, wait a bit and refresh the page source
            time.sleep(2)
            
        # Add random human-like behavior
        add_random_behavior(driver)
        
        # Get the page title
        page_title = driver.title
        
        if debug:
            print(f"Page title: {page_title}")
        
        # Get updated page source after potential consent handling
        page_source = driver.page_source
        
        # Check for actual CAPTCHA - common indicators
        captcha_indicators = [
            "captcha", "CAPTCHA", "robot", "Robot", 
            "human verification", "verify you're human"
        ]
        
        # Filter out cookie consent false positives
        is_captcha = False
        for indicator in captcha_indicators:
            if indicator in page_source and "Equibase asks for your consent" not in page_source:
                is_captcha = True
                break
        
        if is_captcha:
            if debug:
                print("Actual CAPTCHA detected!")
            
            if manual_captcha:
                print("\n=== MANUAL CAPTCHA SOLVING REQUIRED ===")
                print("Please solve the CAPTCHA in the browser window")
                print("=== Press Enter when you're done ===")
                input()
                
                # Refresh page source after manual intervention
                page_source = driver.page_source
                
                # Save cookies after CAPTCHA is solved
                save_cookies(driver)
            else:
                # Wait longer to see if CAPTCHA times out
                print("CAPTCHA detected - waiting for timeout...")
                time.sleep(15)
                page_source = driver.page_source
                
                # Check again for CAPTCHA
                if any(indicator in page_source for indicator in captcha_indicators):
                    print("CAPTCHA still present. Enable manual_captcha or use a different approach.")
                    return None  # Indicate CAPTCHA blocking
        
        # Look for error message in h2 tags
        h2_elements = driver.find_elements(By.TAG_NAME, "h2")
        
        if debug:
            print(f"Found {len(h2_elements)} h2 tags:")
            for i, h2 in enumerate(h2_elements):
                try:
                    print(f"  H2 #{i+1}: {h2.text.strip()}")
                except:
                    print(f"  H2 #{i+1}: [Could not read text]")
        
        # Check if any h2 contains the error message
        for h2 in h2_elements:
            try:
                if error_message in h2.text:
                    if debug:
                        print("Found error message in H2 tag - marking as NO")
                    return False  # No data is present
            except:
                continue
        
        # Check if error message is in the page source
        if error_message in page_source:
            if debug:
                print("Found error message in page source - marking as NO")
            return False  # No data is present
        
        if debug:
            print("Error message NOT found - marking as YES")
        return True  # Data is present (no error message)
            
    except Exception as e:
        print(f"Error checking {url}: {e}")
        return None  # Indicate an error occurred
    

    pass 

def process_csv(input_file, output_file, batch_size=30, debug=True, start_from=0, manual_captcha=False):
    """
    Process CSV with URL checking using a persistent browser profile.
    """
    # Set up the driver with profile
    driver = setup_driver_with_profile(use_wire=True)
    
    try:
        # Try to establish a session using the uploaded cookies
        login_success = login_and_setup_session(driver)
        if not login_success:
            print("Failed to set up session. Exiting.")
            return
        
        # Test the session with a visit to homepage
        driver.get("https://www.equibase.com")
        time.sleep(3)
        
        # Handle cookie consent if it appears on the homepage
        if handle_cookie_consent(driver):
            print("Cookie consent dialog handled on homepage test")
            time.sleep(2)
        
        # Check if we still get CAPTCHA on homepage
        if "captcha" in driver.page_source.lower() or "robot" in driver.page_source.lower():
            if "Equibase asks for your consent" in driver.page_source:
                print("Cookie consent dialog detected but not properly handled. Attempting again...")
                if handle_cookie_consent(driver):
                    print("Cookie consent handled on second attempt")
                    time.sleep(2)
            else:
                print("CAPTCHA detected on homepage. Session may not be valid.")
                if manual_captcha:
                    print("Please solve the CAPTCHA manually...")
                    input("Press Enter when done...")
                    save_cookies(driver)
                else:
                    print("Consider enabling manual_captcha mode or setting up a new session.")
                    return
        
        # Now process the CSV file
        with open(input_file, 'r', newline='', encoding='utf-8-sig') as infile:
            reader = csv.reader(infile)
            rows = list(reader)
            
        # Determine if header exists
        has_header = len(rows) > 1
        url_col_index = 0
            
        # Create or open output file for writing
        file_exists = os.path.isfile(output_file)
        mode = 'a' if start_from > 0 and file_exists else 'w'
        
        with open(output_file, mode, newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            
            # Write header row if starting from beginning
            if mode == 'w' and has_header:
                header_row = rows[0].copy()
                header_row.append("Data Present")
                writer.writerow(header_row)
            
            # Determine start index
            start_index = max(1 if has_header else 0, start_from)
            
            # Process rows in batches with careful timing
            processed_count = 0
            captcha_count = 0
            
            for i in range(start_index, len(rows)):
                row = rows[i].copy()
                
                if len(row) > 0:
                    url = row[url_col_index].strip()
                    
                    # Skip empty URLs
                    if not url:
                        row.append("N/A")
                        writer.writerow(row)
                        continue
                    
                    # Check if the URL is valid
                    if not url.startswith('http'):
                        url = 'https://' + url
                    
                    parsed_url = urlparse(url)
                    if not parsed_url.scheme or not parsed_url.netloc:
                        print(f"Invalid URL format: {url}")
                        row.append("Invalid URL")
                        writer.writerow(row)
                        continue
                    
                    print(f"Checking ({i}/{len(rows) - (1 if has_header else 0)}): {url}")
                    
                    # Variable delay before request
                    pre_delay = random.uniform(2, 5)
                    print(f"Waiting {pre_delay:.2f} seconds before request...")
                    time.sleep(pre_delay)
                    
                    # If we've hit too many CAPTCHAs, take a longer break
                    if captcha_count >= 2:
                        print("Too many CAPTCHAs encountered. Taking a long break...")
                        time.sleep(random.uniform(300, 600))  # 5-10 minute break
                        captcha_count = 0
                    
                    result = check_url_with_selenium(url, driver, debug=debug, manual_captcha=manual_captcha)
                    
                    # Handle CAPTCHA case
                    if result is None:
                        captcha_count += 1
                        row.append("CAPTCHA")
                    elif result is True:
                        row.append("yes")
                    else:
                        row.append("no")
                    
                    writer.writerow(row)
                    outfile.flush()
                    
                    # Variable delay after request
                    delay = random.uniform(5, 10)
                    print(f"Waiting {delay:.2f} seconds before next request...")
                    time.sleep(delay)
                    
                    processed_count += 1
                    
                    # Pause after processing batch_size URLs
                    if processed_count % batch_size == 0:
                        print(f"\nPaused after processing {processed_count} URLs.")
                        print(f"Currently at row {i} in the CSV.")
                        print(f"Please check the output file: {output_file}")
                        
                        # Take a longer break between batches - more variable
                        pause_time = random.uniform(60, 120)  # reduced to be quicker 
                        print(f"Taking a {pause_time/60:.1f}-minute break to avoid rate limiting...")
                        time.sleep(pause_time)
    
    finally:
        # Close the browser
        driver.quit()

if __name__ == "__main__":
    # Set file paths
    input_file = "/root/scraping_project/Equibase_URLs_csv.csv"
    output_file = "/root/scraping_project/CLOUD_results.csv"
    batch_size = 30  # Increased for faster processing
    
    # Modified behavior for Digital Ocean operation - always choose option 2
    mode = "2"  # Default to "Process CSV file"
    manual_captcha_mode = False  # No manual CAPTCHA since we're running headless
    
    print("Running in automated mode on Digital Ocean server")
    print(f"Using pre-loaded cookies from cookies.pkl")
    
    # Split the CSV into parts (you can adjust the number)
    print("Splitting CSV into 4 parts...")
    split_csv(input_file, 4)
    
    # Process each part with a delay between
    for part in range(1, 5):
        part_input = f"{os.path.splitext(input_file)[0]}_part{part}.csv"
        part_output = f"{os.path.splitext(output_file)[0]}_part{part}.csv"
        
        print(f"Processing part {part}/4: {part_input}")
        
        # Run with fully automated mode
        process_csv(part_input, part_output, batch_size, debug=True, start_from=0, manual_captcha=manual_captcha_mode)
        
        print(f"Completed part {part}/4")
        
        # Wait a bit before starting the next part
        if part < 4:
            wait_time = random.randint(300, 600)  # 5-10 minutes
            print(f"Waiting {wait_time} seconds before starting next part...")
            time.sleep(wait_time)
    
    print("All parts processed!")