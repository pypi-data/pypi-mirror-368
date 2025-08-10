class FrequencyPowerTime():

    def __init__(self, frequency:float, power:float, date_time:str) -> None:
        self.frequency = frequency
        self.power = power
        self.date_time = date_time

    def get_all(self)->tuple[float,float,str]:
        return self.frequency, self.power, self.date_time


class Search():
    def __init__(self,freq:tuple[float,float], power:tuple[float,float])->None:
        # doc later. max min
        self.freq = freq
        self.power = power
