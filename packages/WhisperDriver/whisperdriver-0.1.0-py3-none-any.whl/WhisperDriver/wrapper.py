########################################################################################################################
# WhisperDriver: Python Wrapper for WhisperTrades.com API
#
# Author: Paul Nobrega   Contact: Paul@PaulNobrega.net
# Python Version: 3.10+
#
# This module provides a high-level Python interface to the WhisperTrades.com API, including
# bots, variables, reports, scheduling, and browser automation via Selenium.
#
# Usage Example:
#   from WhisperDriver import ApiWrapper
#   api = ApiWrapper(token="YOUR_API_TOKEN")
#   api.update_all_bots_list()
#   print(api.bot_number_list)
#
# Released under the MIT License.
########################################################################################################################

from . import Obj
import time
from typing import List, Optional

class ApiWrapper:
    """
    Main interface for interacting with the WhisperTrades.com API.

    Attributes:
        throttle: API rate limiter.
        endpts: Endpoint handler for all API endpoints.
        scheduler: Scheduler for timed tasks.
        bots: Bot management interface.
        variables: Variable management interface.
        via_selenium: Selenium-based UI automation interface.
        bot_number_list: List of all bot numbers.
        report_number_list: List of all report numbers.
        variable_number_list: List of all variable numbers.
    """
    def __init__(self, token: str):
        """
        Initialize the API wrapper with a WhisperTrades API token.

        Args:
            token (str): WhisperTrades.com API token.
        """
        self.throttle = Obj.WhisperTradesThrottle()
        self.throttle.disable()
        self.endpts = Obj.WhisperTradesEndpoints(token, self.throttle)
        self.scheduler = Obj.WhisperTradesScheduler(self.endpts)
        self.bots = Obj.WhisperTradesBots(self.scheduler)
        self.variables = Obj.WhisperTradesVariables(self.endpts)
        self.via_selenium = Obj.SeleniumDriver(self.endpts)
        self.bot_number_list: List[str] = []
        self.report_number_list: List[str] = []
        self.variable_number_list: List[str] = []
        self.__populate()
        self.throttle.enable()

    def __del__(self):
        """
        Ensure the scheduler thread is stopped before object destruction.
        """
        while self.scheduler.scheduler_is_on:
            time.sleep(1)
        return

    def __populate(self) -> None:
        """
        Populate all bot, report, and variable lists from the API.
        """
        self.update_all_bots_list()
        self.update_all_reports_list()
        self.update_all_variables_list()
        return

    def update_all_bots_list(self) -> None:
        """
        Update the list of bot numbers via the WhisperTrades API.
        """
        self.bots.update_all_bots()
        self.bot_number_list = [i.number for i in self.bots.bots_list.all]
        return

    def update_all_reports_list(self) -> None:
        """
        Update the list of report numbers via the WhisperTrades API.
        """
        self.report_number_list = [i['number'] for i in self.endpts.reports.get_all_bot_reports()]
        return

    def update_all_variables_list(self) -> None:
        """
        Update the list of variable numbers via the WhisperTrades API.
        """
        self.variable_number_list = [i['number'] for i in self.endpts.variables.get_all_bot_variables()]
        return

    def start_scheduler(self) -> None:
        """
        Start the scheduler loop in a unique thread. Thread automatically started at instantiation.
        """
        self.scheduler.start()
        return

    def stop_scheduler(self) -> None:
        """
        Stop the scheduler loop thread.
        """
        self.scheduler.stop()
        return

    def stop_scheduler_at_time(self, time_str: Optional[str] = None, tz_str: str = 'America/New_York') -> None:
        """
        Stop the scheduler thread at a predefined time.

        Args:
            time_str (Optional[str]): String representation of military time (e.g., '22:30'). If 12-hr format, PM or AM must be included.
            tz_str (str): Human-readable timezone. Default is 'America/New_York'.
        """
        self.scheduler.stop_scheduler_at_time(time_str, tz_str)
        return
        self.variable_number_list = [i['number'] for i in self.endpts.variables.get_all_bot_variables()]
    
    def start_scheduler(self):
        """
        Start Scheduler loop in unique thread.  Thread automatically started at instantiation
        """
        self.scheduler.start()
        return 
    
    def stop_scheduler(self):
        """
        Stop Scheduler loop thread.
        """
        self.scheduler.stop()
        return
    
    def stop_scheduler_at_time(self, time_str: str=None, tz_str: str='America/New_York'):
        """
        Stop Scheduler thread at predefined time.
        
        :param time_str: string representation of military time (example: '22:30'). If 12-hr format, PM or AM must be included in string.
        :type time_str: String
        :param tz_str: human readable TimeZone. Default is 'America/New_York'
        :type tz_str: String
        """
        self.scheduler.stop_scheduler_at_time(time_str, tz_str)
        return

