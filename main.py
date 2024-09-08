from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv
import os
import time
import requests


load_dotenv()
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
API_URL = os.getenv('API_URL')


def wait_for_countdown_to_finish(driver, timeout=60):
    try:
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located((By.ID, "countdown"))
        )
        print("Countdown finished.")
    except Exception as e:
        print(f"Error waiting for countdown: {e}")

# Set up ChromeDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)
driver.get("https://server.thecoderschool.com/toolset/")

sign_in_link = driver.find_element(By.LINK_TEXT, "sign in")
sign_in_link.click()

email_input = driver.find_element(By.ID, "account_email")
email_input.send_keys(EMAIL)

password_input = driver.find_element(By.ID, "account_password")
password_input.send_keys(PASSWORD)

sign_in_button = driver.find_element(By.XPATH, '//button[@type="submit" and contains(@class, "confirm_button")]')
sign_in_button.click()
allow_access_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@name="authorize" and @value="1"]')))
allow_access_button.click()
northsandiego_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[text()="northsandiego"]')))
northsandiego_button.click()
notes_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.toolbutton')))
notes_button.click()
window_handles = driver.window_handles
driver.switch_to.window(window_handles[-1])


buttons = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'button.notebutton')))
print(f"Found {len(buttons)} buttons.")

for i, button in enumerate(buttons):
    background_color = button.value_of_css_property('background-color')
    print(f"Button {i} background color: {background_color}")

    if background_color == 'rgba(0, 170, 0, 1)':
        print(f"Clicking button {i}...")
        button.click()

        # Switch to the new popup window
        window_handles = driver.window_handles
        driver.switch_to.window(window_handles[-1])
        wait_for_countdown_to_finish(driver)
        # Fill out the notes form
        try:
            iframe = wait.until(EC.presence_of_element_located((By.ID, "note_ifr")))

            driver.switch_to.frame(iframe)

            # Now locate the editable area inside the iframe
            # Note: The actual selector will depend on the structure of the iframe's content
            # For example, you might need to locate a <body> or <div> element inside the iframe
            try:
                editable_area = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
                editable_area.send_keys("Auto-generated notes based on previous data.")
                print("Text input completed.")
            except Exception as e:
                print(f"Error interacting with iframe content: {e}")

            driver.switch_to.default_content()

            # Continue with the rest of your code (e.g., submit the form)
            time.sleep(200)
            submit_button = wait.until(EC.element_to_be_clickable((By.ID, "submit_note_button")))
            #submit_button.click()
            print("Form submitted.")
        except Exception as e:
            print(f"Error filling out form: {e}")

        # Switch back to the original window
        driver.switch_to.window(window_handles[0])
        print("Switched back to the main window.")

        # Optional: Wait before clicking the next button
        time.sleep(2)

    else:
        print(f"Skipping button {i} with background color {background_color}")