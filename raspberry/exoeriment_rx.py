'''
Reception script of the range test.

\author Jonathan Munoz (jonathan.munoz@inria.fr), January 2017
'''

import time
import sys
import logging
import threading

import radio_rpi   as radio
import ieee802154g as ie154g

PACKET_LENGTH = 2047
CRC_SIZE      = 4

class ExperimentRx(threading.Thread):
    
    def __init__(self):
        
        # local variables
        self.radio_driver = None

        # start the thread
        threading.Thread.__init__(self)
        self.name = 'ExperimentRx'
        self.start()

    def run(self):

        # initialize the radio
        self.radio_driver = radio.At86rf215(self._cb_rx_frame)
        self.radio_driver.radio_init(3)
        self.radio_driver.radio_reset()
        self.radio_driver.read_isr_source() # no functional role, just clear the pending interrupt flag
        
        while True: # main loop
            
            # re-configure the radio
            self.radio_driver.radio_write_config(ie154g.radio_configs_rx[0])
            self.radio_driver.radio_set_frequency(ie154g.radio_frequencies[0])
            self.radio_driver.radio_trx_enable()
            self.radio_driver.radio_rx_now()
            
            # wait for the GPS thread to indicate it's time to move to the next configuration
            time.sleep(10) # FIXME: replace by an event from the GPS thread
            print('TIMER 10 Seconds triggers')
    
    #======================== public ==========================================
    
    def getStats(self):
        raise NotImplementedError()

    #======================== private =========================================

    def _cb_rx_frame(self, pkt_rcv, rssi, crc, mcs):
        
        # handle the received frame
        print ('packet {0}'.format(pkt_rcv)) # FIXME: replace by logging
        
        # re-arm the radio in RX mode
        self.radio_driver.radio_rx_now()

#============================ main ============================================

def main():
    experimentRx = ExperimentRx()
    while True:
        input = raw_input('>')
        if   input == 's':
            print experimentRx.getStats()
        elif input == 'q':
            sys.exit(0)
            
if __name__ == '__main__':
    main()
