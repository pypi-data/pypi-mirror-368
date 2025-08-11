########################################################################################################################
########################################################################################################################
###   Scheduler Object for WhisperTrades.com API                                                                     ###
###                                                                                                                  ###
###   Authored by Paul Nobrega   Contact: Paul@PaulNobrega.net                                                       ###
###   Python Version 3.10                                                                                            ###
########################################################################################################################
########################################################################################################################
import schedule
from datetime import datetime
from WhisperDriver.utils.time import get_hour_minute_ampm_format
import time
from threading import Thread

class WhisperTradesScheduler(object):
    """
    Scheduler for WhisperTrades.com API bot actions.

    Args:
        endpts (object): Endpoints object for API access.
    """
    def __init__(self, endpts: object) -> None:
        self._endpts: object = endpts
        self.scheduler_is_on: bool = False
        self.__scheduler = None
   
    def __del__(self):
        self.stop()
        return

    def __schedule_loop(self):
        while self.scheduler_is_on:
            schedule.run_pending()
            time.sleep(1)
        return
    
    def start(self):
        """
        Start Scheduler loop in unique thread.  Thread automatically started at instantiation
        """
        if self.scheduler_is_on == False:
            self.scheduler_is_on = True
            self.__scheduler = None
            self.__scheduler = Thread(target=self.__schedule_loop)
            self.__scheduler.start()
        return 
    
    def stop(self):
        """
        Stop Scheduler loop thread.
        """
        if self.scheduler_is_on == True:
            schedule.clear()
            self.scheduler_is_on = False
            time.sleep(1)
        return
    
    def stop_scheduler_at_time(self, time_str: str=None, tz_str: str='America/New_York'):
        """
        Stop Scheduler thread at predefined time.
        
        :param time_str: string representation of military time (example: '22:30'). If 12-hr format, PM or AM must be included in string.
        :type time_str: String
        :param tz_str: human readable TimeZone. Default is 'America/New_York'
        :type tz_str: String
        """
        if not time_str or not isinstance(time_str, str):
            raise ValueError('Time input string is required!')
        if 'pm' in time_str.lower() or 'am' in time_str.lower():
            time_str = datetime.strptime(time_str, get_hour_minute_ampm_format()).strftime('%H:%M')
        self.start()
        schedule.every().day.at(time_str, tz_str).do(self.stop)
        return

    def add_task(self, time_str: str=None, tz_str: str='America/New_York', fxn=None):
        """
        Add Task to scheduler.
        
        :param time_str: string representation of military time (example: '22:30'). If 12-hr format, PM or AM must be included in string.
        :type time_str: String
        :param tz_str: human readable TimeZone. Default is 'America/New_York'
        :type tz_str: String
        :param fxn: function to execute
        :type tz_str: python function
        """
        if not time_str or not isinstance(time_str, str):
            raise ValueError('Time input string is required!')
        if 'pm' in time_str.lower() or 'am' in time_str.lower():
            time_str = datetime.strptime(time_str, get_hour_minute_ampm_format()).strftime('%H:%M')
        schedule.every().day.at(time_str, tz_str).do(fxn)
        return

