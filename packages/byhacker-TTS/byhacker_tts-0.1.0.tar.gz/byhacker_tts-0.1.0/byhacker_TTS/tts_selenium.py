from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def speak_text(text):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get("https://texttospeech-a0f55.web.app/")

        textarea = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "text"))
        )
        textarea.clear()
        textarea.send_keys(text)

        speak_button = driver.find_element(By.ID, "button")
        speak_button.click()

        time.sleep(5)  # Wait for speech to process/play
    finally:
        driver.quit()
