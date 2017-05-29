# -*- coding: utf-8 -*-
from __future__ import absolute_import, division

import os
import sys
import ujson
import multiprocessing as Process
from datetime import datetime
from threading import Thread, Lock
from time import time, sleep
from .decrypter import EmotivCrypto
from .packet import EmotivPacket
from .python_queue import Queue
from .reader import EmotivReader
from .emotiv_connection import EmotivConnection
from .send import EmotivSend
from .tasks import EmotivReaderTask
from .sensors import sensors_mapping
from .util import path_checker, system_platform, values_header

class Emotiv_Lite(object):
    """
    Receives, decrypts and stores packets received from Emotiv Headsets and other sources.
    """

    # TODO: Add a calibration mechanism, get a "noise average" per sensor or even a "noise pattern" to filter
    #       sensor values when processing packets received. Ideally this would be done not on someone's head.
    # TODO: Add filters for facial expressions, muscle contractions.
    def __init__(self, serial_number=None, is_research=False, input_source="emotiv",
                 sys_platform=system_platform, verbose=False, output_path=None, 
                 chunk_writes=True, chunk_size=32, save_encrypt_data=True, save_decrypt_data=False,
                 decrypt_encrypt_folder = "", decrypt_encrypt = False):
        """
        Sets up initial values.
        :param serial_number - Specify serial_number, needed to decrypt packets for raw data reader and special cases.
        :param is_research - Is EPOC headset research edition? Doesn't seem to work even if it is.
        :param input_source - emotiv 
        :param sys_platform - Operating system, to avoid global statement
        :param verbose - Detailed logging.
        :param output_path - The path to output data files to.
        :param chunk_writes - Write a chunk of data instead of a single line.
        :param chunk_size - The number of packets to buffer before writing.
        :param hub_url - URL to connect for sending data and receiving commands
        Expect performance to suffer when writing data to a csv, maybe.

        """
        print("Initializing Emokit...")
        self.running = False
        self.chunk_writes = chunk_writes
        self.chunk_size = chunk_size
        # Battery percent, as int.
        self.battery = 0
        # Print details of operation in console, exceptions, etc.
        self.verbose = verbose
        # Should be True for research edition EPOCs and newer EPOC+s, apparently.
        self.is_research = is_research
        self.sensors = sensors_mapping
        # The EPOCs serial number.
        self.serial_number = serial_number
        # Only really applies to quality value calculation, probably needs some updating.
        self.old_model = False
        # Not used at the moment.
        self.read_values = False
        # The current platform.
        self.platform = sys_platform
        # The number of times data was received.
        self.packets_received = 0
        # The number of times data was decrypted or made into EmotivPackets.
        self.packets_processed = 0
        # The source of the emotiv data.
        self.input_source = input_source
        # If the input source is not an emotiv headset, it is a file.
        self.reader = None
        self.lock = Lock()
        # Setup output writers, multiple types can be output now at once.
        self.crypto = None
        # Setup the crypto thread, if we are reading from an encrypted data source.
        self.connection = None
        self.hub_url = 'http://localhost:51560/signalr'
        self.hub_name = 'EmokitHub'
        self.emotiv_sender = None
        # Setup SignalR to synchronize with the Producer
        self.save_encrypt_data = save_encrypt_data
        self.save_decrypt_data = save_decrypt_data
        self.decrypt_encrypt_folder = decrypt_encrypt_folder
        self.decrypt_encrypt = decrypt_encrypt
        # Setup emokit loop thread. This thread coordinates the work done from the reader to be decrypted and queued
        # into EmotivPackets.
        self.thread = Thread(target=self.run)
        self.thread.setDaemon(True)
        self.start()

    def initialize_reader(self, failed_to_initialize):
        print("Initializing Reader Thread...")
        if self.input_source == "emotiv":
            # Initialize an EmotivReader with default values, it will try to locate a headset.
            self.reader = EmotivReader()
            if self.reader.serial_number is not None:
                # If EmotivReader found a serial number automatically, change local serial number to the reader serial.
                self.serial_number = self.reader.serial_number
                # Send init info to the server
                if failed_to_initialize is False:
                    print("Waiting for SignalR to acknowledge - 'init'")
                    self.connection.reader_init = True;
                else:
                    print("Please check if the device is paired")
    
    def initialize_crypto(self):
        print("Initializing Crypto Thread...")
        self.crypto = EmotivCrypto(self.serial_number, self.is_research, verbose=self.verbose)

    def initialize_connection(self):
        print("Connection Thread Started")
        if self.hub_url and self.hub_name:
        # Initialize an EmotivConnection with default values.
            self.connection = EmotivConnection()

    def Initialize_sender(self):
        print("Sender Thread Started")
        self.emotiv_sender = EmotivSend()
        #Setup sender
        if(self.decrypt_encrypt):
            self.emotiv_sender.output_folder = self.decrypt_encrypt_folder + "custom\\"
        else:
            full_path = os.path.realpath(__file__)
            self.emotiv_sender.output_folder = os.path.dirname(full_path).replace("\emokit", "\\eeg\\" + datetime.utcnow().strftime('%Y%m%d%H%M%S%f') + "\\")
        self.emotiv_sender.connection = self.connection
        self.emotiv_sender.queue_size = self.packets_received
        #Start
        self.emotiv_sender.start(self.save_encrypt_data, self.save_decrypt_data)

    def start(self):
        """
        Initialize the hub and wait for commands
        """
        self.running = True
        self.thread.start()

    def stop(self):
        """
        Stops emotiv
        :return:
        """
        if self.reader is not None:
            self.reader.stop()
        if self.crypto is not None:
            self.crypto.stop()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if traceback:
            self.log(traceback)
        self.stop()

    def log(self, message):
        """
        Logging function, only prints if verbose is True.
        :param message: Message to log/print
        """
        if self.display_output and self.verbose:
            print("%s" % message)

    def init(self):
        self.initialize_connection()
        if self.connection is not None:
            self.connection.start()
            # Initialize the reader and crypto after the SignalR connection is established so 
            # that we can send an update to the server that the initialization is complete
            self.initialize_reader(False)
            # To store all the read eeg tasks
            self.initialize_crypto()

    def decrypt_and_save(self):
        #Init
        if(self.save_encrypt_data is False):
            self.Initialize_sender()  
        #Start
        self.crypto.start()
        # sensors data
        sensors_data = sensors_mapping.copy()
        decrypt_counter = 0
        self.lock.acquire()
        while self.running:
            self.lock.release()

            #Decrypt the data received from the device
            if self.crypto.data_ready():
                decrypted_task = self.crypto.get_data()
  
                self.packets_processed += 1
                new_packet = EmotivPacket(decrypted_task.data, timestamp=decrypted_task.timestamp)
                sensors_data = new_packet.sensors
                if new_packet.battery is not None:
                    self.battery = new_packet.battery

                ## Send Emotiv Data using new thread
                data = {}
                data['systemmillisecond'] = str( new_packet.timestamp )
                data['battery'] = self.battery
                data['sensors'] = sensors_data
                self.emotiv_sender.decrypt_data.put_nowait(data)
                decrypt_counter += 1    
                print("Decrypting " + str(decrypt_counter) + "/" + str(self.packets_received))           

            self.lock.acquire()

            if decrypt_counter >= self.packets_received:                                     
                #Stop crypting thread         
                self.crypto.stop()
                #Now start the save thread
                self.running = False

    def add_reader_data_to_crypto(self, readers_received):
        if(self.save_decrypt_data):
            #Read the data from the device and add it as tasks to cryptoo thread
            if not self.reader.data.empty():
                try:
                    reader_task = self.reader.data.get()        
                    self.crypto.add_task(reader_task)
                    readers_received += 1
                except KeyboardInterrupt:
                    print("Keyboard inetrupted")
                    self.quit()
        return readers_received

    def run(self):
        """ Do not call explicitly, called upon initialization of class or self.start()
        The main emokit loop.
        :param reader: EmotivReader class
        :param crypto: EmotivCrypto class
        """
        self.init() 
        isConnectionSet = False;
        readers_received = 0
        last_packets_received = 0
        packets_received_since_last_update = 0
        tick_time = time()
        stale_rx = 0
        restarting_reader = False
        self.lock.acquire()
        while self.running:
            self.lock.release()

            # Decode the encrypted data and save it
            if self.decrypt_encrypt:
                decrypt_folder = self.decrypt_encrypt_folder + "encrypt"
                filenames = os.listdir(decrypt_folder)
                for filename in filenames:
                    with open(decrypt_folder + "\\" + filename) as json_file:
                        json_data_list = ujson.load(json_file)
                        for json_data_string in json_data_list:
                            json_data = ujson.loads(json_data_string)
                            reader_task = EmotivReaderTask(data=''.join(map(chr, json_data['data'])), timestamp=json_data['systemmillisecond'])
                            self.crypto.add_task(reader_task)
                            self.packets_received += 1
                            print("Packet Size " + str(self.packets_received))
                # Now decrypt and save
                if(self.packets_received > 0):
                    self.save_encrypt_data = False
                    self.save_decrypt_data = True
                    self.decrypt_and_save()
            # Read data from the sensors and decide what to do
            else:
                if self.connection.running:
                    #Execute this when the connection starts
                    if not isConnectionSet:
                        isConnectionSet = True
                        self.reader.start()                 

                    # Update the packet size directly from reader
                    self.packets_received = self.reader.save_data_size
                    # Sample rate
                    if(packets_received_since_last_update > 0):
                        print(packets_received_since_last_update)

                    # Only enable this if decrypting straight after reading
                    readers_received = self.add_reader_data_to_crypto(readers_received)
                
                    #Calculate sampling rate/crypto rate and Restart reader if cannot read
                    tick_diff = time() - tick_time
                    if tick_diff >= 1:
                        tick_time = time()
                        packets_received_since_last_update = self.packets_received - last_packets_received
                        if packets_received_since_last_update == 1 or packets_received_since_last_update == 0:
                            stale_rx += 1
                        last_packets_received = self.packets_received
                        if restarting_reader and self.reader.stopped:
                            print("Restarting Reader")
                            stale_rx = 0
                            self.initialize_reader(True)
                            self.reader.start()
                            restarting_reader = False
                            print("Reader Thread Restarted")

                        elif stale_rx > 5 and not restarting_reader:
                            self.reader.stop()
                            restarting_reader = True
                else:
                    #Execute this when the connection stops
                    if isConnectionSet:
                        isConnectionSet = False
                        self.reader.stop() 

                        if(self.save_encrypt_data):
                            self.Initialize_sender()
                            while not self.reader.save_data.empty(): 
                                self.emotiv_sender.encrypt_data.put_nowait(self.reader.save_data.get_nowait())
                    
                        if(self.save_decrypt_data):
                            # Make sure we retreieved all the reader data
                            while (self.packets_received > readers_received):
                                readers_received = self.add_reader_data_to_crypto(readers_received)
                            self.decrypt_and_save()
                           
                    sleep(0.0001)

            self.lock.acquire()

    def quit(self):
        """
        A little more forceful stop.
        """
        self.stop()
        os._exit(1)

    def force_quit(self):
        """
        Kill emokit. Might leave files and other objects open or locked.
        """
        os._exit(1)


if __name__ == "__main__":
    a = Emotiv()

