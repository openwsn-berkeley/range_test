#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import struct
import socket
import logging
try:
   import serial
except ImportError:
   pass

banner  = []
banner += [""]
banner += [" ___                 _ _ _  ___  _ _ "]
banner += ["| . | ___  ___ ._ _ | | | |/ __>| \ |"]
banner += ["| | || . \/ ._>| ' || | | |\__ \|   |"]
banner += ["`___'|  _/\___.|_|_||__/_/ <___/|_\_|"]
banner += ["     |_|                  openwsn.org"]
banner += [""]
banner  = '\n'.join(banner)
print banner


def mote_connect(motename=None , serialport= None, baudrate='115200'):
    try:
        if (motename):
            mote = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            mote.connect((motename,20000))
        else:
            mote = serial.Serial(serialport, baudrate)
        return mote
    except Exception as err:
        print "{0}".format(err)
        raw_input('Press Enter to close.')
        sys.exit(1)

def mote_msp430_at86(serialport= '/dev/moteTRX', baudrate='115200'):

    mote_msp = serial.Serial(serialport, baudrate)
    return mote_msp

def gps():
    GPS_fix = False
    GPS_synchro = False
    ser = serial.Serial('/dev/gps', 9600)
    while GPS_fix == False:
        GPS_frame = ser.readline()
        index = GPS_frame.find("GPRMC")
        if index == -1 :
            ser.flushInput()
            print "not locked"
        else:
            print GPS_frame
            if GPS_frame[57] != '280606':
                GPS_fix = True
                print "valid time"
            else:
                print "not valid"
                ser.flushInput()
    while GPS_synchro == False:
        GPS_frame = ser.readline()
        index = GPS_frame.find("GPRMC")
        if index == -1 :
            print GPS_frame
            print "not now"
            ser.flushInput()
        else:
            print GPS_frame
            if GPS_frame[9:13] == '5700' or  GPS_frame[9:13] == '5800':
                GPS_synchro = True
                print "c'est parti"
            else:
                ser.flushInput()
    return 1

#============================ configuration and connection ===================================
mote_msp = None
gps()
mote_msp = mote_msp430_at86()
print "ay caramba"
mote_msp.write('G')
print "muchacho"

#============================ read ============================================

rawFrame = []
logging.basicConfig(filename='log.txt', filemode='w+', level=logging.DEBUG)

while True:

    byte  = mote_msp.read(1)
    rawFrame += [ord(byte)]

    if rawFrame[-3:]==[0xff]*3 and len(rawFrame)>=10:

        (rxpk_len,rxpk_num,rxpk_rssi,rxpk_crc,rxpk_mcs) = \
            struct.unpack('>HHbBB', ''.join([chr(b) for b in rawFrame[-10:-3]]))
        print 'len={0:<4} num={1:<5} rssi={2:<4} crc={3}  mcs={4}'.format(
            rxpk_len,
            rxpk_num,
            rxpk_rssi,
            rxpk_crc,
            rxpk_mcs
        )
        logging.info('len={0:<4} num={1:<5} rssi={2:<4} crc={3}  mcs={4}'.format(
            rxpk_len,
            rxpk_num,
            rxpk_rssi,
            rxpk_crc,
            rxpk_mcs
        ))
        if rxpk_len>2047:
            print "ERROR: frame too long.\a"

        rawFrame = []

