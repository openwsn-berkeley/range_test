

import time
import sys
import logging

import radio_rpi as radio
import at86rf215 as at86
import ieee802154g as ie154g

PACKET_LENGTH = 2047
CRC_SIZE = 4

class ExperimentRx(threading.Thread):
    def __init__(self):
        
        # start the thread
        threading.Thread.__init__(self)
        self.name            = 'ExperimentRx'
        self.start()
    
    def run(self):
        
        # initialization
        # FIXME: init driver, pass self._cb_rx_frame
        
        # initialize the radio
        radio.init_spi()
        radio.init_GPIO()
        radio.radio_reset()
        radio.write_config(ie154g.modulation_list_rx[0])
        
        # switch to RX mode
        radio.set_frequency(ie154g.frequencies_setup[0])
        radio.trx_enable()
        radio.rx_now()
        
        # main loop
        while True:

            radio.at86_state = 0
            print radio.at86_state
            radio.rx_done = 0
            # FIXME: using a Threading.Event() object
            while radio.done == 0:
                pass

            (pkt_rcv, rssi, crc, mcs) = radio.get_received_frame()
            print (pkt_rcv, rssi, crc, mcs)
            radio.rx_now()
    
    #======================== public ==========================================
    
    def getStats(self):
        return 0
    
    #======================== private =========================================
    
    def _cb_rx_frame(self,frame):
        print frame

#============================ main ============================================

def main():
    experimentRx = ExperimentRx()
    while True:
        input = raw_input('>')
        if input=='s':
            print experimentRx.getStats()

if __name__ == '__main__':
    main()
