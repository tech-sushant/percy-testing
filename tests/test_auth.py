import pytest
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from config import BASE_URL, SUPERUSER_EMAIL, SUPERUSER_PASSWORD
from helpers import (
    login,
    login_as_superuser,
    logout,
    random_email,
    random_string,
    wait_for,
    wait_for_all,
    wait_for_url_to_be,
    wait_for_text,
    wait_for_invisibility,
    wait_for_toast_to_disappear
)
from locators import Auth, Dashboard, General, Navbar, Settings, Items, Admin


@pytest.mark.auth
def test_login_page_loads(driver):
    driver.get(f"{BASE_URL}/login")
    
    assert "Full Stack FastAPI Project" in driver.title
    wait_for(driver, Auth.EMAIL_INPUT)
    wait_for(driver, Auth.PASSWORD_INPUT)
    wait_for(driver, Auth.LOGIN_BUTTON)

@pytest.mark.auth
def test_login_with_valid_credentials(driver):
    login(driver, SUPERUSER_EMAIL, SUPERUSER_PASSWORD)
    
    assert wait_for(driver, Dashboard.WELCOME_TEXT).is_displayed()

@pytest.mark.auth
def test_login_with_invalid_email_format(driver):
    login(driver, "invalid-email", "password", expect_success=False)
    
    wait_for_text(driver, (By.TAG_NAME, "body"), "Invalid email address")

@pytest.mark.auth
def test_login_with_non_existent_user(driver):
    login(driver, random_email(), "password", expect_success=False)
    
    wait_for(driver, General.TOAST_ERROR_TITLE)
    wait_for_text(driver, General.TOAST_ERROR_DESCRIPTION, "Incorrect email or password")

@pytest.mark.auth
def test_login_with_incorrect_password(driver):
    login(driver, SUPERUSER_EMAIL, "wrongpassword", expect_success=False)
    
    wait_for(driver, General.TOAST_ERROR_TITLE)
    wait_for_text(driver, General.TOAST_ERROR_DESCRIPTION, "Incorrect email or password")

@pytest.mark.auth
def test_login_with_empty_credentials(driver):
    driver.get(f"{BASE_URL}/login")
    
    wait_for(driver, Auth.LOGIN_BUTTON).click()
    wait_for_text(driver, (By.TAG_NAME, "body"), "Username is required")

@pytest.mark.auth
def test_forgot_password_link_redirects(driver):
    driver.get(f"{BASE_URL}/login")
    
    wait_for(driver, Auth.FORGOT_PASSWORD_LINK).click()
    wait_for_url_to_be(driver, f"{BASE_URL}/recover-password")

@pytest.mark.auth
def test_signup_link_redirects(driver):
    driver.get(f"{BASE_URL}/login")
    
    wait_for(driver, Auth.SIGNUP_LINK).click()
    wait_for_url_to_be(driver, f"{BASE_URL}/signup")

@pytest.mark.auth
def test_signup_page_loads(driver):
    driver.get(f"{BASE_URL}/signup")
    
    assert "Full Stack FastAPI Project" in driver.title
    wait_for(driver, Auth.FULL_NAME_INPUT)
    wait_for(driver, Auth.EMAIL_INPUT)
    wait_for(driver, Auth.PASSWORD_INPUT)
    wait_for(driver, Auth.CONFIRM_PASSWORD_INPUT)

@pytest.mark.auth
def test_signup_with_valid_details(driver):
    driver.get(f"{BASE_URL}/signup")
    
    password = random_string()
    wait_for(driver, Auth.FULL_NAME_INPUT).send_keys("Test User")
    wait_for(driver, Auth.EMAIL_INPUT).send_keys(random_email())
    wait_for(driver, Auth.PASSWORD_INPUT).send_keys(password)
    wait_for(driver, Auth.CONFIRM_PASSWORD_INPUT).send_keys(password)
    wait_for(driver, Auth.SIGNUP_BUTTON).click()
    wait_for_url_to_be(driver, f"{BASE_URL}/login")

@pytest.mark.auth
def test_signup_with_existing_email(driver):
    driver.get(f"{BASE_URL}/signup")
    
    password = random_string()
    wait_for(driver, Auth.FULL_NAME_INPUT).send_keys("Test User")
    wait_for(driver, Auth.EMAIL_INPUT).send_keys(SUPERUSER_EMAIL)
    wait_for(driver, Auth.PASSWORD_INPUT).send_keys(password)
    wait_for(driver, Auth.CONFIRM_PASSWORD_INPUT).send_keys(password)
    wait_for(driver, Auth.SIGNUP_BUTTON).click()
    wait_for(driver, General.TOAST_ERROR_TITLE)
    wait_for_text(driver, General.TOAST_ERROR_DESCRIPTION, "already exists")

@pytest.mark.auth
def test_signup_with_mismatched_passwords(driver):
    driver.get(f"{BASE_URL}/signup")
    
    wait_for(driver, Auth.FULL_NAME_INPUT).send_keys("Test User")
    wait_for(driver, Auth.EMAIL_INPUT).send_keys(random_email())
    wait_for(driver, Auth.PASSWORD_INPUT).send_keys("password123")
    wait_for(driver, Auth.CONFIRM_PASSWORD_INPUT).send_keys("password456")
    wait_for(driver, Auth.SIGNUP_BUTTON).click()
    wait_for_text(driver, (By.TAG_NAME, "body"), "The passwords do not match")

@pytest.mark.auth
def test_signup_with_weak_password(driver):
    driver.get(f"{BASE_URL}/signup")
    
    wait_for(driver, Auth.PASSWORD_INPUT).send_keys("123")
    wait_for(driver, Auth.EMAIL_INPUT).click()
    wait_for_text(driver, (By.TAG_NAME, "body"), "at least 8 characters")

@pytest.mark.auth
def test_logout_redirects_to_login(driver):
    login_as_superuser(driver)
    logout(driver)
    
    assert driver.current_url == f"{BASE_URL}/login"

@pytest.mark.auth
def test_access_protected_route_after_logout(driver):
    login_as_superuser(driver)
    logout(driver)
    driver.get(f"{BASE_URL}/settings")
    
    wait_for_url_to_be(driver, f"{BASE_URL}/login")

@pytest.mark.auth
def test_password_recovery_sends_email(driver):
    driver.get(f"{BASE_URL}/recover-password")
    
    wait_for(driver, Auth.EMAIL_INPUT).send_keys(SUPERUSER_EMAIL)
    wait_for(driver, (By.XPATH, "//button[contains(text(), 'Continue')]")).click()
    wait_for(driver, General.TOAST_SUCCESS)

@pytest.mark.auth
def test_reset_password_with_mismatched_passwords(driver):
    driver.get(f"{BASE_URL}/reset-password?token=somefaketoken")
    
    wait_for(driver, Auth.NEW_PASSWORD_INPUT).send_keys("newValidPassword1")
    wait_for(driver, Auth.CONFIRM_PASSWORD_INPUT).send_keys("newValidPassword2")
    wait_for(driver, (By.XPATH, "//button[contains(text(), 'Reset')]")).click()
    wait_for_text(driver, (By.TAG_NAME, "body"), "The passwords do not match")

@pytest.mark.auth
def test_access_login_when_already_logged_in(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/login")
    
    wait_for_url_to_be(driver, f"{BASE_URL}/")
