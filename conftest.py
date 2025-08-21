import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--start-maximized")
    
    # Fix for macOS ARM64 ChromeDriver issue
    try:
        # Try to get the ChromeDriver path
        driver_path = ChromeDriverManager().install()
        
        # Check if the path points to the correct executable
        if "THIRD_PARTY_NOTICES" in driver_path:
            # If it's pointing to the notices file, find the actual chromedriver
            driver_dir = os.path.dirname(driver_path)
            actual_driver_path = os.path.join(driver_dir, "chromedriver")
            if os.path.exists(actual_driver_path):
                driver_path = actual_driver_path
            else:
                # Try looking for chromedriver in the parent directory
                parent_dir = os.path.dirname(driver_dir)
                actual_driver_path = os.path.join(parent_dir, "chromedriver")
                if os.path.exists(actual_driver_path):
                    driver_path = actual_driver_path
        
        service = ChromeService(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        
    except Exception as e:
        print(f"Error setting up ChromeDriver: {e}")
        # Fallback: try without specifying the path (assumes chromedriver is in PATH)
        try:
            driver = webdriver.Chrome(options=options)
        except Exception as fallback_error:
            print(f"Fallback also failed: {fallback_error}")
            raise
    
    yield driver
    driver.quit()
