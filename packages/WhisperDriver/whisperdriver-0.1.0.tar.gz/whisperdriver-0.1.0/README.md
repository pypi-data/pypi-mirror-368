# WhisperDriver Library

WhisperDriver is a comprehensive Python library for automating and managing WhisperTrades.com bots, variables, and broker connections. It combines robust API access with advanced Selenium-based web automation, enabling features not available through the API alone. The library is designed for both novice and advanced users, with a focus on reliability, scheduling, and rate-limit safety.

## Features
- **API and Web Automation**: Use the official WhisperTrades API for fast, reliable access, and Selenium automation for advanced features (e.g., UI-only settings, Schwab broker renewal).
- **API and Web Credentials**: Uses API token, WhisperTrades credentials, and Schwab credentials for different functions beyond the scope of WT API alone.
- **Bot Management**: Enable, disable, update, and schedule bots programmatically.
- **Throttle Management**: Optional throttle lets you set a minimum delay between API requests to help avoid rate limits. Throttle is enabled by default, but you can disable or adjust the delay as needed.
- **Scheduler**: Built-in scheduler for timed bot actions (see `example.py`).
- **Built-in Automatic Schwab Broker Renewal Function**: Seamlessly renew Schwab connections using your proivided Schwab credentials.  Requires App Authenticator 2FA enabled on Schwab account.  First-time in-app confirmation required

## Installation

```bash
pip install -r requirements.txt
```

## Authentication & Credentials
- **API Token**: Obtain from your WhisperTrades.com account. Required for all API-based functions.
- **WhisperTrades Username/Password**: Required for Selenium-based web automation (e.g., UI-only features).
- **Schwab Username/Password**: Required for automatic Schwab broker renewal.

## Quick Start Example

```python
import WhisperDriver
import creds as personal

WD = WhisperDriver.ApiWrapper(personal.WT_API_TOKEN)
WD.via_selenium.enable(personal.USER, personal.PWD, is_verbose=True, is_headless=True)

# Start the scheduler
WD.scheduler.start()

# Enable all bots at 9:25 AM Eastern
WD.scheduler.add_task('9:25 AM', 'America/New_York', fxn=WD.bots.enable_all_bots)

# Soft disable all bots at 4:05 PM Eastern using Selenium
from functools import partial
WD.scheduler.add_task('4:05 PM', 'America/New_York', fxn=partial(WD.via_selenium.enabled_to_soft_disabled_by_list, WD.bots.get_all_bot_numbers()))

# Stop the scheduler at 4:30 PM
WD.scheduler.stop_scheduler_at_time('4:30 PM', 'America/New_York')
```

## Function Reference & Examples

### API Wrapper
- **`ApiWrapper(api_token)`**: Main entry point for API and Selenium functions.

### Selenium Web Automation
- **`WD.via_selenium.enable(user, pwd, is_verbose=True, is_headless=True)`**: Log in to WhisperTrades web UI for advanced automation.
- **`WD.via_selenium.enabled_to_soft_disabled_by_list(bot_nums, time_str, tz)`**: Instantly soft-disables a list of bots via the web UI. Use with scheduler for timed actions.
- **`WD.via_selenium.renew_schwab_connection(schwab_user, schwab_pwd)`**: Automatically renew Schwab broker connections. Requires Schwab credentials.

### Bot Management
- **`WD.bots.get_all_bots()`**: Returns a list of all bots and their settings.
- **`WD.bots.enable_bot(bot_num)`**: Enables a specific bot.
- **`WD.bots.disable_bot(bot_num)`**: Disables a specific bot.
- **`WD.bots.enable_all_bots()`**: Enables all bots.
- **`WD.bots.disable_all_bots()`**: Disables all bots.

### Variable Management
- **`WD.variables.get_all_variables()`**: Get all account variables.
- **`WD.variables.update_variable(var_name, value)`**: Update a variable.

### Throttle
 **`WD.throttle.set_delay_sec(seconds)`**: Set the minimum delay (in seconds) between API requests. (Default is 2 seconds)
 **`WD.throttle.enable()` / `WD.throttle.disable()`**: Enable or disable the throttle.

#### Example: Throttle Usage
```python
WD.throttle.set_delay_sec(2)
WD.throttle.set_delay(2)
# Disable throttle if you want maximum speed (not recommended for production)
WD.throttle.disable()
# Enable throttle again
WD.throttle.enable()
```

### Scheduler
- **`WD.scheduler.add_task(time_str, tz, fxn)`**: Schedule any function to run at a specific time and timezone.
- **`WD.scheduler.start()`**: Start the scheduler loop.
- **`WD.scheduler.stop_scheduler_at_time(time_str, tz)`**: Stop the scheduler at a specific time.

#### Example: Per-Bot Scheduling
```python
from functools import partial
for bot in WD.bots.get_all_bots():
    entry_time = bot['entry_time']  # e.g., '9:45 AM'
    bot_num = bot['number']
    # Enable 5 min before entry
    WD.scheduler.add_task('9:40 AM', 'America/New_York', fxn=partial(WD.bots.enable_bot, bot_num))
    # Soft disable 5 min after entry
    WD.scheduler.add_task('9:50 AM', 'America/New_York', fxn=partial(WD.via_selenium.enabled_to_soft_disabled_by_list, [bot_num]))
```

## Notes
- **Selenium Automation**: Some features (like Schwab renewal and soft disable) require a running Chrome/Chromium browser. Headless mode is supported for servers.
- **Security**: Keep your credentials secure. Never share your API token or passwords.

## Troubleshooting
- If Selenium functions fail on a server, ensure Chrome/Chromedriver and all dependencies are installed, and use headless mode.
- For 2FA (e.g., Schwab SMS), you may need to provide the code interactively if prompted.

## License
MIT License

