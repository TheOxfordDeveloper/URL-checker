import time
import os
import pickle
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
]

def setup_local_driver():
    """Set up Chrome WebDriver for local use (not headless)"""
    user_agent = random.choice(USER_AGENTS)
    
    options = uc.ChromeOptions()
    options.add_argument(f'--user-agent={user_agent}')
    
    # Create a user profile directory
    user_data_dir = os.path.join(os.getcwd(), 'chrome_profile')
    os.makedirs(user_data_dir, exist_ok=True)
    options.add_argument(f'--user-data-dir={user_data_dir}')
    
    print(f"Using Chrome profile at: {user_data_dir}")
    
    # Create undetected Chrome driver - NOT headless so you can see it
    driver = uc.Chrome(options=options)
    return driver

def handle_cookie_consent(driver):
    """Handle the cookie consent dialog"""
    try:
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
                
                # Try by class/id that might contain 'consent'
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

def save_cookies(driver, filename='cookies.pkl'):
    """Save browser cookies to file"""
    with open(filename, 'wb') as file:
        pickle.dump(driver.get_cookies(), file)
    print(f"Cookies saved to {filename}")

def generate_cookies():
    """Main function to generate cookies"""
    print("Starting cookie generation process...")
    driver = setup_local_driver()
    
    try:
        # Navigate to site homepage
        driver.get("https://www.equibase.com")
        
        # Handle cookie consent if it appears
        if handle_cookie_consent(driver):
            print("Cookie consent dialog handled")
        
        print("\n=== MANUAL ACTION REQUIRED ===")
        print("1. The browser window is now open")
        print("2. Please login to your Equibase account")
        print("3. Solve any CAPTCHAs that appear")
        print("4. Browse around a bit to establish a normal session")
        print("5. When done, come back to this terminal")
        print("=== Press Enter when you're done ===")
        input()
        
        # Save the authenticated session cookies
        save_cookies(driver)
        
        # Test the cookies by visiting a protected page
        print("\nTesting the cookies by visiting a page...")
        driver.get("https://www.equibase.com/profiles/Results.cfm?type=Stakes&stkid=1201")
        time.sleep(5)
        
        # Check if we're still logged in and no CAPTCHA appears
        if "captcha" in driver.page_source.lower() or "robot" in driver.page_source.lower():
            print("WARNING: CAPTCHA detected during testing. Cookies may not work reliably.")
        else:
            print("Test successful! No CAPTCHA detected.")
        
        print("\nCookies have been saved to 'cookies.pkl'")
        print("Now upload this file to your Digital Ocean server.")
        
    finally:
        # Ask if user wants to keep the browser open
        keep_open = input("\nKeep the browser open? (y/n): ").strip().lower() == 'y'
        if not keep_open:
            driver.quit()
            print("Browser closed.")
        else:
            print("Browser left open. Close it manually when done.")

if __name__ == "__main__":
    generate_cookies()