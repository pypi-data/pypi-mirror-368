"""
Module for handling RECAPTCHA token generation in Goodgame Empire.

This module defines the `Recaptcha` class, which provides a method for generating a RECAPTCHA token for the game.
"""

from ..base_gge_socket import BaseGgeSocket

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Recaptcha(BaseGgeSocket):
    """
    A class for handling RECAPTCHA token generation in Goodgame Empire.

    This class provides a method for generating a RECAPTCHA token for the game.
    """

    def generate_recaptcha_token(self, quiet: bool = False) -> str | bool:
        """
        Generate a RECAPTCHA token using Selenium.

        Args:
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            None
        
        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--window-size=1,1")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            driver = webdriver.Chrome(options=options)

            driver.get("https://empire.goodgamestudios.com/")
            wait = WebDriverWait(driver, 30, poll_frequency=0.01)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe#game')))
            iframe = driver.find_element(By.CSS_SELECTOR, 'iframe#game')
            driver.switch_to.frame(iframe)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.grecaptcha-badge')))

            result = driver.execute_script("""
                return new Promise((resolve) => {
                    window.grecaptcha.ready(() => {
                        window.grecaptcha.execute('6Lc7w34oAAAAAFKhfmln41m96VQm4MNqEdpCYm-k', { action: 'submit' }).then(resolve);
                    });
                });
            """)

            driver.quit()
            
            return result
        except Exception as e:
            if not quiet:
                raise e
            return False

