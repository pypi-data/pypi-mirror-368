# WhisperDriver

WhisperDriver is a comprehensive Python library for automating and managing [WhisperTrades.com](https://whispertrades.com/) bots, variables, and broker connections. It combines robust API access with advanced Selenium-based web automation, enabling features not available through the API alone. The library is designed with a focus on reliability, scheduling, and rate-limit consciousness.

## Features
- **API and Web Automation**: Use the official WhisperTrades API for fast, reliable access, and Selenium automation for advanced features (e.g., UI-only settings, Schwab broker renewal).
- **API and Web Credentials**: Uses API token, WhisperTrades credentials, and Schwab credentials for different functions beyond the scope of WT API alone.
- **Bot Management**: Enable, disable, update, open/close positions, and schedule bots programmatically.
- **Throttle Management**: Optional throttle lets you set a minimum delay between API requests to help avoid rate limits. Throttle is enabled with 2 second delay by default, but you can disable or adjust the delay as needed.
- **Scheduler**: Built-in scheduler for timed bot actions (see `example.py`).
- **Built-in Automatic Schwab Broker Renewal Function**: Seamlessly renew Schwab connections using your proivided Schwab credentials.  Requires App Authenticator 2FA enabled on Schwab account.  First-time in-app confirmation required to enable remembered device.

## Installation

```bash
pip install WhisperDriver
```

Or, to install all development dependencies:
```bash
pip install -r requirements.txt
```

## Authentication & Credentials
- **API Token**: Obtain from your [WhisperTrades.com](https://whispertrades.com/) account. Required for all API-based functions.
- **WhisperTrades Username/Password**: Required for Selenium-based web automation (e.g., UI-only features).
- **Schwab Username/Password**: Required only for automatic Schwab broker renewal.

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

## Core Concepts

### WD Object (`WD = WhisperDriver.ApiWrapper(token)`)
The main interface for all automation and API access. Instantiating `WD` gives you access to all major features:

- `.throttle` — API rate limiter (see below for details)
- `.endpts` — Endpoint handler for all API endpoints (raw API access)
- `.scheduler` — Scheduler for timed tasks and automation
- `.bots` — Bot management interface (see below)
- `.variables` — Variable management interface
- `.via_selenium` — Selenium-based UI automation interface
- `.bot_number_list` — List of all bot numbers
- `.report_number_list` — List of all report numbers
- `.variable_number_list` — List of all variable numbers

### WD.endpts: Endpoint Handler Object
- `.bots` — All bot-related API endpoints:
    - `get_all_bots()` — Get all bots (full details)
    - `get_bot(bot_number, status_filter=['Enabled', 'Disabled', 'Disable on Close'], include_details=True)` — Get a specific bot or filtered list
    - `enable_bot(bot_number)` — Enable a bot
    - `disable_bot(bot_number)` — Disable a bot (or set to 'Disable on Close' if open positions)
    - `get_bot_orders(bot_number)` — Get all orders for a bot
    - `get_bot_positions(bot_number='', position_number='', status='', from_date='', to_date='', page='')` — Get all or filtered positions for a bot
    - `open_position(bot_number)` — Force open a new position for a bot
    - `close_position(bot_number)` — Close all open positions for a bot
    - `close_bot_position(position_number)` — Close a specific position by number
- `.variables` — All variable-related API endpoints:
    - `get_all_bot_variables()` — Get all variables
    - `get_bot_variables(variable_number='')` — Get a specific variable or all
    - `set_bot_variables(variable_number, variable_name, new_value)` — Set a variable's value
- `.reports` — All report-related API endpoints:
    - `get_all_bot_reports()` — Get all reports
    - `get_bot_report(report_number='')` — Get a specific report or all
    - `update_bot_report(report_number, new_name='', new_start_date='', new_end_date='', run_until_latest_date=False)` — Update a report's details
    - `run_bot_report(report_number)` — Run a report
- `.brokers` — All broker connection endpoints:
    - `get_all_broker_connections()` — Get all broker connections
    - `get_broker_connections(number='')` — Get a specific broker connection or all
    - `rebalance_broker_collateral(number)` — Rebalance collateral for a broker connection

**Example:**
```python
# Get all bots (raw API)
raw_bots = WD.endpts.bots.get_all_bots()
# Enable a bot
WD.endpts.bots.enable_bot('123456')
# Get all variables
all_vars = WD.endpts.variables.get_all_bot_variables()
# Run a report
WD.endpts.reports.run_bot_report('report123')
# Get all broker connections
brokers = WD.endpts.brokers.get_all_broker_connections()
```

### WD.throttle: Throttle Object
- `.set_delay_sec(seconds)` — Set the minimum delay (in seconds) between API requests. (Default is 2 seconds)
- `.enable()` / `.disable()` — Enable or disable the throttle.

**Example:**
```python
WD.throttle.set_delay_sec(2)
WD.throttle.disable()
WD.throttle.enable()
```

### WD.scheduler: Scheduler Object
- `.start()` — Start the scheduler loop (runs in a background thread)
- `.stop()` — Stop the scheduler loop
- `.add_task(time_str, tz, fxn)` — Schedule any function to run at a specific time and timezone
- `.stop_scheduler_at_time(time_str, tz)` — Stop the scheduler at a specific time
- `.scheduler_is_on` — Boolean, True if the scheduler is running

**Example:**
```python
WD.scheduler.add_task('9:30 AM', 'America/New_York', fxn=WD.bots.enable_all_bots)
WD.scheduler.start()
```

### WD.variables: Variable Management Object
- `.get_all_variables()` — Get all account variables
- `.update_variable(var_name, value)` — Update a variable
- (Other variable-related methods may be available)

**Example:**
```python
all_vars = WD.variables.get_all_variables()
WD.variables.update_variable('MY_VAR', 42)
```

### WD.via_selenium: Selenium Automation Object
- `.enable(user, pwd, is_verbose=True, is_headless=True)` — Log in to WhisperTrades web UI for advanced automation
- `.enabled_to_soft_disabled_by_list(bot_nums, time_str=None, tz=None)` — Instantly soft-disables a list of bots via the web UI
- `.renew_schwab_connection(schwab_user, schwab_pwd)` — Automatically renew Schwab broker connections (requires Schwab credentials)
- (Other UI automation methods may be available)

**Example:**
```python
WD.via_selenium.enable('myuser', 'mypassword', is_headless=True)
WD.via_selenium.enabled_to_soft_disabled_by_list(['123456', '654321'])
```

## Bot Management

### Bots Object (`WD.bots`)
- `WD.bots.bots_list` — All bot objects (list)
- `WD.bots('bot_number')` — Returns bot object of bot number
- `WD.bots.get_all_bot_variables()` — Queries for variables and associates variables with bot objects in `.variables`
- `WD.bots.update_all_bots()` — Updates bot_list via WhisperTrades API

#### BotsList Object (`WD.bots.bots_list`)
    - `()` or `.all()` — List of all bot objects
    - `.is_enabled()` — List of bot objects that are currently enabled
    - `.is_disabled()` — List of bot objects that are currently disabled
    - `.is_disabled_on_close()` — List of bot objects that are currently disabled-on-close
    - `.add_bot_to_list(bot_dict)` — Creates bot object from JSON and adds to bot_list
    - `.remove_bot_from_list('bot_number')` — Removes bot from bot_list

#### Bot Object (`WD.bots('bot_number')`)
    - `.number` — Bot number
    - `.name` — Bot name
    - `.broker_connection` — Broker details dict
    - `.is_paper` — Bool, is sim or not
    - `.status` — Current enabled/disabled status
    - `.can_enable` — Bool, can enable
    - `.can_disable` — Bool, can disable
    - `.symbol` — Ticker bot is trading
    - `.type` — Position type
    - `.notes` — User notes
    - `.last_active_at` — Time last active
    - `.disabled_at` — Time disabled at
    - `.entry_condition` — Entry settings dict
    - `.exit_condition` — Exit settings dict
    - `.adjustments` — List of adjustment conditions
    - `.notifications` — List of notifications
    - `.variables` — List of bot variables
    - `.enable()` — Enable bot
    - `.disable()` — Disable bot
    - `.get_positions(position_number='', status='', from_date='', to_date='', page='')` — Get all positions for this bot, or use filter arguments
    - `.close_position_by_number(position_number)` — Close position by number
    - `.get_orders()` — Get all orders for bot
    - `.open_position()` — If bot is enabled, force open a new position
    - `.close_position()` — Close all bot’s open positions
    - `.update()` — Update bot information from WhisperTrades API
    - `.get_bot_variables()` — Update bot variable information from WhisperTrades API

**Usage Examples:**
```python
# List all bots
all_bots = WD.bots.bots_list.all

# Get a specific bot object
bot = WD.bots('123456')
print(bot.name, bot.status)

# Get enabled bots
enabled_bots = WD.bots.bots_list.is_enabled()

# Enable/disable a bot
bot.enable()
bot.disable()

# Get positions, orders, and variables
positions = bot.get_positions()
orders = bot.get_orders()
variables = bot.get_bot_variables()

# Open/close positions
bot.open_position()
bot.close_position()
bot.close_position_by_number('pos123')

# Update bot info
bot.update()
```

**Usage Examples:**
```python
# Get a list of all bot objects
all_bots = WD.bots.bots_list.all
for bot in all_bots:
    print(bot.number, bot.name, bot.status)

# Get all enabled bots
enabled_bots = WD.bots.bots_list.is_enabled()

# Refresh the list of all bots from the server
WD.bots.update_all_bots()

# Enable or disable all bots
WD.bots.enable_all_bots()
WD.bots.disable_all_bots()

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
- For 2FA (e.g., Schwab SMS), you may need to provide the code interactively if prompted.  If only sms 2FA you will need to instantiate with headless=False and provide the texted code

## License
MIT License

