'''
Read QR code and verify.

Depedencies:
numpy - pip3 install numpy
pyzbar - pip3 install pyzbar
openCV - pip3 install python-opencv
pyota - pip3 install pyota[ccurl]

Special thanks: Caihao.Cui for openCV reading
'''

from __future__ import print_function

import pyzbar.pyzbar as pyzbar
from imutils.video import VideoStream
import numpy as np
import imutils
import cv2
import time
from datetime import datetime

from iota import (
  __version__,
  Address,
  Iota,
  ProposedTransaction,
  Tag,
  TryteString,
  transaction
)

import random, os, time, sys
import binascii
from configparser import SafeConfigParser

node = 'https://tuna.iotasalad.org:14265' #Select your preferred node

parser = SafeConfigParser()
config_files = parser.read('config.ini')

if len(config_files) == 0:
    #Generate random Nano seed
    print('Generate random seed')
    full_nano_seed = hex(random.SystemRandom().getrandbits(256))
    nano_seed = full_nano_seed[2:].upper()

    #Generate random IOTA seed
    seed = ''
    seed = seed.encode('ascii')
    api = Iota(node, seed)
    iota_seed = str(api.seed)

    cfgfile = open("config.ini",'w')
    parser.add_section('wallet')
    parser.set('wallet', 'iotaSeed', iota_seed)
    parser.set('wallet', 'index', '0')

    parser.write(cfgfile)
    cfgfile.close()

else:
    print("Config file successfully loaded")
    index = int(parser.get('wallet', 'index'))
    iota_seed = parser.get('wallet', 'iotaSeed')

#Check Balance

def get_balances():
    nanoBalance = int(nano.get_balance(nano.get_previous(account)))
    api = Iota(node, iota_seed)
    iotaBalance = api.get_account_data()['balance']
    return iotaBalance, nanoBalance
    

def send_message(address, depth, message, tag, uri, value):
    # Ensure seed is not displayed in cleartext.
    seed = iota_seed
    # Create the API instance.
    api = Iota(uri, seed)

    print('Starting transfer please wait...\n')
    # For more information, see :py:meth:`Iota.send_transfer`.
    bundle = api.send_transfer(
        depth=depth,
        # One or more :py:class:`ProposedTransaction` objects to add to the
        # bundle.
        transfers=[
            ProposedTransaction(
                # Recipient of the transfer.
                address=Address(address),

                # Amount of IOTA to transfer.
                # By default this is a zero value transfer.
                value=value,

                # Optional tag to attach to the transfer.
                tag=Tag(tag),

                # Optional message to include with the transfer.
                message=TryteString.from_string(message),
            ),
        ],
    )

    tx_hash = bundle['bundle'].transactions[0].hash
    return tx_hash

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
#vs = VideoStream(usePiCamera=True).start()
time.sleep(2)

scans=[]
lastScan = datetime.now()
iotaTrinityAddress = ""
# loop over the frames from the video stream
print("Ready for scan!")
while True:

    # grab the frame from the threaded video stream and resize it to
    # have a maximum width of 400 pixels
    frame = vs.read()
    #frame = imutils.resize(frame, width=640)
    cv2.resize(frame, (0,0), fx=0.5, fy=0.5)

    # initialize the frame for viewing
    #cv2.imshow('frame',frame)
    #key = cv2.waitKey(1)

    # find the barcodes in the frame and decode each of the barcodes
    barcodes = pyzbar.decode(frame)

    # loop over the detected barcodes
    for barcode in barcodes:
        # the barcode data is a bytes object so if we want to draw it
        # on our output image we need to convert it to a string first
        data = barcode.data.decode("utf-8")
        type = barcode.type

        #print('Type : ', type)
        #print('Data : ', data,'\n')

        if data.find('address') != -1:
        	iotaTrinityAddress = data[12:102]
        	print('IOTA Address Found! ' ,iotaTrinityAddress)
        	timeScanned = datetime.now()
        	lastScan = datetime.now()
        	print('Address Found at: ',timeScanned)
        else:
            if scans.count(data) < 50 and elapsedSeconds > 1:
                scans.append(data)
                lastScan = datetime.now()
                print('Last scan at: ',lastScan)
                print('Total Items Scanned: ', len(scans))

        # Display screen
    elapsed = datetime.now() - lastScan
    elapsedSeconds = elapsed.total_seconds()
    if elapsedSeconds > 10 and len(scans) > 0:
        if iotaTrinityAddress != "":
            print('Elapsed Time: ',elapsed) 
            print('Total Items Scanned: ', len(scans))
            print('IOTA Address Found! ' ,iotaTrinityAddress)
            print('Address Found at: ',timeScanned)
            reward = len(set(scans))*len(scans) #unique_trash*scans
            print('Thanks for using TangleTrash your reward: ', reward)

            tangleTrash = iotaTrinityAddress + ' has scanned ' + str(len(scans)) + ' pieces of Tangle Trash! ' + str(timeScanned)

            tx_hash = send_message(iotaTrinityAddress, int(reward), tangleTrash, 'TANGLE9TRASH99', node, 3)
            print('Trash Sent!: ', tx_hash)

            #Clean up and reset
            scans=[]
            iotaTrinityAddress = ""
            lastScan = datetime.now()
            print("Ready for scan!")
        else:
            print("Listening for iota address...")
            lastScan = datetime.now()
