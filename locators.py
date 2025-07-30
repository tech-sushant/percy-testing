from selenium.webdriver.common.by import By

class Auth:
    EMAIL_INPUT = (By.CSS_SELECTOR, 'input[placeholder="Email"]')
    EMAIL_INPUT_OTHER = (By.NAME, 'email')
    PASSWORD_INPUT = (By.CSS_SELECTOR, 'input[placeholder="Password"]')
    CONFIRM_PASSWORD_INPUT = (By.NAME, 'confirm_password')
    FULL_NAME_INPUT = (By.NAME, "full_name")
    NEW_PASSWORD_INPUT = (By.CSS_SELECTOR, 'input[placeholder="New Password"]')
    CURRENT_PASSWORD_INPUT = (By.CSS_SELECTOR, 'input[placeholder="Current Password"]')
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Log In']")
    SIGNUP_BUTTON = (By.XPATH, "//button[normalize-space()='Sign Up']")
    FORGOT_PASSWORD_LINK = (By.LINK_TEXT, "Forgot Password?")
    SIGNUP_LINK = (By.LINK_TEXT, "Sign Up")
    LOGIN_LINK = (By.LINK_TEXT, "Log In")

class General:
    TOAST_SUCCESS = (By.XPATH, "//*[contains(text(), 'Success!')]")
    TOAST_ERROR_TITLE = (By.XPATH, "//*[contains(text(), 'Something went wrong!')]")
    TOAST_ERROR_DESCRIPTION = (By.CSS_SELECTOR, "[data-part='description']")
    DIALOG_TITLE = (By.CSS_SELECTOR, "[data-part='title']")

class Navbar:
    USER_MENU = (By.CSS_SELECTOR, '[data-testid="user-menu"]')
    LOGOUT_BUTTON = (By.XPATH, "//div[contains(text(), 'Log Out')]")

class Dashboard:
    WELCOME_TEXT = (By.XPATH, "//*[contains(text(), 'Welcome back')]")

class Settings:
    MY_PROFILE_TAB = (By.XPATH, "//button[text()='My profile']")
    PASSWORD_TAB = (By.XPATH, "//button[text()='Password']")
    APPEARANCE_TAB = (By.XPATH, "//button[text()='Appearance']")
    DANGER_ZONE_TAB = (By.XPATH, "//button[text()='Danger zone']")
    EDIT_BUTTON = (By.XPATH, "//button[text()='Edit']")
    SAVE_BUTTON = (By.XPATH, "//button[text()='Save']")
    CANCEL_BUTTON = (By.XPATH, "//button[text()='Cancel']")
    LIGHT_MODE_RADIO = (By.XPATH, "//span[text()='Light Mode']")
    DARK_MODE_RADIO = (By.XPATH, "//span[text()='Dark Mode']")
    DELETE_ACCOUNT_BUTTON = (By.XPATH, "//button[text()='Delete']")
    CONFIRM_DELETE_BUTTON = (By.XPATH, "//div[@role='alertdialog']//button[normalize-space()='Delete']")

class Items:
    ADD_ITEM_BUTTON = (By.XPATH, "//button[contains(text(), 'Add Item')]")
    SAVE_BUTTON = (By.XPATH, "//div[@role='dialog']//button[normalize-space()='Save']")
    CANCEL_BUTTON = (By.XPATH, "//div[@role='dialog']//button[normalize-space()='Cancel']")
    TITLE_INPUT = (By.CSS_SELECTOR, "input#title")
    DESCRIPTION_INPUT = (By.CSS_SELECTOR, "input#description")
    ITEMS_TABLE = (By.TAG_NAME, "tbody")
    ITEMS_TABLE_ROW = (By.CSS_SELECTOR, "tbody > tr")
    EMPTY_STATE = (By.XPATH, "//*[contains(text(), \"don't have any items yet\")]")
    ACTIONS_MENU_BUTTON = (By.CSS_SELECTOR, "button[aria-label='Open menu']")
    EDIT_ITEM_BUTTON = (By.XPATH, "//button[contains(text(), 'Edit Item')]")
    DELETE_ITEM_BUTTON = (By.XPATH, "//button[contains(text(), 'Delete Item')]")
    CONFIRM_DELETE_BUTTON = (By.XPATH, "//div[@role='alertdialog']//button[normalize-space()='Delete']")
    PAGINATION_PREV_BUTTON = (By.XPATH, "//button[contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'prev')]")

class Admin:
    ADMIN_LINK = (By.XPATH, "//a[@href='/admin']")
    ADD_USER_BUTTON = (By.XPATH, "//button[contains(text(), 'Add User')]")
    SAVE_BUTTON = (By.XPATH, "//div[@role='dialog']//button[normalize-space()='Save']")
    USERS_TABLE_ROW = (By.CSS_SELECTOR, "tbody > tr")
    IS_SUPERUSER_CHECKBOX = (By.XPATH, "//span[text()='Is superuser?']")
    IS_ACTIVE_CHECKBOX = (By.XPATH, "//span[text()='Is active?']")
    EDIT_USER_BUTTON = (By.XPATH, "//button[contains(text(), 'Edit User')]")
    DELETE_USER_BUTTON = (By.XPATH, "//button[contains(text(), 'Delete User')]")
