import pytest
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from config import BASE_URL, SUPERUSER_EMAIL, SUPERUSER_PASSWORD
from helpers import (
    login_as_superuser,
    random_string,
    wait_for,
    wait_for_text,
    wait_for_url_to_be,
    wait_for_invisibility,
    wait_for_toast_to_disappear
)
from locators import Auth, General, Settings

@pytest.mark.settings
def test_my_profile_tab_loads_correctly(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/settings")
    wait_for(driver, Settings.MY_PROFILE_TAB)
    assert SUPERUSER_EMAIL in driver.page_source

@pytest.mark.settings
def test_enter_edit_mode_and_cancel(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/settings")

    # Debug: print all button texts before clicking edit
    buttons = driver.find_elements(By.TAG_NAME, "button")
    print("DEBUG: Button texts before clicking edit:", [b.text for b in buttons])
    try:
        edit_btn = wait_for(driver, Settings.EDIT_BUTTON)
    except Exception:
        with open("debug_no_edit_button.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("DEBUG: No edit button found. Saved page source to debug_no_edit_button.html")
        raise
    edit_btn.click()

    import time
    time.sleep(1)  # Give time for UI to update

    # Debug: print all input names and ids after clicking edit
    inputs = driver.find_elements(By.TAG_NAME, "input")
    print("DEBUG: Inputs after clicking edit:", [(i.get_attribute("name"), i.get_attribute("id")) for i in inputs])

    try:
        assert wait_for(driver, Auth.FULL_NAME_INPUT).is_displayed()
    except Exception as e:
        # Save page source for debugging
        with open("debug_edit_mode_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("DEBUG: Saved page source to debug_edit_mode_page_source.html")
        print("DEBUG: Current URL:", driver.current_url)
        raise

    wait_for(driver, Settings.CANCEL_BUTTON).click()
    assert wait_for_invisibility(driver, Auth.FULL_NAME_INPUT)

@pytest.mark.settings
def test_update_full_name_successfully(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/settings")
    new_name = f"Super Admin {random_string(4)}"
    wait_for(driver, Settings.EDIT_BUTTON).click()
    name_input = wait_for(driver, Auth.FULL_NAME_INPUT)
    name_input.clear()
    name_input.send_keys(new_name)
    save_btn = wait_for(driver, Settings.SAVE_BUTTON)
    if save_btn.is_enabled():
        save_btn.click()
    wait_for(driver, General.TOAST_SUCCESS)
    wait_for_text(driver, (By.TAG_NAME, "body"), new_name)

@pytest.mark.settings
def test_update_email_with_invalid_format(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/settings")
    wait_for(driver, Settings.EDIT_BUTTON).click()
    email_input = wait_for(driver, Auth.EMAIL_INPUT_OTHER)
    email_input.clear()
    email_input.send_keys("invalid-email")
    save_btn = wait_for(driver, Settings.SAVE_BUTTON)
    save_btn.click()
    # Assert error messages appear
    wait_for_text(driver, (By.TAG_NAME, "body"), "Something went wrong")
    wait_for_text(driver, (By.TAG_NAME, "body"), "value is not a valid email address")

@pytest.mark.settings
def test_change_password_tab_loads(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/settings")
    wait_for(driver, Settings.PASSWORD_TAB).click()
    wait_for(driver, Auth.CURRENT_PASSWORD_INPUT)
    wait_for(driver, Auth.NEW_PASSWORD_INPUT)
    wait_for(driver, Auth.CONFIRM_PASSWORD_INPUT)

@pytest.mark.settings
def test_change_password_with_incorrect_current_password(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/settings")
    wait_for(driver, Settings.PASSWORD_TAB).click()
    wait_for(driver, Auth.CURRENT_PASSWORD_INPUT).send_keys("wrongpassword")
    new_password = random_string()
    wait_for(driver, Auth.NEW_PASSWORD_INPUT).send_keys(new_password)
    wait_for(driver, Auth.CONFIRM_PASSWORD_INPUT).send_keys(new_password)
    save_btn = wait_for(driver, Settings.SAVE_BUTTON)
    if save_btn.is_enabled():
        save_btn.click()
    wait_for(driver, General.TOAST_ERROR_TITLE)
    wait_for_text(driver, (By.TAG_NAME, "body"), "Something went wrong")
    wait_for_text(driver, (By.TAG_NAME, "body"), "Incorrect password")

@pytest.mark.settings
def test_change_password_with_mismatched_new_passwords(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/settings")

    wait_for(driver, Settings.PASSWORD_TAB).click()
    wait_for(driver, Auth.CURRENT_PASSWORD_INPUT).send_keys(SUPERUSER_PASSWORD)
    wait_for(driver, Auth.NEW_PASSWORD_INPUT).send_keys("newpassword1")
    wait_for(driver, Auth.CONFIRM_PASSWORD_INPUT).send_keys("newpassword2")

    # Blur the confirm password field to trigger validation
    wait_for(driver, Auth.CURRENT_PASSWORD_INPUT).click()

    save_btn = wait_for(driver, Settings.SAVE_BUTTON)
    assert not save_btn.is_enabled()

    try:
        error_elem = wait_for(driver, (By.CSS_SELECTOR, '[data-part="error-message"], [data-part="error-text"]'), timeout=3)
        assert "do not match" in error_elem.text.lower()
    except Exception as e:
        with open("debug_mismatched_passwords.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("DEBUG: Saved page source to debug_mismatched_passwords.html")
        raise

@pytest.mark.settings
def test_change_password_with_weak_new_password(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/settings")
    wait_for(driver, Settings.PASSWORD_TAB).click()
    wait_for(driver, Auth.NEW_PASSWORD_INPUT).send_keys("123")
    wait_for(driver, Auth.CURRENT_PASSWORD_INPUT).click()
    save_btn = wait_for(driver, Settings.SAVE_BUTTON)
    assert not save_btn.is_enabled()
    wait_for_text(driver, (By.TAG_NAME, "body"), "at least 8 characters")

@pytest.mark.settings
def test_appearance_tab_loads(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/settings")
    wait_for(driver, Settings.APPEARANCE_TAB).click()
    assert wait_for(driver, Settings.LIGHT_MODE_RADIO).is_displayed()
    assert wait_for(driver, Settings.DARK_MODE_RADIO).is_displayed()

@pytest.mark.settings
def test_switch_to_dark_mode(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/settings")
    wait_for(driver, Settings.APPEARANCE_TAB).click()
    wait_for(driver, Settings.DARK_MODE_RADIO).click()
    html_tag = driver.find_element(By.TAG_NAME, "html")
    assert "dark" in html_tag.get_attribute("class")

@pytest.mark.settings
def test_switch_to_light_mode(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/settings")
    wait_for(driver, Settings.APPEARANCE_TAB).click()
    wait_for(driver, Settings.DARK_MODE_RADIO).click()
    wait_for(driver, Settings.LIGHT_MODE_RADIO).click()
    html_tag = driver.find_element(By.TAG_NAME, "html")
    assert "light" in html_tag.get_attribute("class")

@pytest.mark.settings
def test_danger_zone_tab_not_visible_for_superuser(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/settings")
    with pytest.raises(TimeoutException):
        wait_for(driver, Settings.DANGER_ZONE_TAB, timeout=2)
