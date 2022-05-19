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
from collections import namedtuple
from pathlib import Path
from typing import Any

# 3rd-party
from faker import Faker
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome
from selenium.webdriver import Edge
from selenium.webdriver import Firefox
from selenium.webdriver import Opera
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.options import ArgOptions
from selenium.webdriver.common.service import Service
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.manager import DriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.opera import OperaDriverManager

# local
from utils import *

SITE_URL = 'https://halo.lucozade.com/'


class Client:
    """Handles Selenium logic for the Lucozade Redemption Site"""
    _driver_path: str | None = None
    DriverFactory = namedtuple(
        'Factory', ('manager_type', 'driver_type', 'options_type', 'service_type'),
        defaults=(DriverManager, RemoteWebDriver, ArgOptions, None)
    )

    def __init__(self, browser: str, settings: dict[str, Any]) -> None:
        """Initialize the client."""
        self.settings: dict[str, Any] = settings
        x_size: int = self.settings['browser']['x_size']
        y_size: int = self.settings['browser']['y_size']

        self.browser: RemoteWebDriver = self.build_browser_driver(browser)
        self.browser.set_window_size(x_size, y_size)
        self.browser.get(SITE_URL)

    @classmethod
    def build_browser_driver(cls, browser: str, install_only: bool = False) -> RemoteWebDriver | None:
        """Builds a browser."""

        # Create a factory for building the selected driver.
        match browser:
            case 'firefox':
                factory = cls.DriverFactory(GeckoDriverManager, Firefox, FirefoxOptions, FirefoxService)
            case 'chrome':
                factory = cls.DriverFactory(ChromeDriverManager, Chrome, ChromeOptions, ChromeService)
            case 'edge':
                factory = cls.DriverFactory(EdgeChromiumDriverManager, Edge, EdgeOptions, EdgeService)
            case 'opera':
                factory = cls.DriverFactory(OperaDriverManager, Opera, ChromiumOptions, None)
            case _:
                raise ValueError(f'Invalid browser name: "{browser}". Please choose "firefox", "chrome", "edge", or "opera".')

        # Build the browser manager (installs the driver & caches result path)
        if cls._driver_path is None:
            manager: DriverManager = factory.manager_type()
            cls._driver_path = manager.install()

        # Designates the log file name as ./logs/[driver_name].log
        log_path: Path = Path.cwd() / f'logs/{Path(cls._driver_path).with_suffix("").name}.log'

        # Create the logs folder if required
        if not log_path.parent.is_dir():
            log_path.parent.mkdir(parents=True)

        # Return early to avoid creating a new browser if we're only installing the driver
        if install_only:
            return None

        # Create the browser options
        options = factory.options_type()
        if issubclass(factory.options_type, ChromiumOptions):
            # Disable logging for Chromium-based browsers to eliminate noisy output in the console
            options.add_argument('--disable-logging')
            options.add_argument('--log-level=3')
            options.add_experimental_option('excludeSwitches', ['enable-logging'])

        # Build the browser driver object
        if factory.service_type is not None:
            service: Service = factory.service_type(executable_path=cls._driver_path, log_path=log_path)
            driver = factory.driver_type(service=service, options=options)
        else:
            driver = factory.driver_type(executable_path=cls._driver_path, service_log_path=log_path, options=options)

        return driver

    def accept_cookies(self) -> None:
        """Remove cookie popup."""
        WebDriverWait(self.browser, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'block-link')))
        self.browser.find_element(By.CLASS_NAME, 'block-link').click()

    def enter_information(self) -> None:
        """Enter generated information into form."""

        # Generate information
        country_code: str = self.settings['info']['country_code']
        info:         Faker = Faker(locale=f'en_{country_code}')
        name:         str = info.first_name()
        email:        str = info.free_email()
        phone:        str = self.settings['info']['phone_number']
        postcode:     str = self.settings['info']['postcode']
        store:        str = self.settings['info']['store']

        # Wait for main form to load
        WebDriverWait(self.browser, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'infx-form-shell')))
        form = self.browser.find_element(By.CLASS_NAME, 'infx-form-shell')

        # Enter generated information
        form.find_element(By.NAME, 'firstName').send_keys(name)
        form.find_element(By.NAME, 'email').send_keys(email)
        form.find_element(By.NAME, 'confirmEmail').send_keys(email)
        form.find_element(By.NAME, 'mobile').send_keys(phone)
        form.find_element(By.NAME, 'postcode').send_keys(postcode)

        # Select valid options
        WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.XPATH, f'//option[contains(text(), "{store}")]')))
        Select(form.find_elements(By.TAG_NAME, 'select')[0]).select_by_value('+44')
        Select(form.find_elements(By.TAG_NAME, 'select')[1]).select_by_value(country_code)
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
