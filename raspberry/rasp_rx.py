'''
Reception script of the range test.

\author Jonathan Munoz (jonathan.munoz@inria.fr), January 2017
'''

import time
import sys
import logging
import threading

import radio_rpi as radio
import ieee802154g as ie154g

PACKET_LENGTH = 2047
CRC_SIZE = 4


class ExperimentRx(threading.Thread):
    def __init__(self):
        
        # start the thread
        threading.Thread.__init__(self)
        self.name = 'ExperimentRx'
        self.event = threading.Event()
        self.event.clear()
        self.start()

    def run(self):

        radio_driver = radio.At86rf215(self._cb_rx_frame)
        # initialize the radio
        radio_driver.radio_init(3)
        radio_driver.radio_reset()


        # main loop
        while True:
            radio_driver.radio_write_config(ie154g.modulation_list_rx[0])

            # switch to RX mode
            radio_driver.radio_set_frequency(ie154g.frequencies_setup[0])
            radio_driver.radio_trx_enable()
            radio_driver.radio_rx_now()
            time.sleep(10)
            #radio_driver.radio_rx_now()
            print('SUCCESS')


    # ======================== public ==========================================

    def getStats(self):
        return 0

    # ======================== private =========================================

    def _cb_rx_frame(self, pkt_rcv, rssi, crc, mcs):
        print ('packet {0}'.format(pkt_rcv))
        #TODO: FIX THIS printing
        self.event.set()
        #radio_driver.radio_rx_now()



# ============================ main ============================================

def main():
    experimentRx = ExperimentRx()
    while True:
        input = raw_input('>')
        if input == 's':
            print experimentRx.getStats()
        elif input == 'q':
            sys.exit(0)
            

if __name__ == '__main__':
    main()
