import os
import sys
from datetime import datetime
from threading import Thread, Lock
from time import time
from time import sleep

from requests import Session
from signalr import Connection

class EmotivConnection(object):
    """
    Read data from file or hid. Only CSV for now.
    """

    def __init__(self):
        self.hub_url = 'http://localhost:51560/signalr'
        self.hub_name = 'EmokitHub'
        self.connection = None
        self.hub = None
        self.hub_event = 'OnProducerChanged'
        self.stop_connection = False
        self.connection_thread = Thread(target=self.run)
        self.running = False
        self.stop_received = False;
        self.reader_init = False
        self.lock = Lock()

    def start(self):
        """
        Starts the connection thread.
        """
        self.stopped = False
        self.connection_thread.start()

    def stop(self):
        """
        Stops the reader thread.
        """
        self.lock.acquire()
        self._stop_signal = True
        self.lock.release()

    def run(self, source=None):
        with Session() as session:
            #create a connection
            self.connection = Connection(self.hub_url, session)

            #connect to the hub
            self.hub  = self.connection.register_hub(self.hub_name)

            # start the connection
            self.connection.start()
                
            def OnProducerChanged(data):
                if self.stop_received is False:
                    print('received: ', data)
                    """
                    Starts emotiv, called upon initialization.
                    """
                    if data == "start":
                        self.running = True

                    elif data == "stop":
                        self.running = False
                        self.stop_received = True
                        print("Emotiv Stopped")


            #receive new chat messages from the hub
            self.hub.client.on(self.hub_event, OnProducerChanged)

            #create error handler
            def print_signalr_error(error):
                print('error: ', error)

            #process errors
            self.connection.error += print_signalr_error

            #hold the connection (annoying way to do it)
            self.lock.acquire()
            while not self.stop_connection:
                self.lock.release()
                self.connection.wait()
                if(self.reader_init):
                    self.hub.server.invoke("Init");
                    self.reader_init = False
                self.lock.acquire()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
        if self.connection_thread:
            self.connection_thread.close()