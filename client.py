##################################################################################################
#                                 MIT Licence (C) 2022 Cubicpath@Github                          #
##################################################################################################
"""Houses Client implementation."""

__all__ = (
    'Client',
    'ClientSession',
    'DropMailClient',
    'SITE_URL',
)

# stdlib
import webbrowser
from collections import namedtuple
from datetime import datetime
from pathlib import Path
from typing import Any
from warnings import warn

# 3rd-party
from faker import Faker
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver import Edge
from selenium.webdriver import Firefox
from selenium.webdriver import Opera
from selenium.webdriver import Safari
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.options import ArgOptions
from selenium.webdriver.common.service import Service
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.opera.options import Options as OperaOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.safari.service import Service as SafariService
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
from utils import wait

SITE_URL = 'https://halo.lucozade.com/'

DriverFactory = namedtuple(
    'DriverFactory', ('manager_type', 'driver_type', 'options_type', 'service_type'),
    defaults=(DriverManager, RemoteWebDriver, ArgOptions, Service)
)


class ClientSession:
    """Session for managing configurations of multiple :py:class:`Client` instances."""

    def __init__(self, browser: str, settings: dict[str, Any]) -> None:
        self.browser_name:           str = browser
        self.driver_path:            str | None = None
        self.email_client:           DropMailClient | None = None
        self.settings:               dict[str, Any] = settings
        self.skip_proof_of_purchase: bool = False

        self.build_browser_driver(install_only=True)

    def build_email_client(self) -> None:
        """Builds the email client."""
        self.email_client = DropMailClient(self)
        self.email_client.create()

    def build_browser_driver(self, *, headless: bool = False, install_only: bool = False) -> RemoteWebDriver | None:
        """Builds a browser."""
        log_dir: Path = Path.cwd() / 'logs'

        # Create a factory for building the selected driver.
        match self.browser_name:
            case 'firefox':
                factory = DriverFactory(GeckoDriverManager, Firefox, FirefoxOptions, FirefoxService)
            case 'chrome':
                factory = DriverFactory(ChromeDriverManager, Chrome, ChromeOptions, ChromeService)
            case 'edge':
                factory = DriverFactory(EdgeChromiumDriverManager, Edge, EdgeOptions, EdgeService)
            case 'opera':
                factory = DriverFactory(OperaDriverManager, Opera, OperaOptions, None)
            case 'safari':
                factory = DriverFactory(None, Safari, SafariOptions, SafariService)
            case _:
                raise ValueError(f'Invalid browser name: "{self.browser_name}". Please choose "firefox", "chrome", "edge", "opera", "safari".')

        # Build the browser manager (installs the driver & caches result path)
        if self.driver_path is None and factory.manager_type is not None:
            manager: DriverManager = factory.manager_type()
            self.driver_path = str(Path(manager.install()).resolve(strict=True))

        # Return early to avoid creating a new browser if we're only installing the driver
        if install_only:
            return None

        proxy_ip:      str = self.settings['browser']['proxy']['ip'].strip()
        proxy_port:    int = self.settings['browser']['proxy']['port']
        is_socks:      bool = self.settings['browser']['proxy']['is_socks']
        socks_version: int = self.settings['browser']['proxy']['socks_version']
        is_proxy_set:  bool = bool(proxy_ip and proxy_port)

        # Create the browser options
        options = factory.options_type()

        if isinstance(options, ChromiumOptions):
            # Disable logging for Chromium-based browsers to eliminate noisy output in the console
            options.headless = headless
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-logging')
            options.add_argument('--log-level=3')
            options.add_experimental_option('useAutomationExtension', False)
            options.add_experimental_option('excludeSwitches', ['enable-logging'])

            # Add proxy server for Chromium-based browsers
            if is_proxy_set:  # Check if both are set
                options.add_argument(
                    f'--proxy-server='
                    f'socks{socks_version}://' if is_socks else ''
                    f'{proxy_ip}:{proxy_port}'
                )

        if isinstance(options, FirefoxOptions):
            # Add proxy server for Firefox-based browsers
            options.headless = headless
            if is_proxy_set:
                options.set_preference('network.proxy.type', 1)
                options.set_preference('network.proxy.http', proxy_ip)
                options.set_preference('network.proxy.http_port', proxy_port)
                options.set_preference('network.proxy.ssl', proxy_ip)
                options.set_preference('network.proxy.ssl_port', proxy_port)
                if is_socks:
                    options.set_preference('network.proxy.socks', proxy_ip)
                    options.set_preference('network.proxy.socks_port', proxy_port)
                    options.set_preference('network.proxy.socks_version', socks_version)

        # Build the browser driver object
        match factory.driver_type.__mro__:
            # case Opera.__mro__:
            #     driver = factory.driver_type(
            #         service=factory.service_type(),
            #         options=options
            #     )
            case Safari.__mro__:
                driver = factory.driver_type(
                    service=factory.service_type(),
                    options=options
                )
            case _:
                # Designates the log file name as ./logs/[driver_name].log
                log_path: Path = log_dir / Path(self.driver_path).with_suffix(".log").name

                if factory.service_type is not None:
                    service: Service = factory.service_type(executable_path=self.driver_path, log_path=log_path)
                    driver = factory.driver_type(
                        service=service,
                        options=options
                    )
                else:
                    driver = factory.driver_type(
                        executable_path=self.driver_path,
                        service_log_path=log_path,
                        options=options
                    )

        return driver


class Client:
    """Handles Selenium logic for the Lucozade Redemption Site"""

    def __init__(self, session: ClientSession) -> None:
        """Initialize the client."""
        self.session:  ClientSession = session
        x_size: int = session.settings['browser']['x_size']
        y_size: int = session.settings['browser']['y_size']

        # Disable automation for the proof of purchase section (barcode / dropdowns)
        if not session.skip_proof_of_purchase:
            session.skip_proof_of_purchase = session.settings['redeem']['skip_proof_of_purchase']

        self.browser: RemoteWebDriver = self.session.build_browser_driver()
        self.browser.set_window_size(x_size, y_size)
        self.browser.get(SITE_URL)

    def accept_cookies(self) -> None:
        """Remove cookie popup."""
        WebDriverWait(self.browser, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'block-link')))
        self.browser.find_element(By.CLASS_NAME, 'block-link').click()

    def enter_information(self) -> None:
        """Enter generated information into form."""

        # Generate information
        # Northern Ireland is not supported by Faker, so GB is now hardcoded
        country_code: str = self.session.settings['info']['country_code']
        info:         Faker = Faker(locale='en_GB')
        name:         str = info.first_name()
        email:        str = self.session.email_client.get_address()
        phone:        str = self.session.settings['info']['phone_number']
        postcode:     str = self.session.settings['info']['postcode']
        store:        str = self.session.settings['info']['store']

        # Wait for main form to load
        WebDriverWait(self.browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'infx-form-shell')))
        form = self.browser.find_element(By.CLASS_NAME, 'infx-form-shell')

        # Enter generated information
        form.find_element(By.NAME, 'firstName').send_keys(name)
        form.find_element(By.NAME, 'email').send_keys(email)
        form.find_element(By.NAME, 'confirmEmail').send_keys(email)
        form.find_element(By.NAME, 'mobile').send_keys(phone)
        form.find_element(By.NAME, 'postcode').send_keys(postcode)

        # Select valid options
        WebDriverWait(self.browser, 5).until(EC.presence_of_element_located(
            (By.XPATH, f'//option[contains(text(), "{store}")]')
        ))
        Select(form.find_elements(By.TAG_NAME, 'select')[0]).select_by_value('+44')
        Select(form.find_elements(By.TAG_NAME, 'select')[1]).select_by_value(country_code)
        Select(form.find_elements(By.TAG_NAME, 'select')[2]).select_by_value(store)

        # Check agreement boxes
        form.find_element(By.NAME, 'age').click()
        form.find_element(By.NAME, 'terms').click()

    def submit_form(self) -> None:
        """Submit the information after the captcha."""
        form = self.browser.find_element(By.CLASS_NAME, 'infx-form-shell')

        # Scroll to captcha
        self.browser.execute_script("arguments[0].scrollIntoView();", form.find_element(By.TAG_NAME, 'iframe'))

        # Wait until the captcha is solved by the user
        self.browser.switch_to.frame(form.find_elements(By.TAG_NAME, 'iframe')[0])
        WebDriverWait(self.browser, 600).until(EC.presence_of_element_located(
            (By.XPATH, '//div[contains(text(), "You are verified") and @id="recaptcha-accessible-status"]')
        ))
        self.browser.switch_to.default_content()

        # Wait for animation to complete
        wait(0.5)

        # Press next button
        buttons = self.browser.find_element(By.CLASS_NAME, 'button-group')
        buttons.find_elements(By.TAG_NAME, 'button')[1].click()

    def verify_email(self):
        """Get the latest email from the session email client and input the verification code."""
        # Wait until popup is visible
        WebDriverWait(self.browser, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'pop-over-interface-inner')))

        popup = self.browser.find_element(By.CLASS_NAME, 'pop-over-interface-inner')
        buttons = popup.find_element(By.CLASS_NAME, 'button-group').find_elements(By.TAG_NAME, 'button')

        verification_code: str = ''

        # Every 2 seconds check if the email has been sent, and if not five times in a row, resend the email.
        # Do this 3 times
        do_break = False
        for _ in range(3):
            for _ in range(5):
                emails = self.session.email_client.get_emails()
                if emails:
                    try:
                        # Get the latest email's text and parse for the verification code.
                        verification_code = emails[0][0].split(' - ')[1].strip()
                    except IndexError:
                        continue
                    else:
                        # If found, escape all loops
                        do_break = True
                if do_break:
                    break
                wait(1, 2)
            if do_break:
                break
            # Click resend button
            buttons[1].click()

        if not verification_code:
            exit(100)

        # Get the verification code from the email contents and press verify
        text_box = popup.find_element(By.CSS_SELECTOR, 'input.textbox')
        text_box.click()
        text_box.send_keys(verification_code)
        buttons[0].click()

    def input_bar_code(self) -> None:
        """Input bar code."""
        warn('Bar code input should not be used, instead use input_dropdown_checks()', DeprecationWarning)

        bar_code = self.session.settings['info']['bar_code']

        # Input bar code
        WebDriverWait(self.browser, 15).until(EC.presence_of_element_located((By.NAME, 'code')))
        form = self.browser.find_element(By.CLASS_NAME, 'infx-form-shell')
        form.find_element(By.NAME, 'code').send_keys(bar_code)

        # Press play button
        buttons = self.browser.find_element(By.CLASS_NAME, 'button-group')
        buttons.find_elements(By.TAG_NAME, 'button')[1].click()

    def input_dropdown_checks(self) -> None:
        """Input dropdown checks."""
        if self.session.skip_proof_of_purchase:
            return

        try:
            WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(
                (By.XPATH, '//option[contains(text(), "22")]')
            ))
        except TimeoutException as e:
            # The dropdowns are not loaded, check if we are passed this point.
            if self.browser.find_element(By.CLASS_NAME, 'lz-campaign-xbox-container').get_attribute('data-step') != 'proof-of-purchase':
                # If we are, assume we will be in other client instances as well.
                self.__class__._skip_proof_of_purchase = True
                return
            else:
                raise e from e

        # Input dropdown values
        dropdowns = self.browser.find_elements(By.TAG_NAME, 'select')
        Select(dropdowns[0]).select_by_value('22')
        Select(dropdowns[1]).select_by_value('19:00')

        # Press play button
        buttons = self.browser.find_element(By.CLASS_NAME, 'button-group')
        buttons.find_elements(By.TAG_NAME, 'button')[1].click()

    def collect_reward(self) -> None:
        """Collect reward."""
        WebDriverWait(self.browser, 15).until(EC.presence_of_element_located((By.CLASS_NAME, '__winner-state')))
        self.browser.find_element(By.CLASS_NAME, '__winner-state').click()

        # glitch-one is overwritten by lz-campaign-galaxy-container, so click using JavaScript
        WebDriverWait(self.browser, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'glitch-one')))
        self.browser.execute_script("arguments[0].click();", self.browser.find_element(By.CLASS_NAME, 'lz-campaign-xbox-winner'))

        # Press redemption portal button
        WebDriverWait(self.browser, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'button-group')))
        self.browser.find_element(By.CLASS_NAME, 'button-group').find_element(By.TAG_NAME, 'button').click()

    def redeem_codes(self) -> None:
        """Collect redeemed codes."""
        open_redemption_page: bool = self.session.settings['redeem']['open_redemption_page']
        xp_boost_only:        bool = self.session.settings['redeem']['xp_boost_only']

        # Ensure the redemption code buttons are fully loaded
        WebDriverWait(self.browser, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'button-group')))
        for prize_item in self.browser.find_elements(By.CLASS_NAME, 'lz-campaign-xbox-prize-item'):
            prize_code = prize_item.find_element(By.CLASS_NAME, 'lz-campaign-xbox-prize-code').text
            prize_type = prize_item.find_element(By.CLASS_NAME, 'lz-campaign-xbox-prize-type').text.split(' ')[-1]

            # Skip non-xp-boost prize items
            if prize_type != '2XP' and xp_boost_only:
                continue

            # Print code to log and open the redemption link as a new tab in your native web browser
            redemption_url = f'https://www.halowaypoint.com/redeem?code={prize_code}'
            if open_redemption_page:
                webbrowser.open(redemption_url, new=2, autoraise=False)

            if xp_boost_only:
                print(f'{prize_code}')
            else:
                print(f'{(prize_type + ":").ljust(16)} {prize_code}')

    def quit(self) -> None:
        """Quits the browser."""
        if self.browser is not None:
            self.browser.quit()
            self.browser = None


class DropMailClient:
    """Handles Selenium logic for https://dropmail.me/en/"""

    def __init__(self, session: ClientSession) -> None:
        self.session: ClientSession = session
        self.browser: RemoteWebDriver | None = None

    def create(self) -> None:
        """Login to 10 minutes email."""
        headless = not self.session.settings['browser']['email']['visible']
        self.browser = self.session.build_browser_driver(headless=headless)
        self.browser.get('https://dropmail.me/en/')

    def get_address(self) -> str:
        """Get the current email address."""
        # Ensure the address is loaded
        WebDriverWait(self.browser, 180).until(EC.presence_of_element_located((By.CLASS_NAME, 'address')))

        address: str = self.browser.find_element(By.CLASS_NAME, 'address').text
        return address

    def get_emails(self) -> list[tuple[str, datetime]]:
        """Get list of emails sorted by date."""
        WebDriverWait(self.browser, 180).until(EC.presence_of_element_located((By.CLASS_NAME, 'messages-list')))
        results = []

        try:
            emails = self.browser.find_element(By.CLASS_NAME, 'messages-list').find_elements(By.TAG_NAME, 'li')
            if not len(emails):
                return results
        except NoSuchElementException:
            return results

        for email in emails:
            email_content: str = email.find_element(By.TAG_NAME, 'pre').text
            date_text:     str = email.find_element(By.XPATH, '//dd[@data-bind="text: receivedAt.toLocaleString()"]').text
            date:          datetime = datetime.strptime(date_text, '%d/%m/%Y, %H:%M:%S %p')

            results.append((email_content, date))

        return sorted(results, key=lambda x: x[1])

    def get_new_email(self):
        """Refreshing the page will get a new email address."""
        self.browser.refresh()

    def quit(self) -> None:
        """Quits the browser."""
        if self.browser is not None:
            self.browser.quit()
            self.browser = None
