from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from colorama import Fore, init
import time


def speech_listener(url="https://speechtotext-70a96.web.app/"):
    """
    Continuously listens to speech from the given URL (hosted speech-to-text site)
    and prints the transcribed text in real time.

    Args:
        url (str): The URL of the hosted speech-to-text web app.
    """
    init(autoreset=True)

    # --- Chrome setup ---
    chrome_options = Options()
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    try:
        start_btn = driver.find_element(By.ID, "startButton")
        ActionChains(driver).click(start_btn).perform()
        print(Fore.GREEN + "Listening...\n", end="", flush=True)

        last_text = ""
        while True:
            try:
                text = driver.find_element(By.ID, "output").text.strip()
                if text and text != last_text:
                    print(Fore.LIGHTBLUE_EX + "User:", text)
                    last_text = text
            except Exception:
                pass
            time.sleep(0.5)

    except KeyboardInterrupt:
        print(Fore.RED + "Stopping...", end="", flush=True)
    finally:
        driver.quit()


if __name__ == "__main__":
     speech_listener()
