'''
$ sqlitebrowser
to run the client
see https://sqlitebrowser.org/dl/

sqllite:
https://docs.python.org/3/library/sqlite3.html

'''

import sqlite3
import os.path
from pathlib import Path

s = os.path.dirname(__file__)
p = Path(s).parent.parent.parent.joinpath("database")

class RowDataBaseManager():
    db_raw_path = str(p) + os.path.sep + "raw.db" # raw database

    def __init__(self)->None:
        pass

    @classmethod
    def insert_high_power_frequency(cls,data:str)->None:
        con = sqlite3.connect(cls.db_raw_path)
        cur = con.cursor()
        cur.execute("INSERT INTO HighPowerFrequency VALUES(NULL,?)", (data,))
        con.commit()
        con.close() # not effecient

    @classmethod
    def insert_high_power_sample(cls,data:str)->None:
        con = sqlite3.connect(cls.db_raw_path)
        cur = con.cursor()
        cur.execute("INSERT INTO HighPowerSample VALUES(NULL,?)", (data,))
        con.commit()
        con.close() # not effecient


class DetailDataBaseManager():
    db_detail_path = str(p) + os.path.sep + "detail.db" # detail database

    def __init__(self)->None:
        pass

    @classmethod
    def insert_frequency_samples(cls,frequency:float, power:float, date_time:str, samples:list[complex])->None:
        # power, frequency and samples for the center frequency v2
        con = sqlite3.connect(cls.db_detail_path)
        cur = con.cursor()
        cur.execute("INSERT INTO Frequency VALUES(NULL,?,?,?)", (frequency,power, date_time))
        primary_key = cur.lastrowid
        if(primary_key):
            data = cls.__convert__(primary_key=primary_key,samples=samples)
            cur.executemany("INSERT INTO FrequencySamples VALUES(NULL,?,?,?)",data)
            con.commit()
        else:
            con.rollback() # FIXME add log warning

        con.close()

    @classmethod
    def insert_frequency_power(cls,frequency:float, power:float, date_time:str)->None:
        # power, frequency v1
        con = sqlite3.connect(cls.db_detail_path)
        cur = con.cursor()
        cur.execute("INSERT INTO Frequency VALUES(NULL,?,?,?)", (frequency,power, date_time))
        con.commit()
        con.close()

    @classmethod
    def __convert__(cls, primary_key:int, samples:list[complex])->list[tuple[int,float,float]]:
        lst = []
        for x in samples:
           var = (primary_key,x.real,x.imag)
           lst.append(var)

        return lst

    @classmethod
    def insert_power_frequencies(cls, power: float, date_time:str, frequencies: list[float]):
        con = sqlite3.Connection(cls.db_detail_path)
        cur = con.cursor()
        cur.execute("INSERT INTO Power VALUES(NULL,?,?)",(power,date_time))
        primary_key = cur.lastrowid
        lst = []
        for x in frequencies:
            var = (primary_key,x)
            lst.append(var)

        cur.executemany("INSERT INTO PowerFrequencies VALUES(NULL,?,?)",lst)
        con.commit()
        con.close()






if __name__ == '__main__':
    #RowDataBaseManager.insert_high_power_frequency("High power frequency")
    #RowDataBaseManager.insert_high_power_sample("High power sample")
    power:float = 50.55
    frequency = 105.55
    lst = []
    c:complex = complex(2.0,1.333)
    lst.append(c)
    date_time="25-05-04 13:33:10"
    #v2 DetailDataBaseManager.insert_frequency_samples(frequency=frequency,power=power,date_time=date_time,samples=lst)
    DetailDataBaseManager.insert_frequency_power(frequency=frequency, power=power, date_time=date_time)
    #v2 frequencies = [105.55,106.44,107.68,108.68]
    # v2 DetailDataBaseManager.insert_power_frequencies(power,date_time,frequencies)s



