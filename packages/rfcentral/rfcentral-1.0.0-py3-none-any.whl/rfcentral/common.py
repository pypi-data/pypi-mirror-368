class GeneralUtil():

    def __init__(self)->None:
        pass

    @classmethod
    def get_freq_power(cls,data:str)->list[str]|None:
        '''
         15.55|65.69(frequency|power)
        '''
        try:
            values:list[str] = data.split("|")
            return values
        except IndexError as ex:
            return None # FIXME needs to log