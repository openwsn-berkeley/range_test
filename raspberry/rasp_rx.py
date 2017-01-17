'''
Reception script of the range test.

\author Jonathan Munoz (jonathan.munoz@inria.fr), January 2017
'''

import time
import sys
import logging

import radio_rpi as radio
import ieee802154g as ie154g

PACKET_LENGTH = 2047
CRC_SIZE = 4


class ExperimentRx(threading.Thread):
    def __init__(self):

        # start the thread
        threading.Thread.__init__(self)
        self.name = 'ExperimentRx'
        self.start()

    def run(self):

        # initialization
        # FIXME: init driver, pass self._cb_rx_frame
        radio_driver = radio.At86rf215()
        # initialize the radio
        radio_driver.radio_init(3)
        radio_driver.radio_reset()
        radio_driver.radio_write_config(ie154g.modulation_list_rx[0])

        # switch to RX mode
        radio_driver.radio_set_frequency(ie154g.frequencies_setup[0])
        radio_driver.radio_trx_enable()
        radio_driver.radio_rx_now()

        # main loop
        while True:

            radio_driver.at86_state = 0
            print radio_driver.at86_state
            radio_driver.rx_done = 0
            # FIXME: using a Threading.Event() object
            while radio_driver.rx_done == 0:
                pass

            (pkt_rcv, rssi, crc, mcs) = radio_driver.radio_get_received_frame()
            print (pkt_rcv, rssi, crc, mcs)
            radio_driver.radio_rx_now()

    # ======================== public ==========================================

    def getStats(self):
        return 0

    # ======================== private =========================================

    def _cb_rx_frame(self, frame):
        print frame


# ============================ main ============================================

def main():
    experimentRx = ExperimentRx()
    while True:
        input = raw_input('>')
        if input == 's':
            print experimentRx.getStats()


if __name__ == '__main__':
    main()
