# -*- coding: utf-8 -*-

import ujson
import os
import copy
import stat
from datetime import datetime
from .python_queue import Queue
from threading import Thread, Lock

class EmotivSend(object):

    def __init__(self):
        self.connection = None
        self.output_folder = ""
        self.decrypt_data = Queue()
        self.encrypt_data = Queue()
        self.lock = Lock()
        self.thread = Thread(target=self.run)
        self.thread.setDaemon(True)
        self.encrypt_running = False
        self.decrypt_running = False
        self.stopped = False
        self.queue_size = 0
        self.readings_per_file = 100
        self.encrypt_array = []
        self.decrypt_array = []

    def start(self, is_encrypt, is_decrypt):
        """
        Starts the Emotiv Sender thread.
        """
        self.encrypt_running = is_encrypt
        self.decrypt_running = is_decrypt
        self.stopped = False
        self.thread.start()

    #incomplete stop
    def stop(self):
        """
        Stops the Emotiv Sender thread.
        """
        self.lock.acquire()
        self.stopped = True;
        self.lock.release()

    def save_data(self, saving_counter, all_data, folder_name):    
        folder_filename = self.output_folder + folder_name + "\\" + str(ujson.loads(all_data[0])['systemmillisecond']) + '_' + str(ujson.loads(all_data[-1])['systemmillisecond'])
        with open(folder_filename, 'wb') as outfile:
            #print("Dumping file " + folder_filename)
            outfile.write(ujson.dumps(all_data))
            all_data = []
            print(" Saving " + str(saving_counter) + "\\" + str(self.queue_size))  

    def save_all_data(self, queue_data, list_data, counter, type):
        while not queue_data.empty(): 
            print(" Send data " + type + " " + str(counter) + "\\" + str(self.queue_size))
            # get the data from the crypto
            list_data.append(ujson.dumps(queue_data.get()))

            # Batch Save
            if counter % self.readings_per_file == 0:
                if counter > 0:
                    self.save_data(counter, list_data, type)
                    del list_data[:]
                  
                
            #send to server
            #json_data = json.dumps(_data, ensure_ascii = False)
            #if(self.connection is not None):
            #    if(self.connection.hub is not None):
            #        self.connection.hub.server.invoke('SendEEG', json_data)
                
            counter += 1

            if counter == self.queue_size:
                self.save_data(counter, list_data, type)
                del list_data[:]
                if(type == "decrypt"):
                    self.decrypt_running = False
                else:
                    self.encrypt_running = False

        return counter

    def make_folders(self):
        if not os.path.exists(self.output_folder):
            print("Creating folder " + self.output_folder)
            os.makedirs(self.output_folder)
            if not os.path.exists(self.output_folder + "/decrypt/"):
                os.makedirs(self.output_folder + "/decrypt/")
            if not os.path.exists(self.output_folder + "/encrypt/"):
                os.makedirs(self.output_folder + "/encrypt/")

    def run(self):
        print("Save thread started")
        # Make folders
        self.make_folders()    
        saving_decrypt_counter = 0
        saving_encrypt_counter = 0
        self.lock.acquire()
        while self.encrypt_running or self.decrypt_running:
            self.lock.release()          

            # Save encrypted data if available
            saving_encrypt_counter = self.save_all_data(self.encrypt_data, self.encrypt_array, saving_encrypt_counter, "encrypt")

            # Save decrypted data if available
            saving_decrypt_counter = self.save_all_data(self.decrypt_data, self.decrypt_array, saving_decrypt_counter, "decrypt")
                                  
            self.lock.acquire()

        print("Dump thread complete")




