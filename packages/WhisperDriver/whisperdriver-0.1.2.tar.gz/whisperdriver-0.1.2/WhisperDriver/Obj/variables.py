########################################################################################################################
########################################################################################################################
###   Variable Object for WhisperTrades.com API                                                                      ###
###                                                                                                                  ###
###   Authored by Paul Nobrega   Contact: Paul@PaulNobrega.net                                                       ###
###   Python Version 3.10                                                                                            ###
########################################################################################################################
########################################################################################################################
import json
import warnings

class WhisperTradesVariables(object):
    """
    Handles bot/global variable API actions for WhisperTrades.com.

    Args:
        endpts (object): Endpoints object for API calls.
    """
    def __init__(self, endpts: object) -> None:
        self._endpts: object = endpts
        self.unassociated_variable_numbers: list = []
        self.variables_list = self.__variable_list(self._endpts)
        self.update_all_variables()
    
    
    def update_all_variables(self):
        """
        Update variabless_list with data retrieved from WhisperTrades.com API
        """
        self.variables_list.all = []
        _ = [self.variables_list.add_variable_to_list(vari) for vari in self._endpts.variables.get_all_bot_variables()]
        self.unassociated_variable_numbers = [vari.number for vari in self.variables_list.all if vari.bot is None]
        return
    

    class __variable_list(object):
            def __init__(self, endpts):
                self.all = []
                self._endpts = endpts
            
            def all(self) -> list:
                """
                Return list of all bot numbers
                """
                return self.all
            
            def add_variable_to_list(self, variable_dict:dict={}):
                """
                Add dictionary representation of a WT variable to variable_list.all

                Note: if variable_number exists in variables_list.all, it is removed and replaced with the new information
                """
                if variable_dict=={}:
                    warnings.warn(f'variable_dict is empty!')
                    return
                vari_json = json.loads(json.dumps(variable_dict))
                self.remove_variable_from_list(vari_json['number'])
                self.all.append(self.vari_obj(vari_json, self._endpts))
                return
            
            def remove_variable_from_list(self, variable_number:str):
                """
                Removes variable from variables_list.all list by given variable number
                """
                for i in range(len(self.all)):
                    if self.all[i].number == variable_number:
                        del self.all[i]
                        return
                return

            class vari_obj(object):
                
                def __init__(self, vari_dict, endpts):
                    self.number = ''
                    self.name = ''
                    self.bot = ''
                    self.value= ''
                    self.free_text_value = ''
                    self.last_updated_at = ''
                    self.conditions = []
                    self._endpts = endpts
                    self.__vari_dict_to_attr(vari_dict)
            
                def __str__(self):
                    attrs = vars(self)
                    test = [f'{item[0]}: {str(item[1])}' for item in attrs.items()]
                    return "\n".join(test)
                
                def __repr__(self):
                    return self.__str__()
                
                def __vari_dict_to_attr(self, vari_dict):
                    for key in vari_dict: 
                        setattr(self, key, vari_dict[key])
                
                def update(self):
                    """
                    Query WhisperTrades.com for bot information and update object with new information 
                    """
                    vari_dict = self._endpts.variables.get_bot_variables(variable_number = self.number)
                    self.__vari_dict_to_attr(json.loads(json.dumps(vari_dict)))
                    return
                
                def set(self, new_value:str='') -> json:
                    """
                    Set 'unassociated' bot variables via WhisperTrades.com, update object with new information, return json

                    REQUIRED
                    :param new_value: new 'free text type' value to associate with variable name.
                    :type variable_number: String

                    :return: json data from response received from WhisperTrades API
                    :type return: json
                    """
                    vari_dict = self._endpts.variables.set_bot_variables(variable_number=self.number, variable_name=self.name, new_value=new_value)
                    self.__vari_dict_to_attr(json.loads(json.dumps(vari_dict)))
                    return vari_dict



        