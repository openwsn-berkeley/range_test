"""
Reception script of the range test.

\author Jonathan Munoz (jonathan.munoz@inria.fr), January 2017
"""

import time
import sys
import logging
import threading
import sched
import Queue

import at86rf215_driver      as radio
import experiment_settings   as settings

PACKET_LENGTH = 2047
CRC_SIZE      = 4


class InformativeRx(threading.Thread):

    def __init__(self, queue):

        # store parameters
        self.queue = queue
        self.count_rx = 0
        self.frame_last_rx = 0

        # local variables

        # start the thread
        threading.Thread.__init__(self)
        self.name = 'InformativeRx'
        self.daemon = True
        self.start()

        logging.basicConfig(stream=sys.__stdout__, level=logging.WARNING)

    def run(self):

        while True:
            item = self.queue.get()
            if type(item) is tuple:
                logging.warning('Frames received / Frames sent = {0}/{1}\n'.
                             format(((item[0][0])*256 + item[0][1]), item[4]))
            else:
                logging.warning('Modulation used is: {0}'.format(item))


class Scheduled(threading.Thread):

    def __init__(self, start_time):

        #local variables
        self.experiment = None
        self.start_time = start_time

        #start the thread
        threading.Thread.__init__(self)
        self.name = 'Scheduler'
        self.daemon = True
        self.start()

        self.start_event_sch = threading.Event()
        self.start_event_sch.clear()

    def timer(self):
        self.start_event_sch.set()

    def run(self):
        s = sched.scheduler(time.time, time.sleep)
        s.enter(self.start_time, 1, self.timer, ())
        s.run()


class ExperimentRx(threading.Thread):
    
    def __init__(self, index, start_event):
        
        # local variables
        self.radio_driver = None
        self.index = index
        self.start_event = start_event
        self.queue_rx = Queue.Queue()
        self.count_frames_rx = 0
        self.frame_number_last = 0

        # start the thread
        threading.Thread.__init__(self)
        self.name = 'ExperimentRx'
        self.daemon = True
        self.start()

        self.informativeRx = InformativeRx(self.queue_rx)
        # configure the logging module
        logging.basicConfig(stream= sys.__stdout__, level=logging.WARNING)

    def run(self):

        # initialize the radio
        self.radio_driver = radio.At86rf215(self._cb_rx_frame)
        self.radio_driver.radio_init(3)
        self.radio_driver.radio_reset()
        self.radio_driver.read_isr_source()  # no functional role, just clear the pending interrupt flag

        # re-configure the radio
        self.radio_driver.radio_write_config(settings.radio_configs_rx[self.index])
        self.radio_driver.radio_set_frequency(settings.radio_frequencies[self.index])

        self.start_event.wait()
        self.start_event.clear()
        # show the config
        self.queue_rx.put(settings.radio_configs_name[self.index])

        self.radio_driver.radio_trx_enable()
        self.radio_driver.radio_rx_now()
        while True:  # main loop

            # wait for the GPS thread to indicate it's time to move to the next configuration
            time.sleep(10)
            # FIXME: replace by an event from the GPS thread
            print('TIMER 10 Seconds triggers')
    
    #  ======================== public ========================================
    
    def getStats(self):
        raise NotImplementedError()

    #  ====================== private =========================================

    def _cb_rx_frame(self, pkt_rcv, rssi, crc, mcs):
        self.count_frames_rx += 1
        self.queue_rx.put((pkt_rcv, rssi, crc, mcs, self.count_frames_rx))
        # handle the received frame
        # logging.info('frame number: {0}, frame size: {1}, RSSI: {2} dBm,  CRC: {3}, MCS: {4}\n'.
        #             format((pkt_rcv[0]*256 + pkt_rcv[1]), len(pkt_rcv), rssi, crc, mcs))

        # re-arm the radio in RX mode
        self.radio_driver.radio_rx_now()

#  ========================== main ============================================


def main():
    scheduler = Scheduled(int(sys.argv[1]))
    experimentRx = ExperimentRx(0, scheduler.start_event_sch)
    while True :
        input = raw_input('>')
        if input == 's':
            print experimentRx.getStats()
        elif input == 'q':
            sys.exit(0)
            
if __name__ == '__main__':
    main()
