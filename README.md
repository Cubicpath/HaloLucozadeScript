HaloLucozadeScript
===============

A small script built on [Selenium](https://www.selenium.dev/selenium/docs/api/py/) that automatically completes the [halo-lucozade](https://halo.lucozade.com) promotional form.
The script will automatically fill out the form and submit it, you just have to complete the captchas.
It takes around 15 seconds to complete one form, and a second form is generated after you finish the first one's captcha.

Please remember that the maximum number of Double XP codes you can redeem during this promotion is 120 per account.

### Disclaimer:
_**This project is in no way associated with, endorsed by, or otherwise affiliated with the
Microsoft Corporation, Xbox Game Studios, 343 Industries, Suntory Holding Limited, or its Lucozade brand.**_

How to use:
---------------

1. Install [python 3.10](https://www.python.org/downloads/)

2. Download the latest release zip

3. Extract the contents of the zip to a folder

4. Install the requirements using `pip install -r requirements.txt` while in the folder

5. Run `main.py` with python

Example Console Output Image:
---------------

![example](https://i.imgur.com/AEe3ayv.png)

Settings
---------------

There are many configurable settings that can be found in `settings.toml`.
You can change them by editing the file in your text editor of choice.

### All settings:

#### Browser
| Setting                  | Type        | Default       | Description                                                                          |
|--------------------------|-------------|---------------|--------------------------------------------------------------------------------------|
| `x_size`                 | **integer** | 600           | The width of the browser window                                                      |
| `y_size`                 | **integer** | 1080          | The height of the browser window                                                     |

#### Redeem
| Setting                  | Type        | Default       | Description                                                                          |
|--------------------------|-------------|---------------|--------------------------------------------------------------------------------------|
| `skip_proof_of_purchase` | **boolean** | false         | Disable automation for the proof of purchase section (barcode / dropdowns).          |
| `open_redemption_page`   | **boolean** | true          | Automatically open redemption page on your default browser with the code pre-filled. |
| `xp_boost_only`          | **boolean** | true          | Ignore non-XP boost codes (emblem/backdrop).                                         |

#### Info
| Setting                  | Type        | Default       | Description                                                                          |
|--------------------------|-------------|---------------|--------------------------------------------------------------------------------------|
| `country_code`           | **string**  | "NI"          | Country code representing the country dropdown choice.                               |
| `phone_number`           | **string**  | "7911 123456" | Old number not in use. Used for filling form.                                        |
| `postcode`               | **string**  | "SW1A 1AA"    | Postcode that is related to the country code. Used for filling form.                 |
| `store`                  | **string**  | "Other"       | Store option. "Other" should be fine.                                                |
