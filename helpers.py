import random
import string
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import SUPERUSER_EMAIL, SUPERUSER_PASSWORD, BASE_URL
from locators import Auth, Navbar, Dashboard, General

def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def random_email():
    return f"test_{random_string()}@example.com"

def login(driver, email, password, expect_success=True):
    driver.get(f"{BASE_URL}/login")
    wait_for(driver, Auth.EMAIL_INPUT).send_keys(email)
    wait_for(driver, Auth.PASSWORD_INPUT).send_keys(password)
    wait_for(driver, Auth.LOGIN_BUTTON).click()
    if expect_success:
        wait_for_url_to_be(driver, f"{BASE_URL}/")
        wait_for(driver, Dashboard.WELCOME_TEXT)

def login_as_superuser(driver):
    login(driver, SUPERUSER_EMAIL, SUPERUSER_PASSWORD)
    wait_for(driver, Dashboard.WELCOME_TEXT)

def logout(driver):
    try:
        user_menu = wait_for(driver, Navbar.USER_MENU)
        print("DEBUG: USER_MENU found, attempting to click.")
        user_menu.click()
    except Exception as e:
        print("DEBUG: Exception when clicking USER_MENU:", e)
        raise
    try:
        logout_btn = wait_for(driver, Navbar.LOGOUT_BUTTON)
        print("DEBUG: LOGOUT_BUTTON found, attempting to click.")
        logout_btn.click()
    except Exception as e:
        print("DEBUG: Exception when clicking LOGOUT_BUTTON:", e)
        raise
    wait_for_url_to_be(driver, f"{BASE_URL}/login")

def wait_for(driver, locator, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(locator))

def wait_for_all(driver, locator, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.visibility_of_all_elements_located(locator))

def wait_for_url_to_be(driver, url, timeout=10):
    WebDriverWait(driver, timeout).until(EC.url_to_be(url))

def wait_for_text(driver, locator, text, timeout=10):
    WebDriverWait(driver, timeout).until(EC.text_to_be_present_in_element(locator, text))

def wait_for_invisibility(driver, locator, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.invisibility_of_element_located(locator))

def wait_for_toast_to_disappear(driver, timeout=10):
    # Wait for both success and error toasts to disappear
    try:
        wait_for_invisibility(driver, General.TOAST_SUCCESS, timeout)
    except Exception:
        pass
    try:
        wait_for_invisibility(driver, General.TOAST_ERROR_TITLE, timeout)
    except Exception:
        pass
    time.sleep(0.5)  # Ensure overlays are fully gone before proceeding
