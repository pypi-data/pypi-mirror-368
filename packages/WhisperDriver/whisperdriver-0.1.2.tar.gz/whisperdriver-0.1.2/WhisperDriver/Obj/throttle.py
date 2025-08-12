########################################################################################################################
########################################################################################################################
###   Throttle Object for WhisperTrades.com API                                                                      ###
###                                                                                                                  ###
###   Authored by Paul Nobrega   Contact: Paul@PaulNobrega.net                                                       ###
###   Python Version 3.10                                                                                            ###
########################################################################################################################
########################################################################################################################
import time

class WhisperTradesThrottle(object):
    """
    API rate limiter for WhisperTrades.com.

    Attributes:
        delay_sec (int): Delay in seconds between requests.
        is_on (bool): Whether throttling is enabled.
    """
    def __init__(self) -> None:
        self.delay_sec: int = 2
        self.is_on: bool = True
   
    def __call__(self, fxn):
        return self.__run(fxn)

    def __run(self, fxn):
        if self.is_on:
            time.sleep(self.delay_sec)
        return fxn()
    
    def enable(self):
        """
        Toggle throttle to enabled
        """
        if self.is_on == False:
            self.is_on = True
        return 
    
    def disable(self):
        """
        Toggle throttle to disabled
        """
        if self.is_on == True:
            self.is_on = False
        return 
    
    def set_delay_sec(self, sec_delay: int=2):
        """
        Set seconds to delay before each API request

        :sec_delay: seconds to delay before each API request.  Default is 2 seconds to match WhisperTrades API rate limit
        :type sec_delay: int
        """
        self.delay_sec = sec_delay
        return

