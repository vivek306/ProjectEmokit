# -*- coding: utf-8 -*-
import os
import time
from threading import Thread, Lock
import json
import requests


from .python_queue import Queue
from .sensors import sensors_mapping
from .util import get_quality_scale_level, system_platform


class EmotivMeVitaeOutput(object):
    """
        Write output to console.
    """

    def __init__(self, serial_number="", old_model=False, as_json = False, single_call = False, era_output = False):
        self.tasks = Queue()
        self.running = True
        self.stopped = False
        self.packets_received = 0
        # The number of times data was decrypted or made into EmotivPackets.
        self.packets_processed = 0
        self._stop_signal = False
        self.serial_number = serial_number
        self.old_model = old_model
        self.lock = Lock()
        self.thread = Thread(target=self.run)
        self.thread.setDaemon(True)
        self.as_json = as_json
        self.single_call = single_call

    def start(self):
        """
        Starts the writer thread.
        """
        self.running = True
        self.stopped = False
        self.thread.start()

    def stop(self):
        """
        Stops the writer thread.
        """
        self.lock.acquire()
        self._stop_signal = True
        self.lock.release()

    def run(self, source=None):
        """Do not call explicitly, called upon initialization of class"""
        # self.lock.acquire()
        dirty = False
        tick_time = time.time()
        last_packets_received = 0
        last_packets_decrypted = 0
        packets_received_since_last_update = 0
        packets_processed_since_last_update = 0
        battery = 0
        run_once = False
        last_sensors = sensors_mapping.copy()
        print("Emotiv Start")
        self.lock.acquire()
        while self.running:
            self.lock.release()
            while not self.tasks.empty() and not run_once:
                next_task = self.tasks.get_nowait()
                if next_task.packet_received:
                    self.packets_received += 1

                if next_task.packet_decrypted:
                    self.packets_processed += 1
                    if next_task.packet_data.battery is not None:
                        last_sensors = next_task.packet_data.sensors
                        battery = next_task.packet_data.battery

                # if time.time() - tick_time > 1:
                tick_time = time.time()
                packets_received_since_last_update = self.packets_received - last_packets_received
                packets_processed_since_last_update = self.packets_processed - last_packets_decrypted
                last_packets_decrypted = self.packets_processed
                last_packets_received = self.packets_received
                dirty = True
                if dirty:
                    if system_platform == "Windows":
                        os.system('cls')
                    else:
                        os.system('clear')
                    # Sensor info
                    last_sensors["SensorInfo"] = {
                        "serial_number": self.serial_number,
                        "battery": battery,
                        "sample_rate": str(packets_received_since_last_update),
                        "crypto_rate": str(packets_processed_since_last_update),
                        "received": str(self.packets_received),
                        "processed": str(self.packets_processed),
                        "old_model": self.old_model,
                    }
                    json_data = json.dumps(last_sensors, ensure_ascii = False)
                    # Send the JSON to Era.Server
                    url = 'http://localhost:39303/api/era/eeg'
                    headers = {
                        "Content-Type": "application/json; charset=utf-8",
                        "User-Agent": "python-requests/2.12.4"
                    }
                    requests.post(url, data = json_data, headers = headers)
                    # Stop the service after sending it once
                    if self.single_call:
                        run_once = True
                        self._stop_signal = True
                    dirty = False               
            self.lock.acquire()
            if self._stop_signal:
                print("Output thread stopping.")
                self.running = False
            # time.sleep(0.11)
        self.lock.release()


