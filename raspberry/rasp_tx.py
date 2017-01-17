'''
Transmission script of the range test.

\author Jonathan Munoz (jonathan.munoz@inria.fr), January 2017
'''

import time
import logging

import radio_rpi as radio
import at86rf215 as at86
import ieee802154g as ie154g

PACKET_LENGTH = 2047
CRC_SIZE = 4
radio.at86_state = 0


class ExperimentTx(threading.Thread):
    def __init__(self):
        # start the thread
        threading.Thread.__init__(self)
        self.name = 'ExperimentTx'
        self.start()

    def run(self):

        radio_driver = radio.At86rf215()
        radio_driver.radio_init(3)
        radio_driver.radio_reset()
        radio_driver.read_isr()
        pkt_nb = 0
        packet = [i & 0xFF for i in range(PACKET_LENGTH)]

        for modulations_tx in ie154g.modulation_list_tx:
            radio_driver.radio_write_config(modulations_tx)
            for frequency_setup in ie154g.frequencies_setup:
                radio_driver.radio_off()
                radio_driver.radio_set_frequency(frequency_setup)
                radio_driver.radio_off()
                for j in range(len(ie154g.packet_sizes)):
                    pkt_size = radio_driver.change_pkt_size(ie154g.packet_sizes, (j%4))
                    for i in range(100):
                        pkt_nb += 1
                        packet = [pkt_nb&0xFF, pkt_nb>>8] + packet
                        radio_driver.radio_load_packet(packet[:pkt_size - CRC_SIZE])
                        radio_driver.radio_trx_enable()
                        print('radio enabled')
                        radio_driver.radio_tx_now()
                        print('packet sent')


def main():

    experimentTx = ExperimentTx()
    while True:
        input = raw_input('>')
        if input=='s':
            print experimentTx.getStats()

if __name__ == '__main__':
    main()
