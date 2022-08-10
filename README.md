HaloLucozadeScript
===============

A small script built on [Selenium](https://www.selenium.dev/selenium/docs/api/py/) that automatically completes the [halo-lucozade](https://halo.lucozade.com) promotional form.
The script will automatically fill out the form and submit it, you just have to complete the captchas.
It takes around 15 seconds to complete one form, and a second form is generated after you finish the first one's captcha.
Codes will be saved to the created `codes` folder, next to main.py etc.

#### Notes:
+ The maximum number of Double XP codes you can redeem during this promotion is 120 per account.
+ The promotion ends between Aug 12, 2022 at 11:00:00PM UTC.
+ If you do not live in the UK, then you may require a VPN. I recommend the [Windscribe](https://windscribe.net/) desktop client, as it works perfectly with this script, and is free.
+ Email verification has around a 20% chance of failing. If this happens, you are free to close the blocked browser window.

### Disclaimer:
_**This project is in no way associated with, endorsed by, or otherwise affiliated with the
Microsoft Corporation, Xbox Game Studios, 343 Industries, Suntory Holding Limited, or its Lucozade brand.**_

How to use:
---------------

1. Install [python 3.10](https://www.python.org/downloads/)

2. Download the latest [release zip](https://github.com/Cubicpath/HaloLucozadeScript/releases/latest)

3. Extract the contents of the zip to a folder

4. Install the requirements using `pip install -r requirements.txt` while in the folder

5. Run `main.py` with python

Example Console Output Images:
---------------
### Windows
![example](https://i.imgur.com/AEe3ayv.png)

### Linux
![example](https://i.imgur.com/QIoSexq.png)

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

#### Browser.email
| Setting                  | Type        | Default | Description                             |
|--------------------------|-------------|---------|-----------------------------------------|
| `visible`                | **boolean** | false   | Whether to show the email client window |
| `change_email_every`     | **integer** | 1       | Get a new email address every X clients |

#### Browser.proxy
| Setting         | Type        | Default | Description                                    |
|-----------------|-------------|---------|------------------------------------------------|
| `ip`            | **string**  | ""      | The proxy IP/hostname                          |
| `port`          | **integer** | 0       | The proxy Port                                 |
| `is_socks`      | **boolean** | false   | If true, uses socks proxies as opposed to HTTP |
| `socks_version` | **integer** | 5       | The socks version to use if `is_socks` is true |

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
