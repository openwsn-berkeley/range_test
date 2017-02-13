"""
Transmission script of the range test.

author Jonathan Munoz (jonathan.munoz@inria.fr), January 2017
"""

import time
import logging
import threading
import sys
import sched
import Queue

import at86rf215_driver      as radio
import experiment_settings   as settings

FRAME_LENGTH  = 2047
CRC_SIZE      = 4


class InformativeTx(threading.Thread):

    def __init__(self, queue):

        # store parameters
        self.queue = queue

        # local variables

        # start the thread
        threading.Thread.__init__(self)
        self.name = 'InformativeTx'
        self.daemon = True
        self.start()

        logging.basicConfig(stream=sys.__stdout__, level=logging.WARNING)

    def run(self):

        while True:
            item = self.queue.get()
            if type(item) is tuple:
                logging.warning('Time to send the frames {0} - {1} was {2} seconds\n'.format(item[0] - 100, item[0], item[1]))
            else:
                logging.warning('Modulation used is: {0}'.format(item))


class TxTimer(threading.Thread):

    TIMER_PERIOD = 0.0200

    def __init__(self, event):

        # store parameters
        self.event = event

        # local variables

        # start the thread
        threading.Thread.__init__(self)
        self.name = 'TxTimer'
        self.daemon = True
        self.start()

    def run(self):
        while True:
            time.sleep(self.TIMER_PERIOD)
            self.event.set()


class ExperimentTx(threading.Thread):
    
    def __init__(self, start_time):
        
        # local variables
        self.radio_driver = None
        self.start_time = start_time
        self.index = 0
        self.queue_tx = Queue.Queue()
        
        # start the thread
        threading.Thread.__init__(self)
        self.name = 'ExperimentTx_'
        self.daemon = True
        self.start()

        self.txEvent = threading.Event()
        self.txEvent.clear()

        self.informativeTx = InformativeTx(self.queue_tx)
        self.txTimer = TxTimer(self.txEvent)
        # configure the logging module
        logging.basicConfig(stream= sys.__stdout__, level=logging.WARNING)

    def radio_setup(self):

        # initialize the radio driver
        self.radio_driver = radio.At86rf215(self._cb_rx_frame)
        self.radio_driver.radio_init(3)
        self.radio_driver.radio_reset()
        self.radio_driver.read_isr_source()  # no functional role, just clear the pending interrupt flag

    def execute_exp(self):

        # initialize the frame counter
        frame_counter = 0

        logging.warning('Number of threads; {0}'.format(threading.enumerate()))
        # match up a modulation with a frequency setup (frequency_0, bandwidth, channel)
        # freq_mod_tech = zip(settings.radio_configs_tx, settings.radio_frequencies)

        # loop radio configurations
        # for radio_config in settings.radio_configs_tx:
        # for fmt in freq_mod_tech:

        # re-configure the radio
        self.radio_driver.radio_write_config(settings.radio_configs_tx[self.index])
        # self.radio_driver.radio_write_config(freq_mod_tech[9][0])

        # loop through frequencies
        # for frequency_setup in settings.radio_frequencies:

        # switch frequency
        self.radio_driver.radio_off()
        self.radio_driver.radio_set_frequency(settings.radio_frequencies[self.index])
        # self.radio_driver.radio_set_frequency(freq_mod_tech[9][1])

        # wait for the right moment to start transmitting
        # self.start_event.wait()
        # self.start_event.clear()
        self.queue_tx.put(settings.radio_configs_name[self.index])

        # loop through packet lengths
        for frame_length in settings.frame_lengths:

            logging.warning('frame length {0}, thread name: {1}'.format(frame_length, self.name))
            now = time.time()
            self.radio_driver.radio_trx_enable()
            # send burst of frames
            logging.warning('before start sending frames')
            for i in range(settings.BURST_SIZE):
                logging.debug('frame burst {0}'.format(i))
                # increment the frame counter
                frame_counter += 1

                # create frame
                frameToSend = [(frame_counter >> 8) & 0xFF, frame_counter & 0xFF] + [i & 0xFF for i in
                                                                                     range(FRAME_LENGTH - 2)]
                logging.debug(
                    'frame counter: byte 0:{0} byte 1:{1} real counter {2}'.format(((frame_counter >> 8) & 0xFF),
                                                                                   frame_counter & 0xFF, frame_counter))
                logging.debug('three first bytes, frame counter: {0}.\n'.format(frameToSend[0:3]))
                # send frame
                self.radio_driver.radio_load_packet(frameToSend[:frame_length - CRC_SIZE])
                self.queue_tx.put('SENDING')
                self.radio_driver.radio_tx_now()
                self.queue_tx.put('SENT')
                # wait for IFS (to allow the receiver to handle the RX'ed frame)
                self.txEvent.wait()
                self.txEvent.clear()

            self.queue_tx.put((frame_counter, time.time() - now))
        logging.warning('FINAL')
        logging.warning('Number of threads; {0}'.format(threading.enumerate()))
        self.index += 1
    
    def run(self):

        self.radio_setup()
        s = sched.scheduler(time.time, time.sleep)
        s.enter(self.start_time, 1, self.execute_exp, ())
        s.enter(self.start_time + 30, 1, self.execute_exp, ())
        s.enter(self.start_time + 60, 1, self.execute_exp, ())
        s.run()


    #  ======================== private =======================================
    
    def _cb_rx_frame(self, pkt_rcv, rssi, crc, mcs):
        raise SystemError("frame received on transmitting mote")

#  ============================ main ==========================================


def main():
    # scheduler = Scheduled(int(sys.argv[1]))
    experimentTx = ExperimentTx(int(sys.argv[1]))
    #Scheduled(int(sys.argv[1]))
    while True:
        input = raw_input('>')
        if input == 's':
            print experimentTx.getStats()
            # print 'print stats TX'
        if input == 'q':
            sys.exit(0)

if __name__ == '__main__':
    main()
