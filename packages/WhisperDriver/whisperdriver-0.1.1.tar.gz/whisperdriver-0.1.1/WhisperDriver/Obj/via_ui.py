########################################################################################################################
########################################################################################################################
###   Selenium driver for WhisperTrades.com API                                                                      ###
###                                                                                                                  ###
###   Authored by Paul Nobrgea   Contact: Paul@PaulNobrega.net                                                       ###
###   Python Version 3.10                                                                                            ###
########################################################################################################################
########################################################################################################################
import os
import platform
import warnings
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime, timedelta
import time
import copy
import chromedriver_autoinstaller


class SeleniumDriver:
    """
    Selenium-based driver for automating WhisperTrades.com UI actions.

    Handles login, bot management, and settings manipulation via browser automation.
    Designed for robust, isolated browser sessions.

    Args:
        endpts: API endpoints object for broker/bot lookups.
    """
    def __init__(self, endpts: object) -> None:
        self._endpts: object = endpts
        self.webdriver: uc.Chrome | None = None
        self.headless: bool | None = None
        self.verbose: bool | None = None
        self.user_name: str | None = None
        self.password: str | None = None
        self.delay_time_sec: int | None = None
        self._session_start_time: datetime | None = None
        self.login_url: str | None = None
        self.logout_url: str | None = None
        self.is_enabled: bool = False
        self._profile_dir: str | None = None
        return


    def __enter__(self) -> 'SeleniumDriver':
        """
        Enable use as a context manager (with statement).
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Cleanup resources when object is destroyed or context exits.
        """
        import shutil
        if self.webdriver is not None:
            self.webdriver.quit()
        if self._profile_dir:
            try:
                shutil.rmtree(self._profile_dir, ignore_errors=True)
            except Exception as e:
                warnings.warn(f'Failed to remove temp Chrome profile dir: {e}')
        return


    def close(self) -> None:
        """
        Explicitly destroy the object and cleanup resources.
        """
        self.__exit__(None, None, None)
        return

    def __configure_web_driver(self) -> None:
        """
        Configure and launch the Selenium browser with unique user profile for isolation.
        """

        def __get_chrome_version() -> int:
            os_name = platform.system()
            try:
                from chromedriver_autoinstaller.utils import get_chrome_version
                return int(get_chrome_version().split('.')[0])
            except Exception:
                if os_name.lower() == 'windows':
                    try:
                        return int(os.popen('reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version').read().split('REG_SZ')[-1].strip().split('.')[0])
                    except Exception:
                        raise Exception('Unable to determine Chrome version on Windows!')
                elif os_name.lower() == 'linux':
                    try:
                        ver = int(os.popen('chromium --version').read().split()[1].split('.')[0])
                    except Exception:
                        ver = int(os.popen('google-chrome --version').read().split()[-1].split('.')[0])
                    return ver
                else:
                    raise Exception('Incompatible operating system!')

        def __set_chrome_options(self_ref) -> uc.ChromeOptions:
            import tempfile
            options = uc.ChromeOptions()
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4515.159 Safari/537.36'
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-first-run')
            options.add_argument('--no-service-autorun')
            options.add_argument('--password-store=basic')
            options.add_argument('--lang=en-US')
            options.add_argument('--window-size=1920,1080')
            options.add_argument(f'--user-agent={user_agent}')
            # Add a unique user-data-dir for each instance to prevent cross talk
            self_ref._profile_dir = tempfile.mkdtemp(prefix="wt_chrome_profile_")
            options.add_argument(f'--user-data-dir={self_ref._profile_dir}')
            if self_ref.headless:
                options.add_argument('--headless')
            chrome_preferences = {'profile.default_content_settings': {"images": 2}}
            options.experimental_options["prefs"] = chrome_preferences
            return options

        try:
            chromedriver_autoinstaller.install()
        except Exception as e:
            warnings.warn(f'Could not auto-install chromedriver: {e}')

        try:
            self.webdriver = uc.Chrome(options=__set_chrome_options(self), version_main=__get_chrome_version())
        except Exception as e:
            warnings.warn(f'Could not start Chrome with detected version: {e}. Trying fallback version 114.')
            self.webdriver = uc.Chrome(options=__set_chrome_options(self), version_main=114)
        return

    def __restart_webdriver(self) -> None:
        """
        Quit webdriver and reconfigure a new browser session.
        """
        if self.webdriver:
            self.webdriver.quit()
        self.__configure_web_driver()
        return
    
    def __on_error_404(self, warn_except: str, error_str: str) -> bool:
        is_404 = True if 'page not found' in self.webdriver.title else False
        if is_404 and 'warn' in warn_except.lower():
            warnings.warn(error_str)
            return True
        elif is_404 and 'except' in warn_except.lower():
            raise Exception(error_str)
        return False

    def __get_url_and_wait(self, url: str) -> bool:
        """
        Get specified url via self.webdriver. Wait for page load using Selenium's WebDriverWait.

        :param url: WhisperTrades.com url
        :type url: str
        :return: Bool value of successful url load
        :rtype: bool
        :raises Exception: If url cannot load within 2 seconds.
        """
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        self.log_in_if_not()
        self.webdriver.get(url)
        try:
            WebDriverWait(self.webdriver, 2).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        except Exception:
            self.webdriver.get(url)
            try:
                WebDriverWait(self.webdriver, 2).until(lambda d: d.execute_script('return document.readyState') == 'complete')
            except Exception:
                self._session_start_time = self._session_start_time - timedelta(minutes=60)
                raise Exception(f'UNABLE TO LOAD {url}')
        self._session_start_time = datetime.now()
        return False if self.__on_error_404('warn', f'Error 404: INVALID URL {url}') else True

    def __authorization(self) -> bool:
        """
        Login to whispertrades.com via web UI login page

        :return: Bool value of authorization state
        :rtype: bool
        """

        if not self.is_enabled:
            raise Exception('Selenium Driver is not enabled.  Enabled command must be run first. Example:\nWD.via_selenium.enable(user_name: str, password: str, is_verbose: bool = False, is_headless: bool = True)')
        
        self.webdriver.get(self.login_url)
        time.sleep(1)
        username = self.webdriver.find_element(by=By.NAME, value="email")
        password = self.webdriver.find_element(by=By.NAME, value="password")
        login_btn = self.webdriver.find_element(by=By.CLASS_NAME, value="bg-green-primary")
        username.send_keys(self.user_name)
        password.send_keys(self.password)
        login_btn.click()
        time.sleep(1)
        self.__on_error_404('except', f'UNABLE TO LOGIN TO WHISPERTRADES.COM')
        self._session_start_time = datetime.now()
        return True

    def enable(self, user_name: str, password: str, is_verbose: bool = False, is_headless: bool = True) -> None:
        self.is_enabled = True
        self.webdriver = None
        self.headless = is_headless
        self.verbose = is_verbose
        self.user_name = user_name
        self.password = password
        self.delay_time_sec = 1
        self._session_start_time = datetime.now()
        self.login_url = "https://whispertrades.com/login"
        self.logout_url = "https://whispertrades.com/logout"
        self.__configure_web_driver()
        self.__authorization()
        self.current_bots = {}
        return
    

    def is_logged_in(self) -> bool:
        """
        Determine if logged in by 1) if last session was less than 5 minutes ago or 2) presence of url redirect at login url

        :return: Bool value of logged in state
        :rtype: bool
        """
        if self._session_start_time + timedelta(minutes=2) > datetime.now():
            return True
        self.webdriver.get(self.login_url)
        time.sleep(0.3)
        return True if self.webdriver.current_url != self.login_url else False

    def log_in_if_not(self) -> bool:
        """
        Login if not currently logged in

        :return: Bool value of logged in state
        :rtype: bool
        """
        if self.is_logged_in():
            return True
        else:
            for i in range(3):
                if self.__authorization():
                    break
            return self.is_logged_in()

    def renew_accesss_token(self) -> bool:
        """
        Log out user and login again.

        :return: Bool value of authorization state
        :rtype: bool
        """
        self.revoke_accesss_token()
        return self.__authorization()

    def revoke_accesss_token(self) -> None:
        """
        Log out user.
        """
        self.webdriver.get(self.logout_url)
        return
    
    def __update_field(self, field, value) -> None:
        """
        Update a form field with a new value using keyboard shortcuts.
        """
        try:
            field.send_keys(Keys.CONTROL + 'a')
            field.send_keys(Keys.DELETE)
            field.send_keys(value)
        except Exception as e:
            warnings.warn(f'Failed to update field: {e}')
        return

    def renew_schwab_connection(self, schwab_user: str, schwab_pass: str, blacklist: list=[]) -> bool:
            """
            Renew schwab connection with passed schwab credentials
            
            :param schwab_user: Schwab User Name
            :type schwab_user: string
            :param schwab_pass: Schwab Password
            :type schwab_pass: string
            :param blacklist: List of schwab WT broker numbers to not renew
            :type blacklist: list
            :return: Success as True or False
            :rtype: bool
            """

            def __find_and_sleep(id=''):
                for _ in range(3):
                    time.sleep(5)
                    try:
                        element = self.webdriver.find_element(by=By.ID, value=id)
                        if 'traceback' in element.text.lower():
                            raise NoSuchElementException
                        return element
                    except NoSuchElementException:
                        time.sleep(5)
                return False

            def __click_by_id(id):
                element = __find_and_sleep(id=id)
                return element.click()
            
            def __click_by_id_via_js(id):
                btn = __click_by_id(id)
                return self.webdriver.execute_script ("arguments[0].click();",btn)
                
            
            all_brokers = self._endpts.brokers.get_all_broker_connections()
            connections = [d for d in all_brokers if d['broker'].lower() == 'schwab' and d['number'] not in blacklist]

            for c in connections:
                method = 'renew' if c['status'].lower() == 'active' else 'enable'
                schwab_renew_url = f"https://whispertrades.com/broker_connections/{c['number']}/{method}"
                print(f'Renew URL: {schwab_renew_url}')
                self.__get_url_and_wait(schwab_renew_url)
                user_field = __find_and_sleep(id='loginIdInput')
                pass_field = __find_and_sleep(id='passwordInput')
                login_btn = __find_and_sleep(id='btnLogin')
                self.__update_field(user_field, schwab_user)
                self.__update_field(pass_field, schwab_pass)
                login_btn.click()
                time.sleep(5)

                try:
                    id_selection = 'mobile_approve'
                    self.webdriver.find_element(by=By.ID, value=id_selection)
                    new_device = __click_by_id_via_js(id_selection)
                except Exception as e:
                    try:
                        id_selection = 'otp_sms'
                        self.webdriver.find_element(by=By.ID, value=id_selection)
                        new_device = __click_by_id_via_js(id_selection)
                    except Exception as e:
                        new_device = None
                
                if new_device:
                    # If device is not yet trusted
                    new_device.click()
                    clicks = ['remember-device-yes', 'btnContinue', 'acceptTerms', 'submit-btn', 'agree-modal-btn-', 'submit-btn', 'cancel-btn']
                    _ = [__click_by_id(c) for c in clicks]
                else:
                    clicks = ['acceptTerms', 'submit-btn', 'agree-modal-btn-', 'submit-btn', 'cancel-btn']
                    _ = [__click_by_id(c) for c in clicks]
                time.sleep(5)
            return True

    def get_entry_settings(self, bot_num: str) -> dict:
            """
            Get current WT Bot Entry Settings of specified bot number
            Scrapes all entry fields from the WhisperTrades bot form, including frequency, allocation, DTEs, strike selection, filters, toggles, etc.
            Handles missing/optional fields robustly.
            :param bot_num: WhisperTrades bot Number
            :type bot_num: string
            :return: Dictionary of settings
            :rtype: dict
            """

            # Helper functions must be defined before use
            def safe_find_value(by, value, attr='value', default=None):
                try:
                    el = self.webdriver.find_element(by=by, value=value)
                    return el.get_attribute(attr)
                except Exception:
                    return default

            def safe_find_checkbox(by, value, default=False):
                try:
                    el = self.webdriver.find_element(by=by, value=value)
                    return el.is_selected()
                except Exception:
                    return default

            def safe_find_select(by, value, default=None):
                try:
                    el = self.webdriver.find_element(by=by, value=value)
                    return el.get_attribute('value')
                except Exception:
                    return default

            wt_entry_edit_url = f'https://whispertrades.com/bots/{bot_num}/entry/edit'
            self.__get_url_and_wait(wt_entry_edit_url)

            # --- Allocation Section ---
            settings = {}
            # Frequency (dropdown)
            settings['frequency'] = safe_find_select(By.ID, 'data.frequency')
            # Allocation Type (dropdown)
            settings['allocation_type'] = safe_find_select(By.ID, 'data.allocation_type')
            # Contract Quantity (number input)
            settings['allocation_quantity'] = safe_find_value(By.ID, 'data.allocation_quantity')
            # Maximum Concurrent Positions (dropdown)
            settings['maximum_concurrent_positions'] = safe_find_select(By.ID, 'data.maximum_concurrent_positions')
            # Allocation Percent (hidden unless allocation_type == 'Percent of Portfolio')
            settings['allocation_percent'] = safe_find_value(By.ID, 'data.allocation_percent')
            # Allocation Dollars (hidden unless allocation_type == 'Leverage Amount')
            settings['allocation_dollars'] = safe_find_value(By.ID, 'data.allocation_dollars')
            # Allocation Leverage (hidden unless allocation_type == 'Leverage Amount')
            settings['allocation_leverage'] = safe_find_value(By.ID, 'data.allocation_leverage')
            # --- Miscellaneous Section ---
            # Entry Speed (dropdown)
            settings['entry_speed'] = safe_find_select(By.ID, 'data.entry_speed')
            # Move Strike Selection With Conflict (toggle)
            settings['move_strike_selection_with_conflict'] = safe_find_checkbox(By.ID, 'data.move_strike_selection_with_conflict')

            # --- Strike Selection Section ---
            # DTEs
            settings['min_dte'] = safe_find_value(By.ID, 'data.minimum_days_to_expiration')
            settings['target_dte'] = safe_find_value(By.ID, 'data.target_days_to_expiration')
            settings['max_dte'] = safe_find_value(By.ID, 'data.maximum_days_to_expiration')

            # Put Short Strike Target Type (dropdown)
            settings['put_short_strike_target_type'] = safe_find_select(By.ID, 'data.put_short_strike_target_type')
            # Put Short Strike Delta fields
            settings['put_short_strike_delta_minimum'] = safe_find_value(By.ID, 'data.put_short_strike_delta_minimum')
            settings['put_short_strike_delta'] = safe_find_value(By.ID, 'data.put_short_strike_delta')
            settings['put_short_strike_delta_maximum'] = safe_find_value(By.ID, 'data.put_short_strike_delta_maximum')
            # Put Spread Target Type (dropdown)
            settings['put_spread_strike_target_type'] = safe_find_select(By.ID, 'data.put_spread_strike_target_type')
            # Put Spread Target Premium
            settings['put_spread_strike_target_price'] = safe_find_value(By.ID, 'data.put_spread_strike_target_price')
            # Put Spread Min/Max Width
            settings['put_spread_minimum_width'] = safe_find_value(By.ID, 'data.put_spread_minimum_width')
            settings['put_spread_maximum_width'] = safe_find_value(By.ID, 'data.put_spread_maximum_width')
            # Restrict Spread Width By (dropdown)
            settings['restrict_put_spread_width_by'] = safe_find_select(By.ID, 'data.restrict_put_spread_width_by')

            # (Retain call fields for call bots, if present)
            settings['call_min_delta'] = safe_find_value(By.ID, 'data.call_short_strike_delta_minimum')
            settings['call_target_delta'] = safe_find_value(By.ID, 'data.call_short_strike_delta')
            settings['call_max_delta'] = safe_find_value(By.ID, 'data.call_short_strike_delta_maximum')
            settings['long_strike_target_premium'] = safe_find_value(By.ID, 'data.put_spread_strike_target_price') or safe_find_value(By.ID, 'data.call_spread_strike_target_price')
            settings['long_strike_points_minimum_width'] = safe_find_value(By.ID, 'data.put_spread_minimum_width') or safe_find_value(By.ID, 'data.call_spread_minimum_width')
            settings['long_strike_points_maximum_width'] = safe_find_value(By.ID, 'data.put_spread_maximum_width') or safe_find_value(By.ID, 'data.call_spread_maximum_width')
            # Underlying move filters
            settings['minimum_percent_move_from_close'] = safe_find_value(By.ID, 'data.minimum_underlying_percent_move_from_close')
            settings['maximum_percent_move_from_close'] = safe_find_value(By.ID, 'data.maximum_underlying_percent_move_from_close')
            # Underlying price filters
            settings['min_underlying_price'] = safe_find_value(By.ID, 'data.minimum_underlying_price')
            settings['max_underlying_price'] = safe_find_value(By.ID, 'data.maximum_underlying_price')
            # Underlying IV filters
            settings['min_underlying_iv'] = safe_find_value(By.ID, 'data.minimum_underlying_iv')
            settings['max_underlying_iv'] = safe_find_value(By.ID, 'data.maximum_underlying_iv')
            # Underlying IV rank filters
            settings['min_underlying_iv_rank'] = safe_find_value(By.ID, 'data.minimum_underlying_iv_rank')
            settings['max_underlying_iv_rank'] = safe_find_value(By.ID, 'data.maximum_underlying_iv_rank')
            # Underlying IV percentile filters
            settings['min_underlying_iv_percentile'] = safe_find_value(By.ID, 'data.minimum_underlying_iv_percentile')
            settings['max_underlying_iv_percentile'] = safe_find_value(By.ID, 'data.maximum_underlying_iv_percentile')
            # Earnings filter
            settings['skip_earnings'] = safe_find_checkbox(By.ID, 'data.skip_earnings')
            # Exclude tickers (comma separated)
            settings['exclude_tickers'] = safe_find_value(By.ID, 'data.exclude_tickers')
            # Only tickers (comma separated)
            settings['only_tickers'] = safe_find_value(By.ID, 'data.only_tickers')
            # Underlying price change filter
            settings['min_underlying_price_change'] = safe_find_value(By.ID, 'data.minimum_underlying_price_change')
            settings['max_underlying_price_change'] = safe_find_value(By.ID, 'data.maximum_underlying_price_change')
            # Underlying volume filter
            settings['min_underlying_volume'] = safe_find_value(By.ID, 'data.minimum_underlying_volume')
            # Underlying open interest filter
            settings['min_underlying_open_interest'] = safe_find_value(By.ID, 'data.minimum_underlying_open_interest')
            # Underlying market cap filter
            settings['min_underlying_market_cap'] = safe_find_value(By.ID, 'data.minimum_underlying_market_cap')
            # Underlying sector filter
            settings['underlying_sector'] = safe_find_select(By.ID, 'data.underlying_sector')
            # Underlying industry filter
            settings['underlying_industry'] = safe_find_select(By.ID, 'data.underlying_industry')
            # Only ETFs toggle
            settings['only_etfs'] = safe_find_checkbox(By.ID, 'data.only_etfs')
            # Only stocks toggle
            settings['only_stocks'] = safe_find_checkbox(By.ID, 'data.only_stocks')
            # Only index toggle
            settings['only_index'] = safe_find_checkbox(By.ID, 'data.only_index')
            # Only liquid options toggle
            settings['only_liquid_options'] = safe_find_checkbox(By.ID, 'data.only_liquid_options')
            # Only marginable toggle
            settings['only_marginable'] = safe_find_checkbox(By.ID, 'data.only_marginable')
            # Only shortable toggle
            settings['only_shortable'] = safe_find_checkbox(By.ID, 'data.only_shortable')
            # Only easy to borrow toggle
            settings['only_easy_to_borrow'] = safe_find_checkbox(By.ID, 'data.only_easy_to_borrow')
            # Only hard to borrow toggle
            settings['only_hard_to_borrow'] = safe_find_checkbox(By.ID, 'data.only_hard_to_borrow')
            # Custom filters (if present)
            settings['custom_filter'] = safe_find_value(By.ID, 'data.custom_filter')

            # Entry time window (dropdowns) -- updated to match actual HTML
            try:
                from selenium.webdriver.support.ui import Select
                earliest_entry_el = self.webdriver.find_element(By.ID, 'data.earliest_entry_time')
                latest_entry_el = self.webdriver.find_element(By.ID, 'data.latest_entry_time')
                earliest_entry = Select(earliest_entry_el).first_selected_option.text.strip()
                latest_entry = Select(latest_entry_el).first_selected_option.text.strip()
                settings['earliest_entry_time'] = earliest_entry if earliest_entry else None
                settings['latest_entry_time'] = latest_entry if latest_entry else None
            except Exception:
                settings['earliest_entry_time'] = None
                settings['latest_entry_time'] = None

            # Entry days of week (checkboxes) -- updated to match actual HTML
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            checked_days = []
            try:
                els = self.webdriver.find_elements(By.CSS_SELECTOR, "input[type='checkbox'][wire\\:model='data.days_of_week']")
                if not els:
                    print('[DEBUG] No checkboxes found for days_of_week')
                for el in els:
                    val = el.get_attribute('value')
                    if val in days and el.is_selected():
                        checked_days.append(val)
            except Exception as e:
                print(f'[DEBUG] Exception in days_of_week scraping: {e}')
            # Always return a list, never None
            settings['days_of_week'] = checked_days

            # Return the full settings dict
            return settings


    def update_entry_settings(self, bot_num: str, entry_settings_dict: dict) -> dict:
        """
        Change WT Bot Entry Settings of specified bot number using dictionary of values
        
        :param bot_num: WhisperTrades bot Number
        :param entry_settings_dict: Dictionary with the same format as returned by function 'get_entry_settings'
        :return: Dictionary of changed settings
        :rtype: dict
        """
        settings = self.get_entry_settings(bot_num)
        initial_settings = copy.deepcopy(settings)
        settings.update(entry_settings_dict)

        if initial_settings == settings:
            if self.verbose:
                print(f'No changes required for ENTRY settings of bot: {bot_num}')
            return settings

        wt_entry_edit_url = f'https://whispertrades.com/bots/{bot_num}/entry/edit'
        self.__get_url_and_wait(wt_entry_edit_url)
        save_btn = self.webdriver.find_element(by=By.CLASS_NAME, value='bg-green-600')

        def safe_update_field(field_id, value, input_type='text'):
            try:
                el = self.webdriver.find_element(By.ID, field_id)
                if input_type == 'checkbox':
                    if bool(el.is_selected()) != bool(value):
                        el.click()
                elif input_type == 'select':
                    from selenium.webdriver.support.ui import Select
                    sel = Select(el)
                    try:
                        sel.select_by_value(str(value))
                    except Exception:
                        # Fallback: try to match by visible text
                        found = False
                        for option in sel.options:
                            if option.text.strip() == str(value).strip():
                                option.click()
                                found = True
                                break
                        if not found:
                            print(f"[DEBUG] Could not set select field {field_id} to value '{value}' by value or text.")
                else:
                    el.clear()
                    if value is not None:
                        el.send_keys(str(value))
            except Exception as e:
                print(f"[DEBUG] Exception in safe_update_field for {field_id}: {e}")

        # Update all fields present in settings
        field_map = {
            # --- Allocation Section ---
            'frequency': ('data.frequency', 'select'),
            'allocation_type': ('data.allocation_type', 'select'),
            'allocation_quantity': ('data.allocation_quantity', 'text'),
            'maximum_concurrent_positions': ('data.maximum_concurrent_positions', 'select'),
            'allocation_percent': ('data.allocation_percent', 'text'),
            'allocation_dollars': ('data.allocation_dollars', 'text'),
            'allocation_leverage': ('data.allocation_leverage', 'text'),
            # --- Miscellaneous Section ---
            'entry_speed': ('data.entry_speed', 'select'),
            'move_strike_selection_with_conflict': ('data.move_strike_selection_with_conflict', 'checkbox'),
            # --- Strike Selection Section ---
            'min_dte': ('data.minimum_days_to_expiration', 'text'),
            'target_dte': ('data.target_days_to_expiration', 'text'),
            'max_dte': ('data.maximum_days_to_expiration', 'text'),
            'min_delta': ('data.put_short_strike_delta_minimum', 'text'),
            'target_delta': ('data.put_short_strike_delta', 'text'),
            'max_delta': ('data.put_short_strike_delta_maximum', 'text'),
            'call_min_delta': ('data.call_short_strike_delta_minimum', 'text'),
            'call_target_delta': ('data.call_short_strike_delta', 'text'),
            'call_max_delta': ('data.call_short_strike_delta_maximum', 'text'),
            'long_strike_target_premium': ('data.put_spread_strike_target_price', 'text'),
            'long_strike_points_minimum_width': ('data.put_spread_minimum_width', 'text'),
            'long_strike_points_maximum_width': ('data.put_spread_maximum_width', 'text'),
            # --- Filters, toggles, etc. ---
            'minimum_percent_move_from_close': ('data.minimum_underlying_percent_move_from_close', 'text'),
            'maximum_percent_move_from_close': ('data.maximum_underlying_percent_move_from_close', 'text'),
            'min_underlying_price': ('data.minimum_underlying_price', 'text'),
            'max_underlying_price': ('data.maximum_underlying_price', 'text'),
            'min_underlying_iv': ('data.minimum_underlying_iv', 'text'),
            'max_underlying_iv': ('data.maximum_underlying_iv', 'text'),
            'min_underlying_iv_rank': ('data.minimum_underlying_iv_rank', 'text'),
            'max_underlying_iv_rank': ('data.maximum_underlying_iv_rank', 'text'),
            'min_underlying_iv_percentile': ('data.minimum_underlying_iv_percentile', 'text'),
            'max_underlying_iv_percentile': ('data.maximum_underlying_iv_percentile', 'text'),
            'skip_earnings': ('data.skip_earnings', 'checkbox'),
            'exclude_tickers': ('data.exclude_tickers', 'text'),
            'only_tickers': ('data.only_tickers', 'text'),
            'min_underlying_price_change': ('data.minimum_underlying_price_change', 'text'),
            'max_underlying_price_change': ('data.maximum_underlying_price_change', 'text'),
            'min_underlying_volume': ('data.minimum_underlying_volume', 'text'),
            'min_underlying_open_interest': ('data.minimum_underlying_open_interest', 'text'),
            'min_underlying_market_cap': ('data.minimum_underlying_market_cap', 'text'),
            'underlying_sector': ('data.underlying_sector', 'select'),
            'underlying_industry': ('data.underlying_industry', 'select'),
            'only_etfs': ('data.only_etfs', 'checkbox'),
            'only_stocks': ('data.only_stocks', 'checkbox'),
            'only_index': ('data.only_index', 'checkbox'),
            'only_liquid_options': ('data.only_liquid_options', 'checkbox'),
            'only_marginable': ('data.only_marginable', 'checkbox'),
            'only_shortable': ('data.only_shortable', 'checkbox'),
            'only_easy_to_borrow': ('data.only_easy_to_borrow', 'checkbox'),
            'only_hard_to_borrow': ('data.only_hard_to_borrow', 'checkbox'),
            'custom_filter': ('data.custom_filter', 'text'),
            'entry_time_start': ('data.entry_time_start', 'text'),
            'entry_time_end': ('data.entry_time_end', 'text'),
            'entry_days_of_week': ('data.entry_days_of_week', 'text'),
        }
        for k, v in settings.items():
            if k in field_map and v is not None:
                safe_update_field(field_map[k][0], v, field_map[k][1])

        # --- Days of week (checkboxes) robust update ---
        if 'days_of_week' in settings and settings['days_of_week'] is not None:
            try:
                days = settings['days_of_week']
                els = self.webdriver.find_elements(By.CSS_SELECTOR, "input[type='checkbox'][wire\\:model='data.days_of_week']")
                if not els:
                    print('[DEBUG] No checkboxes found for days_of_week when updating.')
                for el in els:
                    val = el.get_attribute('value')
                    should_be_checked = val in days
                    if el.is_selected() != should_be_checked:
                        el.click()
            except Exception as e:
                print(f'[DEBUG] Exception in updating days_of_week: {e}')

        # --- Earliest/Latest Entry Time dropdowns robust update ---
        from selenium.webdriver.support.ui import Select
        for time_field, dom_id in [('earliest_entry_time', 'data.earliest_entry_time'), ('latest_entry_time', 'data.latest_entry_time')]:
            if time_field in settings and settings[time_field] is not None:
                try:
                    el = self.webdriver.find_element(By.ID, dom_id)
                    sel = Select(el)
                    value_set = False
                    # Try by value
                    try:
                        sel.select_by_value(str(settings[time_field]))
                        value_set = True
                    except Exception:
                        # Fallback: try by visible text
                        for option in sel.options:
                            if option.text.strip() == str(settings[time_field]).strip():
                                option.click()
                                value_set = True
                                break
                    if not value_set:
                        print(f"[DEBUG] Could not set {time_field} to {settings[time_field]}")
                except Exception as e:
                    print(f"[DEBUG] Exception updating {time_field}: {e}")

        save_btn.click()
        time.sleep(1)
        new_settings = self.get_entry_settings(bot_num)
        if self.verbose:
            print(f'Updated ENTRY settings for bot: {bot_num}')
        if initial_settings == new_settings:
            warnings.warn(f'Entry settings are unchanged for bot: {bot_num}')
        return new_settings
    
    
    def get_exit_settings(self, bot_num: str) -> dict:
            """
            Get current WT Bot Exit Settings of specified bot number
            Scrapes all exit fields from the WhisperTrades bot exit form, including all standing profit targets, monitored stops, trailing stops, sensitivities, toggles, and advanced variables.
            Handles missing/optional fields robustly.
            :param bot_num: WhisperTrades bot Number
            :type bot_num: string
            :return: Dictionary of settings
            :rtype: dict
            """
            wt_exit_edit_url = f'https://whispertrades.com/bots/{bot_num}/exit/edit'
            self.__get_url_and_wait(wt_exit_edit_url)

            def safe_find_value(by, value, attr='value', default=None):
                try:
                    el = self.webdriver.find_element(by=by, value=value)
                    return el.get_attribute(attr)
                except Exception:
                    return default

            def safe_find_checkbox(by, value, default=False):
                try:
                    el = self.webdriver.find_element(by=by, value=value)
                    return el.is_selected()
                except Exception:
                    return default

            def safe_find_select(by, value, default=None):
                try:
                    el = self.webdriver.find_element(by=by, value=value)
                    return el.get_attribute('value')
                except Exception:
                    return default

            # --- Profit (Standing) Section ---
            settings = {}
            # Profit Target % (number input)
            settings['profit_target_percent'] = safe_find_value(By.ID, 'data.profit_target_percent')
            # Premium <= (number input)
            settings['premium_profit_less_than_or_equal_to'] = safe_find_value(By.ID, 'data.premium_value_profit')

            # --- Monitored Stops Section ---
            settings['stop_loss_percent'] = safe_find_value(By.ID, 'data.stop_loss_percent')
            settings['premium_value_loss'] = safe_find_value(By.ID, 'data.premium_value_loss')
            settings['itm_percent'] = safe_find_value(By.ID, 'data.itm_percent')
            settings['otm_percent'] = safe_find_value(By.ID, 'data.otm_percent')
            settings['delta_value'] = safe_find_value(By.ID, 'data.delta_value')
            settings['monitored_stop_sensitivity'] = safe_find_select(By.ID, 'data.monitored_stop_sensitivity')

            # Variables (Advanced) - exitVariables repeater
            try:
                exit_vars = []
                idx = 0
                while True:
                    var_id = f'data.exitVariables.{idx}.name'
                    val = safe_find_value(By.ID, var_id)
                    if val is None:
                        break
                    exit_vars.append(val)
                    idx += 1
                settings['exit_variables'] = exit_vars
            except Exception:
                settings['exit_variables'] = []

            # --- Trailing Stops Section ---
            # Profit %
            settings['trail_profit_target_percent_trigger'] = safe_find_value(By.ID, 'data.trail_profit_target_percent_trigger')
            settings['trail_profit_target_percent_amount'] = safe_find_value(By.ID, 'data.trail_profit_target_percent_amount')
            # Premium Value
            settings['trail_premium_value_profit_trigger'] = safe_find_value(By.ID, 'data.trail_premium_value_profit_trigger')
            settings['trail_premium_value_profit_amount'] = safe_find_value(By.ID, 'data.trail_premium_value_profit_amount')
            # Misc
            settings['trailing_stop_sensitivity'] = safe_find_select(By.ID, 'data.trailing_stop_sensitivity')

            # --- Remaining fields (already present) ---
            settings['exit_speed'] = safe_find_select(By.ID, 'data.exit_speed')
            settings['close_short_strike_only'] = safe_find_checkbox(By.ID, 'data.close_short_strike_only')
            settings['exit_ma_crossover_toggle'] = safe_find_checkbox(By.ID, 'data.exit_ma_crossover_toggle')
            settings['exit_ma_value_toggle'] = safe_find_checkbox(By.ID, 'data.exit_ma_value_toggle')

            return settings

    def update_exit_settings(self, bot_num: str, exit_settings_dict: dict) -> dict:
        """
        Change WT Bot Exit Settings of specified bot number using dictionary of values
        
        :param bot_num: WhisperTrades bot Number
        :param exit_settings_dict: Dictionary with the same format as returned by function 'get_exit_settings'
        :return: Dictionary of changed settings
        :rtype: dict
        """
        settings = self.get_exit_settings(bot_num)
        initial_settings = copy.deepcopy(settings)
        settings.update(exit_settings_dict)

        if initial_settings == settings:
            if self.verbose:
                print(f'No changes required for EXIT settings of bot: {bot_num}')
            return settings

        wt_exit_edit_url = f'https://whispertrades.com/bots/{bot_num}/exit/edit'
        self.__get_url_and_wait(wt_exit_edit_url)
        save_btn = self.webdriver.find_element(by=By.CLASS_NAME, value='bg-green-600')

        def safe_update_field(field_id, value, input_type='text'):
            try:
                el = self.webdriver.find_element(By.ID, field_id)
                if input_type == 'checkbox':
                    if bool(el.is_selected()) != bool(value):
                        el.click()
                elif input_type == 'select':
                    from selenium.webdriver.support.ui import Select
                    Select(el).select_by_value(str(value))
                else:
                    el.clear()
                    if value is not None:
                        el.send_keys(str(value))
            except Exception:
                pass


        # Updated field map to match get_exit_settings keys and UI IDs
        field_map = {
            # --- Profit (Standing) Section ---
            'profit_target_percent': ('data.profit_target_percent', 'text'),
            'premium_profit_less_than_or_equal_to': ('data.premium_value_profit', 'text'),
            # --- Monitored Stops Section ---
            'stop_loss_percent': ('data.stop_loss_percent', 'text'),
            'premium_value_loss': ('data.premium_value_loss', 'text'),
            'itm_percent': ('data.itm_percent', 'text'),
            'otm_percent': ('data.otm_percent', 'text'),
            'delta_value': ('data.delta_value', 'text'),
            'monitored_stop_sensitivity': ('data.monitored_stop_sensitivity', 'select'),
            # --- Trailing Stops Section ---
            'trail_profit_target_percent_trigger': ('data.trail_profit_target_percent_trigger', 'text'),
            'trail_profit_target_percent_amount': ('data.trail_profit_target_percent_amount', 'text'),
            'trail_premium_value_profit_trigger': ('data.trail_premium_value_profit_trigger', 'text'),
            'trail_premium_value_profit_amount': ('data.trail_premium_value_profit_amount', 'text'),
            'trailing_stop_sensitivity': ('data.trailing_stop_sensitivity', 'select'),
            # --- Miscellaneous Section ---
            'exit_speed': ('data.exit_speed', 'select'),
            'close_short_strike_only': ('data.close_short_strike_only', 'checkbox'),
            # --- Market Conditions Section ---
            'exit_ma_crossover_toggle': ('data.exit_ma_crossover_toggle', 'checkbox'),
            'exit_ma_value_toggle': ('data.exit_ma_value_toggle', 'checkbox'),
            # exit_variables is a repeater, not handled here
        }
        for k, v in settings.items():
            if k in field_map and v is not None:
                safe_update_field(field_map[k][0], v, field_map[k][1])

        save_btn.click()
        time.sleep(1)
        new_settings = self.get_exit_settings(bot_num)
        if self.verbose:
            print(f'Updated EXIT settings for bot: {bot_num}')
        if initial_settings == new_settings:
            warnings.warn(f'Exit settings are unchanged for bot: {bot_num}')
        return new_settings

    def enable_by_bot_num(self, bot_num: str) -> bool:
        """Enable bot by bot num

        :param bot_num: WhisperTrades bot Number
        :return: Bool value of successful url load
        :rtype: bool
        """
        url = f"https://whispertrades.com/bots/{bot_num}/enable"
        if self.verbose:
            print(f'Enabling bot: {bot_num}')
        return self.__get_url_and_wait(url)

    def force_disable_by_bot_num(self, bot_num: str) -> bool:
        """Disable bot by bot num

        :param bot_num: WhisperTrades bot Number
        :return: Bool value of successful url load
        :rtype: bool
        """

        url = f"https://whispertrades.com/bots/{bot_num}/force_disable?redirectUrl=https%253A%252F%252Fwhispertrades.com%252Fbots"
        if self.verbose:
            print(f'Disabling bot: {bot_num}')
        return self.__get_url_and_wait(url)

    def disable_on_close_by_bot_num(self, bot_num: str) -> bool:
        """Soft disable bot by bot num

        :param bot_num: WhisperTrades bot Number
        :return: Bool value of successful url load
        :rtype: bool
        """
        url = f"https://whispertrades.com/bots/{bot_num}/soft_disable?redirectUrl=https%253A%252F%252Fwhispertrades.com%252Fbots"
        if self.verbose:
            print(f'Disabling on close bot: {bot_num}')
        return self.__get_url_and_wait(url)

    def enabled_to_soft_disabled_by_list(self, bot_num_lst: list[str]) -> None:
        """
        Bot status change: 'Enabled' to 'Disabled on Close'
        :param bot_num_lst: List of WhisperTrades bot Numbers
        :type url: list
        """
        for b in bot_num_lst:
            if not self.disable_on_close_by_bot_num(b):
                warnings.warn(f'UNABLE TO "DISABLE ON CLOSE" BOT_NUM {b}')
        return

    def enabled_to_forced_disabled_by_list(self, bot_num_lst: list[str]) -> None:
        """
        Bot status change: 'Enabled' to 'Disabled'

        :param bot_num_lst: List of WhisperTrades bot Numbers
        :type url: list
        """
        for b in bot_num_lst:
            if not self.force_disable_by_bot_num(b):
                warnings.warn(f'UNABLE TO "DISABLE" BOT_NUM {b}')
        return

    def disabled_to_enabled_by_list(self, bot_num_lst: list[str]) -> None:
        """
        Bot status change: 'Disabled' to 'Enabled'

        :param bot_num_lst: List of WhisperTrades bot Numbers
        :type url: list
        """
        for b in bot_num_lst:
            if not self.enable_by_bot_num(b):
                warnings.warn(f'UNABLE TO "ENABLE" BOT_NUM {b}')
        return

    def force_enabled_by_list(self, bot_num_lst: list[str]) -> None:
        """
        Bot status change: to 'Enabled'

        :param bot_num_lst: List of WhisperTrades bot Numbers
        :type url: list
        """
        for b in bot_num_lst:
            if not self.enable_by_bot_num(b):
                warnings.warn(f'UNABLE TO "ENABLE" BOT_NUM {b}')
        return

    def force_disable_by_list(self, bot_num_lst: list[str]) -> None:
        """
        Bot status change: Any state to 'Disabled'

        :param bot_num_lst: List of WhisperTrades bot Numbers
        :type url: list
        """
        for b in bot_num_lst:
            if not self.force_disable_by_bot_num(b):
                warnings.warn(f'UNABLE TO "DISABLE" BOT_NUM {b}')
        return
    
    def enter_new_position_by_bot_num(self, bot_num: str) -> bool:
        """Enter new position by bot num

        :param bot_num: WhisperTrades bot Number
        :return: Bool value of successful url load
        :rtype: bool
        """
        url = f"https://whispertrades.com/bots/{bot_num}/enter_position"
        if self.verbose:
            print(f'Entering new position on bot: {bot_num}')
        return self.__get_url_and_wait(url)

