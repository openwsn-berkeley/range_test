'''
Transmission script of the range test.

\author Jonathan Munoz (jonathan.munoz@inria.fr), January 2017
'''

import time
import logging
import threading
import sys

import at86rf215_driver      as radio
import experiment_settings   as settings

FRAME_LENGTH  = 2047
CRC_SIZE      = 4

class ExperimentTx(threading.Thread):
    
    def __init__(self):
        
        # local variables
        self.radio_driver = None
        
        # start the thread
        threading.Thread.__init__(self)
        self.name = 'ExperimentTx'
        self.daemon = True
        self.start()

        # configure the logging module
        logging.basicConfig(stream= sys.__stdout__, level=logging.DEBUG)
    
    def run(self):
        
        # initialize the radio driver
        self.radio_driver = radio.At86rf215(self._cb_rx_frame)
        self.radio_driver.radio_init(3)
        self.radio_driver.radio_reset()
        self.radio_driver.read_isr_source()  # no functional role, just clear the pending interrupt flag
        
        # initialize the frame counter
        frame_counter = 0

        # match up a modulation with a frequency setup (frequency_0, bandwidth, channel)
        freq_mod_tech = zip(settings.radio_configs_tx, settings.radio_frequencies)
        
        # loop radio configurations
        #for radio_config in settings.radio_configs_tx:
        for fmt in freq_mod_tech:

            # useless print
            #logging.info("frequencies: {0}".format(fmt[1]))

            # re-configure the radio
            #self.radio_driver.radio_write_config(radio_config)
            self.radio_driver.radio_write_config(freq_mod_tech[17][0])

            # loop through frequencies
            #for frequency_setup in settings.radio_frequencies:
                
            # switch frequency
            self.radio_driver.radio_off()
            #self.radio_driver.radio_set_frequency(frequency_setup)
            self.radio_driver.radio_set_frequency(freq_mod_tech[17][1])
            #logging.info("frequencies: {0}".format(freq_mod_tech[17][1]))
                
            # loop through packet lengths
            for frame_length in settings.frame_lengths:

                now = time.time()
                # send burst of frames
                for i in range(settings.BURST_SIZE):

                    # increment the frame counter
                    frame_counter += 1
                #    logging.info('sending frame {0}...'.format(frame_counter)),
                    #print frame_counter
                    # create frame
                    frameToSend = [frame_counter >> 8, frame_counter & 0xFF] + [i & 0xFF for i in range(FRAME_LENGTH - 2)]
                        
                    # send frame
                    self.radio_driver.radio_load_packet(frameToSend[:frame_length - CRC_SIZE])
                    self.radio_driver.radio_trx_enable()
                    self.radio_driver.radio_tx_now()
                #    logging.info('sent.\n')

                #    print threading.enumerate()

                    # wait for IFS (to allow the receiver to handle the RX'ed frame)
                    time.sleep(settings.IFS_S)

                print time.time() - now
    
    #  ======================== private =======================================
    
    def _cb_rx_frame(self, pkt_rcv, rssi, crc, mcs):
        raise SystemError("frame received on transmitting mote")

#  ============================ main ==========================================


def main():
    experimentTx = ExperimentTx()
    while True:
        input = raw_input('>')
        if input == 's':
            print experimentTx.getStats()
        if input == 'q':
            sys.exit(0)

if __name__ == '__main__':
    main()
