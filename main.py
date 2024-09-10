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
        # print("Countdown finished.")
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
driver.close()
window_handles = driver.window_handles
driver.switch_to.window(window_handles[-1])


buttons = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'button.notebutton')))
# print(f"Found {len(buttons)} buttons.")

for i, button in enumerate(buttons):
    background_color = button.value_of_css_property('background-color')
    # print(f"Button {i} background color: {background_color}")

    if background_color == 'rgba(0, 170, 0, 1)':
        # print(f"Clicking button {i}...")
        button.click()

        window_handles = driver.window_handles
        driver.switch_to.window(window_handles[-1])
        wait_for_countdown_to_finish(driver)
        student_name_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.cdiv > div:nth-child(1) > span')))
        student_name = student_name_element.text.strip()
        # print(f"CSS Selected Student Name: {student_name}")
        # student_name_element = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div[1]/span')))
        # student_name = student_name_element.text
        # print(f"XPath Selected Student Name: {student_name}")


        driver.execute_script("window.open('https://server.thecoderschool.com/portal/portalsearch.php', '_blank');")
        window_handles = driver.window_handles
        driver.switch_to.window(window_handles[-1])

        search_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div#studentdiv input#student')))
        search_input.send_keys(student_name)

        search_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/form/div/div/p/button')))
        driver.execute_script("document.querySelector('li').style.display = 'none';")
        search_button.click()

        student_page_link = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div[2]/div[1]/div[2]')))
        # print("click student page link")
        student_page_link.click()

        driver.close()

        window_handles = driver.window_handles
        driver.switch_to.window(window_handles[-1])
        concepts = wait.until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/table/tbody/tr[2]/td/p[1]'))).text
        previous_note = wait.until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/table/tbody/tr[2]/td/p[2]'))).text

        # Print or use the extracted information
        # print("Concepts:", concepts)
        # print("Previous Note:", previous_note)
        response_note = requests.post(API_URL, json={"student_name":student_name, "previous_note": previous_note, "concepts": concepts})
        note = response_note.json()
        # print(note)
        driver.close()
        window_handles = driver.window_handles
        driver.switch_to.window(window_handles[-1])

        working_concepts_part = concepts.split("Working Concepts:")[1].split("Session Notes:")[0].strip()

        concepts_list = [concept.strip() for concept in working_concepts_part.split(",")]

        for concept in concepts_list:
            try:
                add_concept_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="addconcept"]')))
                add_concept_input.clear()
                add_concept_input.send_keys(concept)

                button = driver.find_element(By.CLASS_NAME, 'gobutton')
                button.click()
            except Exception as e:
                print(e)
        # Fill out the notes form
        try:
            iframe = wait.until(EC.presence_of_element_located((By.ID, "note_ifr")))
            driver.switch_to.frame(iframe)
            try:
                editable_area = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body > p")))
                # editable_area.send_keys(note)
                driver.execute_script(f"document.querySelector('body > p').innerText = \"{note}\";")
                # print("Text input completed.")
            except Exception as e:
                print(f"Error interacting with iframe content: {e}")

            driver.switch_to.default_content()
            dropdown_menu = wait.until(EC.element_to_be_clickable((By.ID, 'studentinterest')))
            dropdown_menu.click()
            option = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'option[value="green"]')))
            option.click()

            submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"].gobutton')))
            # submit_button.click()
            time.sleep(30)
            driver.close()
            # print("Form submitted.")
        except Exception as e:
            print(f"Error filling out form: {e}")

        driver.switch_to.window(window_handles[0])
        # print("Switched back to the main window.")
        time.sleep(2)

    else:
        print(f"Skipping button {i} with background color {background_color}")