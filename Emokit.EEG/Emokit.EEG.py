# -*- coding: utf-8 -*-
# This is an example of popping a packet from the Emotiv class's packet queue
# and printing the gyro x and y values to the console. 


import time
import sys
import os

from emokit.emokit_lite import Emotiv_Lite

    # This to manualy do the decryption 
    # (NOTE: YOU NEED THE EMOKIT USB DONGLE PLUGGED IN TO DECRYPT)
    # Only change the folder name to decrypt
    # Usually the eeg folder is created in the python project "{Your saved path to the folder}\ProjectEmokit\Emokit.EEG\eeg"
    #folder_name = "20170526162704788000"
    #folder = str("C:\\Users\\Vivek\\Documents\\visual studio 2017\\Projects\\ProjectEmokit\\Emokit.EEG\\eeg\\") + folder_name + "\\"
    #Emotiv_Lite(verbose=True, decrypt_encrypt_folder=folder, decrypt_encrypt=True)



def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

if __name__ == "__main__":

    if(len(sys.argv) > 2):
        type = str(sys.argv[1])
        if(type == "Read"):
            argument1 = str2bool(sys.argv[2])
            argument2 = str2bool(sys.argv[3])
            Emotiv_Lite(verbose=True, save_encrypt_data = argument1, save_decrypt_data = argument2)
        else: 
            argument = str(sys.argv[2]).replace("SPACE", " ") + "\\"
            print(argument)
            Emotiv_Lite(verbose=True, decrypt_encrypt_folder=argument, decrypt_encrypt=True)
    else:
        # By default it will only save the encrypted data
        Emotiv_Lite(verbose=True)
