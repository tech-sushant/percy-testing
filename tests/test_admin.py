import pytest
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from config import BASE_URL, SUPERUSER_EMAIL, SUPERUSER_PASSWORD
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
from locators import Auth, General, Admin

ACTIONS_MENU_BUTTON_LOCATOR = (By.CSS_SELECTOR, "td:last-child button")

def find_user_row_by_email(driver, email):
    """
    Paginate through all admin user pages and return the row WebElement for the given email.
    Raises AssertionError if not found.
    """
    from selenium.webdriver.common.by import By
    found_row = None
    while True:
        rows = driver.find_elements(*Admin.USERS_TABLE_ROW)
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) > 1 and cells[1].text.strip() == email:
                found_row = row
                break
        if found_row:
            return found_row
        next_button = wait_for(driver, (By.XPATH, "//button[@aria-label='next page']"))
        if not next_button.is_enabled():
            break
        next_button.click()
        wait_for_toast_to_disappear(driver)
    # If not found after paginating all pages
    all_emails = []
    for row in driver.find_elements(*Admin.USERS_TABLE_ROW):
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) > 1:
            all_emails.append(cells[1].text.strip())
    raise AssertionError(
        f"User email not found in table.\n"
        f"EXPECTED EMAIL: {email}\n"
        f"FOUND EMAILS ON FINAL PAGE: {all_emails}\n"
        f"DEBUG PAGE SOURCE:\n{driver.page_source}"
    )

@pytest.mark.admin
def test_admin_page_is_inaccessible_to_regular_user(driver):
    email, password = random_email(), random_string()
    driver.get(f"{BASE_URL}/signup")
    
    wait_for(driver, Auth.FULL_NAME_INPUT).send_keys("Regular User")
    wait_for(driver, Auth.EMAIL_INPUT).send_keys(email)
    wait_for(driver, Auth.PASSWORD_INPUT).send_keys(password)
    wait_for(driver, Auth.CONFIRM_PASSWORD_INPUT).send_keys(password)
    wait_for(driver, Auth.SIGNUP_BUTTON).click()
    print("Current URL after driver.get():", driver.current_url)
    print("Title:", driver.title)
    print("Page Source (short):", driver.page_source[:500]) 
    login(driver, email, password, expect_success=False)

@pytest.mark.admin
def test_admin_page_loads_for_superuser(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/admin")
    
    assert "Users Management" in wait_for(driver, (By.TAG_NAME, "h2")).text
    assert wait_for(driver, Admin.ADD_USER_BUTTON).is_displayed()

@pytest.mark.admin
def test_add_user_dialog_opens_and_closes(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/admin")
    
    wait_for(driver, Admin.ADD_USER_BUTTON).click()
    
    assert "Add User" in wait_for(driver, General.DIALOG_TITLE).text
    wait_for(driver, (By.XPATH, "//div[@role='dialog']//button[text()='Cancel']")).click()
    
    assert wait_for_invisibility(driver, General.DIALOG_TITLE)

@pytest.mark.admin
def test_add_user_successfully(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/admin")
    
    new_user_email = random_email()
    password = random_string()
    wait_for(driver, Admin.ADD_USER_BUTTON).click()
    
    wait_for(driver, General.DIALOG_TITLE)
    wait_for(driver, Auth.EMAIL_INPUT).send_keys(new_user_email)
    wait_for(driver, Auth.PASSWORD_INPUT).send_keys(password)
    wait_for(driver, Auth.CONFIRM_PASSWORD_INPUT).send_keys(password)
    wait_for(driver, Admin.SAVE_BUTTON).click()
    
    wait_for(driver, General.TOAST_SUCCESS)
    while True:
        next_button = wait_for(driver, (By.XPATH, "//button[@aria-label='next page']"))
        if not next_button.is_enabled():
            break
        next_button.click()
        wait_for_toast_to_disappear(driver)
    # Manually check all rows for the email
    rows = driver.find_elements(*Admin.USERS_TABLE_ROW)
    found_emails = []
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) > 1:
            found_emails.append(cells[1].text.strip())
    assert new_user_email in found_emails, (
        f"User email not found in table.\n"
        f"EXPECTED EMAIL: {new_user_email}\n"
        f"FOUND EMAILS ON FINAL PAGE: {found_emails}\n"
        f"DEBUG PAGE SOURCE:\n{driver.page_source}"
    )

@pytest.mark.admin
def test_add_superuser_successfully(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/admin")
    
    new_superuser_email = random_email()
    password = random_string()
    wait_for(driver, Admin.ADD_USER_BUTTON).click()
    
    wait_for(driver, General.DIALOG_TITLE)
    wait_for(driver, Auth.EMAIL_INPUT).send_keys(new_superuser_email)
    wait_for(driver, Auth.PASSWORD_INPUT).send_keys(password)
    wait_for(driver, Auth.CONFIRM_PASSWORD_INPUT).send_keys(password)
    wait_for(driver, Admin.IS_SUPERUSER_CHECKBOX).click()
    wait_for(driver, Admin.SAVE_BUTTON).click()
    
    wait_for(driver, General.TOAST_SUCCESS)
    wait_for_toast_to_disappear(driver)
    # Paginate through all pages and collect emails
    import time
    found_emails = []
    page_num = 1
    while True:
        print(f"DEBUG: On page {page_num}")
        rows = driver.find_elements(*Admin.USERS_TABLE_ROW)
        page_emails = []
        for row in rows:
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) > 1:
                    email = cells[1].text.strip()
                    found_emails.append(email)
                    page_emails.append(email)
            except Exception as e:
                print(f"DEBUG: Exception for row: {e}")
        print(f"DEBUG: Emails found on page {page_num}: {page_emails}")
        next_button = wait_for(driver, (By.XPATH, "//button[@aria-label='next page']"))
        if not next_button.is_enabled():
            break
        next_button.click()
        wait_for_toast_to_disappear(driver)
        time.sleep(0.5)
        page_num += 1
    print(f"DEBUG: All emails found: {found_emails}")
    print(f"DEBUG: EXPECTED EMAIL: {new_superuser_email}")
    assert new_superuser_email in found_emails, (
        f"Superuser email not found in table.\n"
        f"EXPECTED EMAIL: {new_superuser_email}\n"
        f"FOUND EMAILS IN ALL PAGES: {found_emails}\n"
        f"DEBUG PAGE SOURCE:\n{driver.page_source}"
    )

@pytest.mark.admin
def test_add_user_with_existing_email(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/admin")
    
    password = random_string()
    wait_for(driver, Admin.ADD_USER_BUTTON).click()
    
    wait_for(driver, General.DIALOG_TITLE)
    wait_for(driver, Auth.EMAIL_INPUT).send_keys(SUPERUSER_EMAIL)
    wait_for(driver, Auth.PASSWORD_INPUT).send_keys(password)
    wait_for(driver, Auth.CONFIRM_PASSWORD_INPUT).send_keys(password)
    wait_for(driver, Admin.SAVE_BUTTON).click()
    
    wait_for(driver, General.TOAST_ERROR_TITLE)
    wait_for_text(driver, General.TOAST_ERROR_DESCRIPTION, "already exists")

@pytest.mark.admin
def test_edit_user_dialog_opens(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/admin")
    
    rows = wait_for_all(driver, Admin.USERS_TABLE_ROW)
    target_row = next(row for row in rows if SUPERUSER_EMAIL not in row.text)
    target_row.find_element(*ACTIONS_MENU_BUTTON_LOCATOR).click()
    wait_for(driver, Admin.EDIT_USER_BUTTON).click()
    
    assert "Edit User" in wait_for(driver, General.DIALOG_TITLE).text

@pytest.mark.admin
def test_edit_user_details_successfully(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/admin")
    
    new_user_email = random_email()
    new_full_name = "New User to Edit"
    password = random_string()
    wait_for(driver, Admin.ADD_USER_BUTTON).click()
    
    wait_for(driver, General.DIALOG_TITLE)
    wait_for(driver, Auth.EMAIL_INPUT).send_keys(new_user_email)
    try:
        wait_for(driver, Auth.FULL_NAME_INPUT).send_keys("Initial Name")
    except TimeoutException:
        print("DEBUG: FULL_NAME_INPUT not found. Page source:\n", driver.page_source)
        raise
    wait_for(driver, Auth.PASSWORD_INPUT).send_keys(password)
    wait_for(driver, Auth.CONFIRM_PASSWORD_INPUT).send_keys(password)
    wait_for(driver, Admin.SAVE_BUTTON).click()
    
    wait_for(driver, General.TOAST_SUCCESS)
    wait_for_toast_to_disappear(driver)
    row = find_user_row_by_email(driver, new_user_email)
    row.find_element(*ACTIONS_MENU_BUTTON_LOCATOR).click()
    wait_for(driver, Admin.EDIT_USER_BUTTON).click()
    
    wait_for(driver, General.DIALOG_TITLE)
    name_input = wait_for(driver, Auth.FULL_NAME_INPUT)
    name_input.clear()
    name_input.send_keys(new_full_name)
    wait_for(driver, Admin.SAVE_BUTTON).click()
    
    wait_for(driver, General.TOAST_SUCCESS)
    wait_for_text(driver, (By.TAG_NAME, "body"), new_full_name)

@pytest.mark.admin
def test_delete_user_successfully(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/admin")
    
    email_to_delete = random_email()
    password = random_string()
    wait_for(driver, Admin.ADD_USER_BUTTON).click()
    
    wait_for(driver, General.DIALOG_TITLE)
    wait_for(driver, Auth.EMAIL_INPUT).send_keys(email_to_delete)
    wait_for(driver, Auth.PASSWORD_INPUT).send_keys(password)
    wait_for(driver, Auth.CONFIRM_PASSWORD_INPUT).send_keys(password)
    wait_for(driver, Admin.SAVE_BUTTON).click()
    
    wait_for(driver, General.TOAST_SUCCESS)
    wait_for_toast_to_disappear(driver)
    row = find_user_row_by_email(driver, email_to_delete)
    row.find_element(*ACTIONS_MENU_BUTTON_LOCATOR).click()
    wait_for(driver, Admin.DELETE_USER_BUTTON).click()
    
    wait_for(driver, General.DIALOG_TITLE)
    wait_for(driver, (By.XPATH, "//div[@role='alertdialog']//button[normalize-space()='Delete']")).click()
    
    wait_for(driver, General.TOAST_SUCCESS)
    # Optionally, verify the user is no longer present
    try:
        find_user_row_by_email(driver, email_to_delete)
        assert False, f"User {email_to_delete} still found after deletion."
    except AssertionError:
        pass

@pytest.mark.admin
def test_users_list_is_paginated(driver):
    login_as_superuser(driver)
    driver.get(f"{BASE_URL}/admin")
    
    initial_rows = len(driver.find_elements(*Admin.USERS_TABLE_ROW))
    # Create enough users to ensure pagination
    for i in range(6 - initial_rows):
        email, password = random_email(), random_string()
        wait_for(driver, Admin.ADD_USER_BUTTON).click()
        
        wait_for(driver, General.DIALOG_TITLE)
        wait_for(driver, Auth.EMAIL_INPUT).send_keys(email)
        wait_for(driver, Auth.PASSWORD_INPUT).send_keys(password)
        wait_for(driver, Auth.CONFIRM_PASSWORD_INPUT).send_keys(password)
        wait_for(driver, Admin.SAVE_BUTTON).click()
        
        wait_for(driver, General.TOAST_SUCCESS)
        wait_for_toast_to_disappear(driver)
    assert wait_for(driver, (By.XPATH, "//button[text()='2']")).is_displayed()
    
@pytest.mark.admin
def test_add_user_button_is_visible_for_superuser(driver):
    """Checks that the 'Add User' button is visible for a logged-in superuser."""
    # 1. Log in as a superuser
    login_as_superuser(driver)
    
    # 2. Navigate to the admin page
    driver.get(f"{BASE_URL}/admin")
    
    # 3. Find the 'Add User' button and assert it is displayed
    add_user_button = wait_for(driver, Admin.ADD_USER_BUTTON)
    assert add_user_button.is_displayed()
