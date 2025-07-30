import pytest
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from config import BASE_URL
from helpers import (
    login,
    login_as_superuser,
    random_email,
    random_string,
    wait_for,
    wait_for_all,
    wait_for_url_to_be,
    wait_for_text,
    wait_for_invisibility,
    wait_for_toast_to_disappear
)
from locators import Auth, Dashboard, General, Items

ACTIONS_MENU_BUTTON_LOCATOR = (By.CSS_SELECTOR, "td:last-child button")

@pytest.mark.items
def test_add_item_dialog_opens_and_closes(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/items")
    
    wait_for(driver, Items.ADD_ITEM_BUTTON).click()
    dialog_title = wait_for(driver, General.DIALOG_TITLE)
    assert "Add Item" in dialog_title.text
    wait_for(driver, Items.CANCEL_BUTTON).click()
    assert wait_for_invisibility(driver, General.DIALOG_TITLE)

@pytest.mark.items
def test_add_item_with_valid_data(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/items")
    
    item_title = f"My Test Item {random_string()}"
    wait_for(driver, Items.ADD_ITEM_BUTTON).click()
    wait_for(driver, General.DIALOG_TITLE) 
    wait_for(driver, Items.TITLE_INPUT).send_keys(item_title)
    wait_for(driver, Items.DESCRIPTION_INPUT).send_keys("A description")
    wait_for(driver, Items.SAVE_BUTTON).click()
    wait_for(driver, General.TOAST_SUCCESS)
    # Navigate to the last page to find the newly added item
    while True:
        next_button = wait_for(driver, (By.XPATH, "//button[@aria-label='next page']"))
        if not next_button.is_enabled():
            break
        next_button.click()
        wait_for_toast_to_disappear(driver)
    try:
        wait_for_text(driver, Items.ITEMS_TABLE, item_title)
    except TimeoutException:
        assert False, (
            f"Item title '{item_title}' not found in table after adding item.\n"
            f"DEBUG PAGE SOURCE:\n{driver.page_source}"
        )

@pytest.mark.items
def test_add_item_with_missing_title(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/items")
    
    wait_for(driver, Items.ADD_ITEM_BUTTON).click()
    wait_for(driver, General.DIALOG_TITLE)
    wait_for(driver, Items.DESCRIPTION_INPUT).send_keys("A description")
    assert not wait_for(driver, Items.SAVE_BUTTON).is_enabled()

@pytest.mark.items
def test_items_empty_state_is_shown(driver):
    email, password = random_email(), random_string()
    driver.get(f"{BASE_URL}/signup")
    
    wait_for(driver, Auth.FULL_NAME_INPUT).send_keys("Empty State User")
    wait_for(driver, Auth.EMAIL_INPUT).send_keys(email)
    wait_for(driver, Auth.PASSWORD_INPUT).send_keys(password)
    wait_for(driver, Auth.CONFIRM_PASSWORD_INPUT).send_keys(password)
    wait_for(driver, Auth.SIGNUP_BUTTON).click()
    import time; time.sleep(1)
    login(driver, email, password)
    wait_for_url_to_be(driver, f"{BASE_URL}/")
    wait_for(driver, Dashboard.WELCOME_TEXT)
    driver.get(f"{BASE_URL}/items")
    
    assert wait_for(driver, Items.EMPTY_STATE).is_displayed()

@pytest.mark.items
def test_edit_item_dialog_opens_with_data(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/items")
    
    item_title = f"Edit Test Item {random_string()}"
    wait_for(driver, Items.ADD_ITEM_BUTTON).click()
    wait_for(driver, General.DIALOG_TITLE)
    wait_for(driver, Items.TITLE_INPUT).send_keys(item_title)
    wait_for(driver, Items.SAVE_BUTTON).click()
    wait_for(driver, General.TOAST_SUCCESS)
    wait_for_toast_to_disappear(driver)
    # Navigate to the last page to find the newly added item
    while True:
        next_button = wait_for(driver, (By.XPATH, "//button[@aria-label='next page']"))
        if not next_button.is_enabled():
            break
        next_button.click()
        wait_for_toast_to_disappear(driver)
    row = wait_for(driver, (By.XPATH, f"//tr[td[contains(text(), '{item_title}')]]"))
    row.find_element(*ACTIONS_MENU_BUTTON_LOCATOR).click()
    wait_for(driver, Items.EDIT_ITEM_BUTTON).click()
    wait_for(driver, General.DIALOG_TITLE)
    assert wait_for(driver, Items.TITLE_INPUT).get_attribute("value") == item_title

@pytest.mark.items
def test_edit_item_successfully(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/items")
    
    item_title = f"Original Title {random_string()}"
    updated_title = f"Updated Title {random_string()}"
    wait_for(driver, Items.ADD_ITEM_BUTTON).click()
    wait_for(driver, General.DIALOG_TITLE)
    wait_for(driver, Items.TITLE_INPUT).send_keys(item_title)
    wait_for(driver, Items.SAVE_BUTTON).click()
    wait_for(driver, General.TOAST_SUCCESS)
    wait_for_toast_to_disappear(driver)
    # Navigate to the last page to find the newly added item
    while True:
        next_button = wait_for(driver, (By.XPATH, "//button[@aria-label='next page']"))
        if not next_button.is_enabled():
            break
        next_button.click()
        wait_for_toast_to_disappear(driver)
    row = wait_for(driver, (By.XPATH, f"//tr[td[contains(text(), '{item_title}')]]"))
    row.find_element(*ACTIONS_MENU_BUTTON_LOCATOR).click()
    wait_for(driver, Items.EDIT_ITEM_BUTTON).click()
    wait_for(driver, General.DIALOG_TITLE)
    title_input = wait_for(driver, Items.TITLE_INPUT)
    title_input.clear()
    title_input.send_keys(updated_title)
    wait_for(driver, Items.SAVE_BUTTON).click()
    wait_for(driver, General.TOAST_SUCCESS)
    wait_for_text(driver, Items.ITEMS_TABLE, updated_title)

@pytest.mark.items
def test_delete_item_confirmation(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/items")
    
    item_title = f"Confirm Delete Item {random_string()}"
    wait_for(driver, Items.ADD_ITEM_BUTTON).click()
    wait_for(driver, General.DIALOG_TITLE)
    wait_for(driver, Items.TITLE_INPUT).send_keys(item_title)
    wait_for(driver, Items.SAVE_BUTTON).click()
    wait_for(driver, General.TOAST_SUCCESS)
    wait_for_toast_to_disappear(driver)
    # Navigate to the last page to find the newly added item
    while True:
        next_button = wait_for(driver, (By.XPATH, "//button[@aria-label='next page']"))
        if not next_button.is_enabled():
            break
        next_button.click()
        wait_for_toast_to_disappear(driver)
    row = wait_for(driver, (By.XPATH, f"//tr[td[contains(text(), '{item_title}')]]"))
    row.find_element(*ACTIONS_MENU_BUTTON_LOCATOR).click()
    wait_for(driver, Items.DELETE_ITEM_BUTTON).click()
    assert "Delete Item" in wait_for(driver, General.DIALOG_TITLE).text

@pytest.mark.items
def test_delete_item_successfully(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/items")
    
    item_title = f"To Be Deleted {random_string()}"
    wait_for(driver, Items.ADD_ITEM_BUTTON).click()
    wait_for(driver, General.DIALOG_TITLE)
    wait_for(driver, Items.TITLE_INPUT).send_keys(item_title)
    wait_for(driver, Items.SAVE_BUTTON).click()
    wait_for(driver, General.TOAST_SUCCESS)
    wait_for_toast_to_disappear(driver)
    # Navigate to the last page to find the newly added item
    while True:
        next_button = wait_for(driver, (By.XPATH, "//button[@aria-label='next page']"))
        if not next_button.is_enabled():
            break
        next_button.click()
        wait_for_toast_to_disappear(driver)
    row = wait_for(driver, (By.XPATH, f"//tr[td[contains(text(), '{item_title}')]]"))
    row.find_element(*ACTIONS_MENU_BUTTON_LOCATOR).click()
    wait_for(driver, Items.DELETE_ITEM_BUTTON).click()
    wait_for(driver, General.DIALOG_TITLE)
    wait_for(driver, Items.CONFIRM_DELETE_BUTTON).click()
    wait_for(driver, General.TOAST_SUCCESS)
    assert wait_for_invisibility(driver, (By.XPATH, f"//tr[td[contains(text(), '{item_title}')]]"))

@pytest.mark.items
def test_items_pagination_appears(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/items")
    # Clean up existing items to ensure a predictable state
    while True:
        try:
            rows = wait_for_all(driver, Items.ITEMS_TABLE_ROW, timeout=2)
            if not rows:
                break
            for row in rows:
                row.find_element(*ACTIONS_MENU_BUTTON_LOCATOR).click()
                wait_for(driver, Items.DELETE_ITEM_BUTTON).click()
                wait_for(driver, General.DIALOG_TITLE)
                wait_for(driver, Items.CONFIRM_DELETE_BUTTON).click()
                wait_for_toast_to_disappear(driver)
        except TimeoutException:
            break

    for i in range(6):
        wait_for(driver, Items.ADD_ITEM_BUTTON).click()
        wait_for(driver, General.DIALOG_TITLE)
        wait_for(driver, Items.TITLE_INPUT).send_keys(f"Pagination Item {i} {random_string()}")
        wait_for(driver, Items.SAVE_BUTTON).click()
        wait_for(driver, General.TOAST_SUCCESS)
        wait_for_toast_to_disappear(driver)
    assert wait_for(driver, (By.XPATH, "//button[text()='2']")).is_displayed()

@pytest.mark.items
def test_items_pagination_navigation(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/items")
    initial_rows = len(driver.find_elements(*Items.ITEMS_TABLE_ROW))
    # Create enough items to ensure pagination
    for i in range(6 - initial_rows):
        wait_for(driver, Items.ADD_ITEM_BUTTON).click()
        wait_for(driver, General.DIALOG_TITLE)
        wait_for(driver, Items.TITLE_INPUT).send_keys(f"Nav Item {i}")
        wait_for(driver, Items.SAVE_BUTTON).click()
        wait_for_toast_to_disappear(driver)

    # Explicitly click the page 2 button to ensure we are on page 2
    try:
        page2_btn = wait_for(driver, (By.XPATH, "//button[@aria-label='page 2']"), timeout=3)
        page2_btn.click()
        wait_for_url_to_be(driver, f"{BASE_URL}/items?page=2")
        prev_btn = wait_for(driver, Items.PAGINATION_PREV_BUTTON, timeout=3)
        assert prev_btn.is_enabled(), "Prev button should be enabled on page 2"
        prev_btn.click()
        print("DEBUG: Current URL after clicking prev:", driver.current_url)
        wait_for_url_to_be(driver, f"{BASE_URL}/items?page=1")
    except Exception as e:
        with open("debug_items_pagination_navigation.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("DEBUG: Saved page source to debug_items_pagination_navigation.html")
        raise

@pytest.mark.items
def test_add_item_dialog_cancel_button(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/items")
    wait_for(driver, Items.ADD_ITEM_BUTTON).click()
    wait_for(driver, General.DIALOG_TITLE)
    wait_for(driver, Items.CANCEL_BUTTON).click()
    assert wait_for_invisibility(driver, General.DIALOG_TITLE)
