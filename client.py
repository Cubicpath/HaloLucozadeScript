##################################################################################################
#                                 MIT Licence (C) 2022 Cubicpath@Github                          #
##################################################################################################
"""Houses Client implementation."""

__all__ = (
    'Client',
    'SITE_URL',
)

# stdlib
import webbrowser
from pathlib import Path
from typing import Any

# 3rd-party
from faker import Faker
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

# local
from constants import *
from utils import *

SITE_URL = 'https://halo.lucozade.com/'


class Client:
    """Handles Selenium logic for the Luzucade Redemption Site"""

    def __init__(self, settings: dict[str, Any], bin_folder: Path | None = None) -> None:
        """Initialize the client."""
        self.bin_folder: Path = Path.cwd() / 'bin' if bin_folder is None else bin_folder
        self.settings: dict[str, Any] = settings

        self.browser: Firefox = Firefox(service=Service(str(bin_folder / EXECUTABLE_NAME)))
        self.browser.set_window_size(settings['window']['x_size'], settings['window']['y_size'])
        self.browser.get(SITE_URL)

    def accept_cookies(self) -> None:
        """Remove cookie popup."""
        WebDriverWait(self.browser, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'block-link')))
        self.browser.find_element(By.CLASS_NAME, 'block-link').click()

    def enter_information(self) -> None:
        """Enter generated information into form."""

        # Generate information
        info = Faker(locale=f'en_{COUNTRY}')
        name:     str = info.first_name()
        email:    str = info.free_email()
        phone:    str = self.settings['info']['phone_number']
        postcode: str = self.settings['info']['postcode']
        store:    str = self.settings['info']['store']

        # Wait until the entire form is loaded
        WebDriverWait(self.browser, 30).until(EC.presence_of_element_located((By.NAME, 'firstName')))
        form = self.browser.find_element(By.CLASS_NAME, 'infx-form-shell')

        # Enter generated information
        form.find_element(By.NAME, 'firstName').send_keys(name)
        form.find_element(By.NAME, 'email').send_keys(email)
        form.find_element(By.NAME, 'confirmEmail').send_keys(email)
        form.find_element(By.NAME, 'mobile').send_keys(phone)
        form.find_element(By.NAME, 'postcode').send_keys(postcode)

        # Wait to make sure select dropdowns are completely loaded
        wait_between(2, 2)

        # Select valid options
        Select(form.find_elements(By.TAG_NAME, 'select')[0]).select_by_value('+44')
        Select(form.find_elements(By.TAG_NAME, 'select')[1]).select_by_value(COUNTRY)
        Select(form.find_elements(By.TAG_NAME, 'select')[2]).select_by_value(store)

        # Check agreement boxes
        form.find_element(By.NAME, 'age').click()
        form.find_element(By.NAME, 'terms').click()

    def submit_form(self) -> None:
        """Submit the information after the captcha."""
        form = self.browser.find_element(By.CLASS_NAME, 'infx-form-shell')

        # Wait until the captcha is solved by the user
        self.browser.switch_to.frame(form.find_elements(By.TAG_NAME, 'iframe')[0])
        WebDriverWait(self.browser, 600).until(EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "You are verified") and @id="recaptcha-accessible-status"]')))
        self.browser.switch_to.default_content()

        wait_between(0.5, 1)

        # Press next button
        buttons = self.browser.find_element(By.CLASS_NAME, 'button-group')
        buttons.find_elements(By.TAG_NAME, 'button')[1].click()

    def input_bar_code(self) -> None:
        """Input bar code."""
        bar_code = self.settings['info']['bar_code']

        # Input bar code
        WebDriverWait(self.browser, 15).until(EC.presence_of_element_located((By.NAME, 'code')))
        form = self.browser.find_element(By.CLASS_NAME, 'infx-form-shell')
        form.find_element(By.NAME, 'code').send_keys(bar_code)

        # Press play button
        buttons = self.browser.find_element(By.CLASS_NAME, 'button-group')
        buttons.find_elements(By.TAG_NAME, 'button')[1].click()

    def collect_reward(self) -> None:
        """Collect reward."""
        WebDriverWait(self.browser, 15).until(EC.presence_of_element_located((By.CLASS_NAME, '__winner-state')))
        self.browser.find_element(By.CLASS_NAME, '__winner-state').click()

        # glitch-one is overwritten by glitch-two, so click on glitch-two
        WebDriverWait(self.browser, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'glitch-one')))
        self.browser.find_element(By.CLASS_NAME, 'glitch-two').click()

        # Press redemption portal button
        WebDriverWait(self.browser, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'button-group')))
        self.browser.find_element(By.CLASS_NAME, 'button-group').find_element(By.TAG_NAME, 'button').click()

    def redeem_codes(self) -> None:
        """Collect redeemed codes."""
        open_redemption_page: bool = self.settings['redeem']['open_redemption_page']
        xp_boost_only:        bool = self.settings['redeem']['xp_boost_only']

        # Ensure the redemption code buttons are fully loaded
        WebDriverWait(self.browser, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'button-group')))
        for i, prize_item in enumerate(self.browser.find_elements(By.CLASS_NAME, 'lz-campaign-xbox-prize-item')):
            # Skip non-xp-boost prize items
            if i == 0 and xp_boost_only:
                continue
            # Print code to log and open the redemption link as a new tab in your native web browser
            try:
                url = prize_item.find_elements(By.CLASS_NAME, 'infx-button')[1].find_element(By.CLASS_NAME, 'block-link').get_attribute('href')
                if 'sign-in' in url:
                    url = url.replace('sign-in?path=/', '')
                    url = url.replace('%3F', '?')
                if open_redemption_page:
                    webbrowser.open(url, new=2, autoraise=False)
                print(url.split('code=')[1])
            except (NoSuchElementException, IndexError):
                pass

    def quit(self) -> None:
        """Quits the browser."""
        if self.browser is not None:
            self.browser.quit()
            self.browser = None
