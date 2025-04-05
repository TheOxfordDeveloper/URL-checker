import pickle
import time
import os
import sys
import undetected_chromedriver as uc

def load_cookies(filename):
    """Load cookies from a file with extensive debugging."""
    print(f"\nAttempting to load cookies from: {filename}")
    
    # Print current working directory and list files
    current_dir = os.getcwd()
    print(f"Current working directory: {current_dir}")
    
    # Check file existence
    full_path = os.path.join(current_dir, filename)
    
    if not os.path.exists(full_path):
        print(f"ERROR: File does not exist: {full_path}")
        return []
    
    # Load cookies
    try:
        with open(full_path, 'rb') as file:
            cookies = pickle.load(file)
        print(f"Successfully loaded {len(cookies)} cookies from {full_path}")
        
        return cookies
    except Exception as e:
        print(f"Detailed error loading {full_path}: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_cookies():
    """Test if the uploaded cookies work properly with extensive logging"""
    print("Starting cookie testing process...")
    
    # Try loading cookies from both files
    cookies_consent = load_cookies('/root/scraping_project/cookies_after_consent.pkl')
    cookies_pages = load_cookies('/root/scraping_project/cookies_after_visiting_pages.pkl')
    
    # Merge the two cookie lists
    all_cookies = cookies_consent + cookies_pages
    
    if not all_cookies:
        print("ERROR: No cookies found to load!")
        return False
    
    # Detailed system and environment information
    print("\nSystem Information:")
    print(f"Python Version: {sys.version}")
    print(f"Platform: {sys.platform}")
    
    # Set up headless browser 
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    import logging
    logging.basicConfig(level=logging.DEBUG)


    try:
        driver = uc.Chrome(options=options)
    except Exception as e:
        print(f"CRITICAL ERROR setting up WebDriver: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    try:
        # First navigate to base site
        print("\nNavigating to Equibase site...")
        driver.get("https://www.equibase.com")
        time.sleep(5)
        
        # Load all cookies
        print("\nLoading cookies...")
        for cookie in all_cookies:
            try:
                driver.add_cookie(cookie)
                print(f"Added cookie: {cookie.get('name', 'Unknown')}")
            except Exception as e:
                print(f"Error loading individual cookie: {e}")
        
        # Refresh page
        driver.refresh()
        time.sleep(3)
        
        # Test on a specific URL that would require login
        print("\nTesting access to a sample URL...")
        test_url = "https://www.equibase.com/profiles/Results.cfm?type=Stakes&stkid=1201"
        driver.get(test_url)
        time.sleep(5)
        
        # Capture and print page source for debugging
        page_source = driver.page_source
        print("\nPage Source Preview (first 1000 characters):")
        print(page_source[:1000])
        
        # Check for CAPTCHA or login prompts
        page_source_lower = page_source.lower()
        
        if "captcha" in page_source_lower or "robot" in page_source_lower:
            print("CAPTCHA detected! Cookies may not be working properly.")
            return False
        
        if "login" in page_source_lower and "password" in page_source_lower:
            print("Login page detected! Cookies may not be working properly.")
            return False
        
        # Check for error message
        if "The Graded Stakes Profile you were searching for could not be found" in page_source:
            print("Error message found - but this is expected if the URL doesn't have data")
            print("Cookies appear to be working correctly!")
            return True
        
        print("No CAPTCHA or login prompts detected. Cookies appear to be working correctly!")
        return True
    
    except Exception as e:
        print(f"Comprehensive error testing cookies: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        driver.quit()

if __name__ == "__main__":
    success = test_cookies()
    if success:
        print("\nTest PASSED: Cookies are working!")
        print("You can now run your main script.")
    else:
        print("\nTest FAILED: Cookies are not working correctly.")
        print("Please regenerate cookies locally and upload again.")