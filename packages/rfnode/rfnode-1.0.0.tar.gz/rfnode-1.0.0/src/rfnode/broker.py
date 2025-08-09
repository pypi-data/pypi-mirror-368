""" Broker  which works runs in a separate thread 
It reads the queue which get blocked if there is no data
class level attribute broker which get data from the SDR device reader 
Once the data in queue, it is read and send to the Central machine
"""
import logging
import queue
from threading import Thread

from rfnode.model.model import HighPowerFrequency, HighPowerSample
from rfnode.sender.sender import Sender


class DataBroker:
    q = queue.Queue()

    def __init__(self):
        self.logger = logging.getLogger("Broker")

    def set_rf_sender(self, sender: Sender) -> None:
        """ set the sender class which sends the RF data to the Central machine
        Args:
            sender (Sender): The RF sender 
        Returns:
            None: does not return any value
        """
        self.sender = sender

    def worker(self):
        """ loop once the queue is empty this loop block 
             or the thread get blocked await for incoming data to read again
        """
        while True:
            self.logger.info("inside the worker now ..")
            obj = DataBroker.q.get()  # blocks until an element found in queue

            # check for the element type
            if isinstance(obj, HighPowerSample):

                # obj_str = obj.to_json(NumpyComplexEncoder) Alan in V2
                payload: str = (
                    str(round(obj.get_frequency(), 2)) + "|" + str(round(obj.get_power(), 2))
                )
                self.sender.send(payload)
                # self.logger.info(f'Got the HighPowerSample {obj_str}')
            elif isinstance(obj, HighPowerFrequency):
                obj_str = obj.to_json()
                self.logger.info(f" Got the HighPowerFrequency  {obj_str}")

    def start(self):
        # Turn on the worker thread
        Thread(target=self.worker, daemon=True).start()
