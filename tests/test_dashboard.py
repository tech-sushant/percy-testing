import pytest
from selenium.webdriver.common.by import By
from config import BASE_URL
from helpers import (
    login_as_superuser,
    wait_for,
    wait_for_url_to_be,
)
from locators import Dashboard, Navbar


@pytest.mark.dashboard
def test_dashboard_displays_welcome_message(driver):
    login_as_superuser(driver)
    
    assert "Hi, " in wait_for(driver, (By.XPATH, "//*[contains(text(), 'Hi,')]")).text

@pytest.mark.dashboard
def test_sidebar_navigation_to_items(driver):
    login_as_superuser(driver)
    wait_for(driver, (By.XPATH, "//a[@href='/items']")).click()
    wait_for_url_to_be(driver, f"{BASE_URL}/items")
    
    assert wait_for(driver, (By.TAG_NAME, "h2")).text == "Items Management"

@pytest.mark.dashboard
def test_sidebar_navigation_to_settings(driver):
    login_as_superuser(driver)
    wait_for(driver, (By.XPATH, "//a[@href='/settings']")).click()
    wait_for_url_to_be(driver, f"{BASE_URL}/settings")
    
    assert wait_for(driver, (By.TAG_NAME, "h2")).text == "User Settings"

@pytest.mark.dashboard
def test_navbar_user_menu_opens(driver):
    login_as_superuser(driver)
    wait_for(driver, Navbar.USER_MENU).click()
    
    assert wait_for(driver, (By.XPATH, "//*[contains(text(), 'My Profile')]")).is_displayed()
    assert wait_for(driver, Navbar.LOGOUT_BUTTON).is_displayed()

@pytest.mark.dashboard
def test_404_page_for_invalid_route(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/invalid-route")
    
    assert wait_for(driver, (By.XPATH, "//*[contains(text(), '404')]")).is_displayed()
