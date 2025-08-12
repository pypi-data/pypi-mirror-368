########################################################################################################################
########################################################################################################################
###   Endpoint Objects for WhisperTrades.com API                                                                     ###
###                                                                                                                  ###
###   Authored by Paul Nobrgea   Contact: Paul@PaulNobrega.net                                                       ###
###   Python Version 3.10                                                                                            ###
########################################################################################################################
########################################################################################################################
import requests
from urllib.parse import urljoin
import posixpath
import json
import warnings



class WhisperTradesEndpoints(object):
    """
    Endpoint handler for WhisperTrades.com API.

    Args:
        token (str): API token for authentication.
        throttle (object): Throttle object for rate limiting.
    """
    def __init__(self, token: str, throttle: object) -> None:
        self.throttle: object = throttle
        self.config = self.__config(token)
        self.bots = self.__bots(self.config, self.throttle)
        self.reports = self.__reports(self.config, self.throttle)
        self.variables = self.__variables(self.config, self.throttle)
        self.brokers = self.__brokers(self.config, self.throttle)

    @staticmethod
    def format_response(response):
        """
        Format API responses to JSON and apply rate limit throttle
        """
        txt_to_json = json.loads(response.text)
        if not response.ok:
            msg = txt_to_json['message'] if 'message' in txt_to_json else ''
            warnings.warn(f"Status code: {response.status_code} received with reason: {response.reason} at url: {response.url}\n{msg}")
            if response.reason.lower() == 'unauthorized':
                raise Exception(f'Invalid API token!')
        return txt_to_json['data'] if 'data' in txt_to_json else txt_to_json

    class __config(object):
        def __init__(self, token):
            self.TOKEN = token
            self.SERVER = r'https://api.whispertrades.com/v1/'
            self.HEADERS = {'Accept': 'application/json', 'Content-Type': 'application/json', 'authorization': f'Bearer {self.TOKEN}'}
    
    class __bots(object):
    
        def __init__(self, config, throttle):
            self.endpt = r'bots/'
            self.config = config
            self._throttle = throttle
    
        def get_bot_orders(self, bot_number: str) -> json:
            """
            Get all orders for a specific bot by bot_number.

            :param bot_number: number of bot.
            :type bot_number: String

            :return: json data from response received from WhisperTrades API
            :type return: json
            """
            if not bot_number:
                raise ValueError("Bot number is required to get orders.")
            url_path = urljoin(self.config.SERVER, posixpath.join(self.endpt, bot_number, 'orders'))
            payload = {}
            response = self._throttle(lambda: requests.request("GET", url_path, headers=self.config.HEADERS, data=payload))
            return WhisperTradesEndpoints.format_response(response)

        def get_bot_positions(self, bot_number: str = '', position_number: str = '', status: str = '', from_date: str = '', to_date: str = '', page: str = '') -> json:
            """
            Get a paginated list of bot positions, or a single position if position_number is provided.

            :param bot_number: Bot number to filter positions (optional)
            :param position_number: Unique position number to retrieve a single position (optional)
            :param status: Filter by position status (OPEN or CLOSED, optional)
            :param from_date: Minimum entry date (YYYY-MM-DD, optional)
            :param to_date: Maximum entry date (YYYY-MM-DD, optional)
            :param page: Page number (optional)
            :return: json data from response received from WhisperTrades API
            """
            if position_number:
                url_path = urljoin(self.config.SERVER, posixpath.join('bots/positions', position_number))
                params = {}
            else:
                url_path = urljoin(self.config.SERVER, 'bots/positions')
                params = {}
                if bot_number:
                    params['bot'] = bot_number
                if status:
                    params['status'] = status
                if from_date:
                    params['from_date'] = from_date
                if to_date:
                    params['to_date'] = to_date
                if page:
                    params['page'] = page
            response = self._throttle(lambda: requests.request("GET", url_path, params=params, headers=self.config.HEADERS))
            return WhisperTradesEndpoints.format_response(response)

        def close_bot_position(self, position_number: str) -> json:
            """
            Close a specific bot position by position number.

            :param position_number: Position number to close
            :return: json data from response received from WhisperTrades API
            """
            if not position_number:
                raise ValueError("Position number is required to close a bot position.")
            url_path = urljoin(self.config.SERVER, posixpath.join('bots/positions', position_number, 'close'))
            response = self._throttle(lambda: requests.request("PUT", url_path, headers=self.config.HEADERS))
            return WhisperTradesEndpoints.format_response(response)

        def get_bot(self, bot_number: str='', status_filter: list=['Enabled', 'Disabled', 'Disable on Close'], include_details: bool=True) -> json:
            """
            Query WhisperTrades.com for bot information at endpoint: 'bots/' 

            :param bot_number: number of bot. Default = '' to return all bot information
            :type bot_number: String
            :param status_filter: Empty list or list containing any combination of: 'Enabled', ' Disabled', 'Disabled on Close'. Default = [] to apply no filter
            :type password: List
            :param include_details: Include all bot settings. Default = True
            :type include_details: Boolean

            :return: json data from response received from WhisperTrades API
            :type return: json
            """
            url_path = urljoin(self.config.SERVER, posixpath.join(self.endpt, bot_number))
            payload={}
            params = {'include_details':include_details, 'statuses[]': status_filter}
            response = self._throttle(lambda: requests.request("GET", url_path, params=params, headers=self.config.HEADERS, data=payload))
            return WhisperTradesEndpoints.format_response(response)
        
        def get_all_bots(self) -> json:
            """
            Query WhisperTrades.com for ALL bot information at endpoint: 'bots/' 

            :return: json data from response recieved from WhisperTrades API
            :type return: json
            """
            return self.get_bot(bot_number='', status_filter=[])
        
        def enable_bot(self, bot_number:str) -> json:
            """
            Enable WhisperTrades.com bot by bot_number 

            :param bot_number: number of bot. Default = '' to return all bot information
            :type bot_number: String

            :return: json data from response recieved from WhisperTrades API
            :type return: json
            """
            url_path = urljoin(self.config.SERVER, posixpath.join(self.endpt, bot_number,'enable'))
            payload={}
            response = self._throttle(lambda: requests.request("PUT", url_path, headers=self.config.HEADERS, data=payload))
            return WhisperTradesEndpoints.format_response(response)

        def disable_bot(self, bot_number:str) -> json:
            """
            Disable WhisperTrades.com bot by bot_number.  If bot has open positions, status will be set to 'Disable on Close'

            :param bot_number: number of bot. Default = '' to return all bot information
            :type bot_number: String

            :return: json data from response recieved from WhisperTrades API
            :type return: json
            """
            url_path = urljoin(self.config.SERVER, posixpath.join(self.endpt, bot_number,'disable'))
            payload={}
            response = self._throttle(lambda: requests.request("PUT", url_path, headers=self.config.HEADERS, data=payload))
            return WhisperTradesEndpoints.format_response(response) 

        def open_position(self, bot_number: str) -> json:
            """
            Open a position for the specified bot.

            :param bot_number: number of bot.
            :type bot_number: String

            :return: json data from response received from WhisperTrades API
            :type return: json
            """
            url_path = urljoin(self.config.SERVER, posixpath.join(self.endpt, bot_number, 'open_position'))
            payload = {}
            response = self._throttle(lambda: requests.request("PUT", url_path, headers=self.config.HEADERS, data=payload))
            return WhisperTradesEndpoints.format_response(response)

        def close_position(self, bot_number: str) -> json:
            """
            Close a position for the specified bot.

            :param bot_number: number of bot.
            :type bot_number: String

            :return: json data from response received from WhisperTrades API
            :type return: json
            """
            url_path = urljoin(self.config.SERVER, posixpath.join(self.endpt, bot_number, 'close_position'))
            payload = {}
            response = self._throttle(lambda: requests.request("PUT", url_path, headers=self.config.HEADERS, data=payload))
            return WhisperTradesEndpoints.format_response(response)

    class __reports(object):
        
        def __init__(self, config, throttle):
            self.endpt = r'bots/reports/'
            self.config = config
            self._throttle = throttle
        
        def get_bot_report(self, report_number: str='') -> json:
            """
            Query WhisperTrades.com for report by report_number.

            :param report_number: number of report. Default = '' to return all report information
            :type report_number: String

            :return: json data from response recieved from WhisperTrades API
            :type return: json
            """
            url_path = urljoin(self.config.SERVER, posixpath.join(self.endpt, report_number))
            payload={}
            response = self._throttle(lambda: requests.request("GET", url_path, headers=self.config.HEADERS, data=payload))
            return WhisperTradesEndpoints.format_response(response)
        
        def get_all_bot_reports(self) -> json:
            """
            Query WhisperTrades.com for ALL reports.

            :return: json data from response recieved from WhisperTrades API
            :type return: json
            """
            return self.get_bot_report('')
        
        def update_bot_report(self, report_number: str, new_name:str = '', new_start_date:str='', new_end_date:str='', run_until_latest_date:bool=False) -> json:
            """
            Query WhisperTrades.com for report by report_number.
            
            Required
            :param report_number: number of report.
            :type report_number: String

            Optional
            :param new_name: New name to rename report as
            :type new_name: String
            :param new_start_date: New start date for the report. Expected format is 'YYYY-MM-DD'
            :type new_start_date: String
            :param new_end_date: New end date for the report. Expected format is 'YYYY-MM-DD'
            :type new_end_date: String
            :param run_until_latest_date: Run report until current date if True. Default = False
            :type run_until_latest_date: Boolean

            :return: json data from response recieved from WhisperTrades API
            :type return: json
            """
            url_path = urljoin(self.config.SERVER, posixpath.join(self.endpt, report_number))
            payload = {
                "name": new_name,
                "start_date": new_start_date,
                "end_date": new_end_date,
                "run_until_latest_date": run_until_latest_date
                }
            
            for key in payload:
                if payload[key] == '':
                    del payload[key]

            response = self._throttle(lambda: requests.request("PUT", url_path, headers=self.config.HEADERS, data=json.dumps(payload)))
            return WhisperTradesEndpoints.format_response(response)
        
        def run_bot_report(self, report_number:str=''):
            """
            Run report at WhisperTrades.com by report_number.
            
            Required
            :param report_number: number of report.
            :type report_number: String

            :return: json data from response recieved from WhisperTrades API
            :type return: json
            """

            if report_number == '':
                raise ValueError(f"Insufficient information supplied to run report! (REQUIRED) report_number: {report_number}")
            url_path = urljoin(self.config.SERVER, posixpath.join(self.endpt, report_number,'run'))
            payload={}
            response = self._throttle(lambda: requests.request("PUT", url_path, headers=self.config.HEADERS, data=payload))
            return WhisperTradesEndpoints.format_response(response)
    
    class __variables(object):
        
        def __init__(self, config, throttle):
            self.endpt = r'bots/variables/'
            self.config = config
            self._throttle = throttle
        
        def get_bot_variables(self, variable_number:str='') -> json:
            """
            Query WhisperTrades.com for variable by variable_number.

            :param variable_number: number of variable. Default = '' to return all variable information
            :type variable_number: String

            :return: json data from response recieved from WhisperTrades API
            :type return: json
            """
            url_path = urljoin(self.config.SERVER, posixpath.join(self.endpt, variable_number))
            payload={}
            response = self._throttle(lambda: requests.request("GET", url_path, headers=self.config.HEADERS, data=payload))
            return WhisperTradesEndpoints.format_response(response)
        
        def get_all_bot_variables(self) -> json:
            """
            Query WhisperTrades.com for ALL variables.

            :return: json data from response recieved from WhisperTrades API
            :type return: json
            """
            return self.get_bot_variables('')
        
        def set_bot_variables(self, variable_number:str='', variable_name:str='', new_value:str='') -> json:
            """
            Set WhisperTrades.com variable by name to new given value.

            REQUIRED
            :param variable_number: number of variable.
            :type variable_number: String
            :param variable_name: name of variable.
            :type variable_name: String
            :param new_value: new 'free text type' value to associate with variable name.
            :type new_value: String

            :return: json data from response recieved from WhisperTrades API
            :type return: json
            """
            if variable_number == '' or variable_name == '' or new_value == '':
                raise ValueError(f"Insufficient information supplied to set bot variable! (REQUIRED) variable_number: {variable_number}, (REQUIRED) variable_name: {variable_name}, (REQUIRED) new_value: {new_value}")
            url_path = urljoin(self.config.SERVER, posixpath.join(self.endpt, variable_number))
            payload = json.dumps({"name": variable_name, "value": new_value})
            response = self._throttle(lambda: requests.request("PUT", url_path, headers=self.config.HEADERS, data=payload))
            return WhisperTradesEndpoints.format_response(response)
    
    class __brokers(object):
        
        def __init__(self, config, throttle):
            self.endpt = r'broker_connections/'
            self.config = config
            self._throttle = throttle
        
        def get_broker_connections(self, number: str = '') -> json:
            """
            Get a single broker connection or a list of all broker connections.

            :param number: Unique identifier to retrieve a single broker connection. If omitted, all broker connections will be returned.
            :type number: String

            :return: json data from response received from WhisperTrades API
            :type return: json
            """
            url_path = urljoin(self.config.SERVER, posixpath.join(self.endpt, number))
            payload = {}
            response = self._throttle(lambda: requests.request("GET", url_path, headers=self.config.HEADERS, data=payload))
            data = WhisperTradesEndpoints.format_response(response)
            # Remove any broker connections with 'broker': 'TD Ameritrade' as broker is no longer valid
            if isinstance(data, list):
                data = [d for d in data if d.get('broker', '').lower() != 'td ameritrade']
            elif isinstance(data, dict) and data.get('broker', '').lower() == 'td ameritrade':
                return None
            return data

        def get_all_broker_connections(self) -> json:
            """
            Get a list of all broker connections.

            :return: json data from response received from WhisperTrades API
            :type return: json
            """
            return self.get_broker_connections('')

        def rebalance_broker_collateral(self, number: str) -> json:
            """
            Rebalance your collateral position for a given broker connection.
            This requires that the collateral be configured and enabled at Whispertrades.
            If your current collateral balance is within the minimum and maximum target amounts, a transaction will not happen.

            :param number: Unique identifier for the broker connection to rebalance
            :type number: String

            :return: json data from response received from WhisperTrades API
            :type return: json
            """
            if not number:
                raise ValueError("Broker connection number is required for collateral rebalance.")
            url_path = urljoin(self.config.SERVER, posixpath.join(self.endpt, number, 'collateral', 'rebalance'))
            payload = {}
            response = self._throttle(lambda: requests.request("PUT", url_path, headers=self.config.HEADERS, data=payload))
            return WhisperTradesEndpoints.format_response(response)