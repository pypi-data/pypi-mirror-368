########################################################################################################################
########################################################################################################################
###   Bot Objects for WhisperTrades.com API                                                                          ###
###                                                                                                                  ###
###   Authored by Paul Nobrega   Contact: Paul@PaulNobrega.net                                                       ###
###   Python Version 3.10                                                                                            ###
########################################################################################################################
########################################################################################################################
import json
import warnings
from datetime import datetime


class WhisperTradesBots(object):
    """
    Bot handler for WhisperTrades.com API.

    Args:
        scheduler (object): Scheduler object for bot scheduling and endpoint access.
    """
    def __init__(self, scheduler: object) -> None:
        self._scheduler: object = scheduler
        self._endpts = self._scheduler._endpts
        self.bots_list = self.__bot_list(self._scheduler)

    def __call__(self, bot_number):
        for bot in self.bots_list.all:
            if bot.number == bot_number:
                return bot
        warnings.warn(f"Bot Number: {bot_number} not found!")
        return
       
    def get_all_bot_variables(self) -> json:
        """
        Query WhisperTrades.com for all bot variables and associate data with related bot object
       
        :return: json data from response recieved from WhisperTrades API
        :type return: json
        """
        all_variables = self._endpts.variables.get_all_bot_variables()
        for var in all_variables:
            for bot in self.bots_list.all:
                for i, bot_var in enumerate(bot.variables):
                    if bot_var['number'] == var['number']:
                        bot.variables[i] = var
        return all_variables
    
    def update_all_bots(self):
        """
        Update bots_list with data retrieved from WHisperTrades.com API
        """
        self.bots_list.all = []
        _ = [self.bots_list.add_bot_to_list(bot) for bot in self._endpts.bots.get_all_bots()]
        return

    class __bot_list(object):
        def __init__(self, scheduler):
            self.all = []
            self._scheduler = scheduler
            self._endpts = self._scheduler._endpts
        
        def __call__(self):
            """
            Return list of all bot numbers
            """
            return self.all
        
        def all(self) -> list:
            """
            Return list of all bot numbers
            """
            return self.all
        
        def is_enabled(self) -> list:
            """
            Return list of all bot numbers that have status = 'enabled'
            """
            return [bot for bot in self.all if bot.status.lower() == 'enabled']
        
        def is_disabled(self) -> list:
            """
            Return list of all bot numbers that have status = 'disabled'
            """
            return [bot for bot in self.all if bot.status.lower() == 'disabled']
        
        def is_disabled_on_close(self) -> list:
            """
            Return list of all bot numbers that have status = 'disabled on close'
            """
            return [bot for bot in self.all if bot.status.lower() == 'disabled on close']
        
        def add_bot_to_list(self, bot_dict:dict={}):
            """
            Add dictionary representation of a WT bot to bot_list.all

            Note: if bot_number exists in bot_list.all, it is removed and replaced with the new information
            """
            if bot_dict=={}:
                warnings.warn(f'bot_dict is empty!')
                return
            bot_json = json.loads(json.dumps(bot_dict))
            self.remove_bot_from_list(bot_json['number'])
            self.all.append(self.bot_obj(bot_json, self._scheduler))
            return
        
        def remove_bot_from_list(self, bot_number:str):
            """
            Removes bot from bots.all list by given bot number
            """
            for i in range(len(self.all)):
                if self.all[i].number == bot_number:
                    del self.all[i]
                    return
            return


        class bot_obj(object):
            
            def __init__(self, bot_dict, scheduler):
                self.number = ''
                self.name = ''
                self.broker_connection = {}
                self.is_paper= False
                self.status = ''
                self.can_enable = True
                self.can_disable = True
                self.symbol = ''
                self.type = ''
                self.notes = ''
                self.last_active_at = ''
                self.disabled_at = ''
                self.entry_condition = {}
                self.exit_condition = {}
                self.adjustments = []
                self.notifications = []
                self.variables = []
                self._scheduler = scheduler
                self._endpts = self._scheduler._endpts
                self.__bot_dict_to_attr(bot_dict)
            
            def enable(self):
                """
                Enable the bot.
                """
                return self._change_status('enable', self.number, self._endpts, self._scheduler)

            def disable(self):
                """
                Disable the bot.
                """
                return self._change_status('disable', self.number, self._endpts, self._scheduler)

            def get_positions(self, position_number: str = '', status: str = '', from_date: str = '', to_date: str = '', page: str = ''):
                """
                Get all positions for this bot, or a single position if position_number is provided.
                """
                return self._endpts.bots.get_bot_positions(
                    bot_number=self.number,
                    position_number=position_number,
                    status=status,
                    from_date=from_date,
                    to_date=to_date,
                    page=page
                )

            def close_position_by_number(self, position_number: str):
                """
                Close a specific position by position number for this bot.
                """
                return self._endpts.bots.close_bot_position(position_number)
            
            def get_orders(self):
                """
                Get all orders for this bot using the API endpoint.
                """
                return self._endpts.bots.get_bot_orders(self.number)
            def open_position(self):
                """
                Open a position for this bot using the API endpoint.
                """
                return self._endpts.bots.open_position(self.number)

            def close_position(self):
                """
                Close a position for this bot using the API endpoint.
                """
                return self._endpts.bots.close_position(self.number)
           
            def __str__(self):
                attrs = vars(self)
                test = [f'{item[0]}: {str(item[1])}' for item in attrs.items()]
                return "\n".join(test)
            
            def __repr__(self):
                return self.__str__()
            
            def __bot_dict_to_attr(self, bot_dict):
                for key in bot_dict: 
                    setattr(self, key, bot_dict[key])
            
            def update(self):
                """
                Query WhisperTrades.com for bot information and update object with new information 
                """
                bot_dict = self._endpts.bots.get_bot(bot_number=self.number)
                self.__bot_dict_to_attr(json.loads(json.dumps(bot_dict)))
                return
            
            def get_bot_variables(self):
                """
                Query WhisperTrades.com for variables associated with bot and update object with new information 
                """
                all_var = [v['number'] for v in self.variables]
                self.variables = []
                self.variables = [self._endpts.variables.get_bot_variables(v) for v in all_var]
                return self.variables
            
            class _change_status(object):

                def __init__(self, target_status, bot_number, endpts, scheduler):
                    self._endpts = endpts
                    self._scheduler = scheduler
                    self._target_status = target_status
                    self._bot_number = bot_number

                def __call__(self):
                    return self._toggle_status()
                
                def _toggle_status(self):
                    if self._target_status == 'enable':
                        print(f"Enabling bot: {self._bot_number}")
                        return self._endpts.bots.enable_bot(self._bot_number)
                    elif self._target_status == 'disable':
                        print(f"Disabling bot: {self._bot_number}")
                        return self._endpts.bots.disable_bot(self._bot_number)
                    return
                
                def _meridian_time_to_military_time(self, time_str):
                    from WhisperDriver.utils.time import get_hour_minute_ampm_format
                    return datetime.strptime(time_str, get_hour_minute_ampm_format()).strftime('%H:%M')

                def at_time(self, time_str=None, tz_str='America/New_York'):
                    """
                    Schedule bot status change.
                    
                    :param time_str: string representation of military time (example: '22:30'). If 12-hr format, PM or AM must be included in string.
                    :type time_str: String
                    :param tz_str: human readable TimeZone. Default is 'America/New_York'
                    :type tz_str: String
                    """
                    if not time_str or not isinstance(time_str, str):
                        raise ValueError('Time input string is required!')
                    if 'pm' in time_str.lower() or 'am' in time_str.lower():
                        time_str = self._meridian_time_to_military_time(time_str)
                    if not self._scheduler.scheduler_is_on:
                        self._scheduler.start()
                    self._scheduler.add_task(time_str, tz_str, self._toggle_status)
                    return
                    



    