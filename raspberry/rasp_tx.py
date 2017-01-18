'''
Transmission script of the range test.

\author Jonathan Munoz (jonathan.munoz@inria.fr), January 2017
'''

import time
import logging
import threading
import sys

import radio_rpi as radio
import ieee802154g as ie154g

PACKET_LENGTH = 2047
CRC_SIZE = 4


class ExperimentTx(threading.Thread):
    def __init__(self):
        # start the thread
        threading.Thread.__init__(self)
        self.name = 'ExperimentTx'
        self.start()

    def run(self):

        radio_driver = radio.At86rf215(self._cb_rx_frame)
        radio_driver.radio_init(3)
        radio_driver.radio_reset()
        radio_driver.read_isr()
        pkt_nb = 0
        packet = [i & 0xFF for i in range(PACKET_LENGTH)]

        for modulations_tx in ie154g.modulation_list_tx:
            radio_driver.radio_write_config(modulations_tx)
            print("modulation: {0}".format(modulations_tx))
            for frequency_setup in ie154g.frequencies_setup:
                radio_driver.radio_off()
                radio_driver.radio_set_frequency(frequency_setup)
                print("frequencies: {0}".format(frequency_setup))
                radio_driver.radio_off()
                for size in ie154g.packet_sizes:
                    pkt_size = size
                    for i in range(100):
                        pkt_nb += 1
                        pkt = [pkt_nb>>8, pkt_nb&0xFF] + packet[2:]
                        print('tamano del pkt: {0}'.format(len(pkt[:pkt_size - CRC_SIZE])))
                        radio_driver.radio_load_packet(pkt[:pkt_size - CRC_SIZE])
                        radio_driver.radio_trx_enable()
                        print('radio enabled')
                        time.sleep(0.5)
                        radio_driver.radio_tx_now()
                        print('packet sent')


    # ======================== private =========================================

    def _cb_rx_frame(self, pkt_rcv, rssi, crc, mcs):
        print ('packet {0}'.format(pkt_rcv))
        #TODO: FIX THIS printing
        self.event.set()
        #radio_driver.radio_rx_now()

def main():

    experimentTx = ExperimentTx()
    while True:
        input = raw_input('>')
        if input=='s':
            print experimentTx.getStats()

if __name__ == '__main__':
    main()
