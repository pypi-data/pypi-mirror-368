import queue
from threading import Thread

from .db.database import DetailDataBaseManager
from .model import FrequencyPowerTime




class DataBroker():
    q = queue.Queue()

    def __init__(self):
       pass

    def worker(self):
        while True:
            obj = DataBroker.q.get() # blocks until an element found in queue
            # check for the element type
            if isinstance(obj,FrequencyPowerTime):
               data = obj.get_all()
               DetailDataBaseManager.insert_frequency_power(frequency=data[0], power= data[1], date_time= data[2])


    def start(self):
        # Turn on the worker thread
        Thread(target=self.worker, daemon=True).start()





