##################################################################################################
#                                 MIT Licence (C) 2022 Cubicpath@Github                          #
##################################################################################################
"""Program entry point."""

__all__ = (
    'generate_clients',
    'main',
    'settings',
)

# stdlib
import atexit
from threading import Thread
from pathlib import Path
from typing import Any

# 3rd-party
import toml

# local
from client import Client

settings: dict[str, Any] = toml.loads(
    (Path.cwd() / 'settings.toml').read_text(encoding='utf8')
)
"""Settings loaded from settings.toml in the current working directory."""


def main() -> None:
    """Program entry point. If __name__ == '__main__'."""
    print(f'{"=" * 50}')
    print('Welcome to HaloLucozadeScript! Please remember that you can only redeem 120 xp boost codes per account.\n')
    amount: int = int(input('How many clients would you like to run? ').strip() or '1')  # Default (no answer) is 1
    print('All you have to do from now on is solve the captchas!\n')
    print(f'Generating clients...')
    print(f'{"-" * 17}Collected-Codes{"-" * 18}\n')

    if amount != 0:
        # Create a thread for each client and run them in parallel.
        generate_clients(amount, settings, bin_folder=Path.cwd() / 'bin')
    else:
        finish_up()


def finish_up() -> None:
    """Finish up while user starts on new client."""
    print(f'\n{"-" * 17}Collected-Codes{"-" * 18}\n')
    print('All done! Thanks for using HaloLucozadeScript!')
    input('Press <ENTER> to exit script...')
    print(f'{"=" * 50}')


def generate_clients(number: int, /, *args, **kwargs) -> None:
    """Recursively generate and run clients."""
    # Negative numbers represent infinite runs.
    if number == 0:
        return
    number -= 1

    # Create new client.
    client = Client(*args, **kwargs)
    atexit.register(client.quit)

    # Load the form and fill it out.
    client.accept_cookies()
    client.enter_information()
    client.submit_form()

    # After captcha, launch another client.
    if number:
        next_client = Thread(target=generate_clients, args=(number,) + args, kwargs=kwargs)
        next_client.name = f'Client Thread {number}'
        next_client.start()

    # Finish up while user starts on new client.
    client.input_bar_code()
    client.collect_reward()
    client.redeem_codes()

    # Close window to save resources.
    client.quit()
    atexit.unregister(client.quit)

    if number == 0:
        finish_up()


if __name__ == '__main__':
    main()
