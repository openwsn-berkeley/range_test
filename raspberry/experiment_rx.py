"""
Reception script of the range test.

\ author Jonathan Munoz (jonathan.munoz@inria.fr), January 2017
"""

import time
import sys
import logging
import threading
import sched
import Queue
import numpy as np

import at86rf215_driver as radio
import experiment_settings as settings

PACKET_LENGTH = 2047
CRC_SIZE      = 4


class InformativeRx(threading.Thread):

    def __init__(self, queue, rx_analitics):

        # store parameters
        self.queue = queue
        self.rx_analitics = rx_analitics

        # local variables
        self.rssi_avg = 0
        self.rssi_max = 0
        self.rssi_min = 0
        self.count_rx = 0
        self.frame_last_rx = 0
        self.rx_frames = ['!' for i in range(400)]
        self.rssi_values = np.zeros(400)
        self.current_modulation = None

        # start the thread
        threading.Thread.__init__(self)
        self.name = 'InformativeRx'
        self.daemon = True
        self.start()

        # logging.basicConfig(stream=sys.__stdout__, level=logging.WARNING)
        # logging.basicConfig(filename='range_test_rx.log', level=logging.WARNING)

    def rssi_avg_func(self):
        avg = 0
        val = 0
        for rssi_val in self.rssi_values:
            val += 1
            if rssi_val < -4 and rssi_val is not 127:
                avg += rssi_val
        return avg/val

    def show_results(self):
        logging.warning('Frames received: {0}\n'.format(self.rx_frames[:]))
        logging.warning('RSSI average value: {0}\n'.format(self.rssi_avg_func()))
        self.rx_frames = ['!' for i in range(400)]
        self.rssi_values *= 0
        #for
        #self.rx_frames

    def run(self):

        while True:
            # self.rx_analitics.wait()
            # self.rx_analitics.clear()

            item = self.queue.get()
            if item == 'Start':
                if self.current_modulation is not None:
                    self.show_results()
                #self.count_rx = 0
                #self.frame_last_rx = 0

            else:
                if type(item) is tuple:
                    logging.debug('FRAME number: {0}, frame size: {1}, RSSI: {2} dBm,  CRC: {3}, MCS: {4}\n'.
                                 format( item[0][0] * 256 + item[0][1], len(item[0]), item[1], item[2], item[3]))
                    self.rx_frames[item[0][0] * 256 + item[0][1]] = '.'
                    self.rssi_values[item[0][0] * 256 + item[0][1]] = float(item[1])

                elif item == 'Print last':
                    self.show_results()
                else:
                    logging.warning('Modulation used is: {0}'.format(item))
                    self.current_modulation = item



class ExperimentRx(threading.Thread):
    
    def __init__(self, start_time):
        
        # local variables
        self.radio_driver = None
        self.start_time = start_time
        self.index = 5
        # self.start_event = start_event
        self.queue_rx = Queue.Queue()
        self.count_frames_rx = 0
        self.frame_number_last = 0

        # start the thread
        threading.Thread.__init__(self)
        self.name = 'ExperimentRx'
        self.daemon = True
        self.start()

        self.rxAnalitics = threading.Event()
        self.rxAnalitics.clear()

        self.informativeRx = InformativeRx(self.queue_rx, self.rxAnalitics)
        # configure the logging module
        # logging.basicConfig(stream= sys.__stdout__, level=logging.WARNING)
        # logging.basicConfig(filename='range_test_rx.log', level=logging.WARNING)

    def radio_setup(self):
        # initialize the radio driver
        self.radio_driver = radio.At86rf215(self._cb_rx_frame)
        self.radio_driver.radio_init(3)
        self.radio_driver.radio_reset()
        self.radio_driver.read_isr_source()  # no functional role, just clear the pending interrupt flag

    def stop_exp(self):
        """
        it makes print the last modulation results
        """
        self.queue_rx.put('Print last')

    def execute_exp(self):
        # re-configure the radio
        self.radio_driver.radio_write_config(settings.radio_configs_rx[self.index])
        self.radio_driver.radio_set_frequency(settings.radio_frequencies[self.index])

        # RX counter to zero
        self.count_frames_rx = 0
        self.queue_rx.put('Start')

        # show the config
        self.queue_rx.put(settings.radio_configs_name[self.index])
        self.index += 1
        self.radio_driver.radio_trx_enable()
        self.radio_driver.radio_rx_now()
        # self.rxAnalitics.set()
       # while True:  # main loop

            # wait for the GPS thread to indicate it's time to move to the next configuration
        #    time.sleep(10)
            # FIXME: replace by an event from the GPS thread
        #    print('TIMER 10 Seconds triggers')

    def run(self):

        self.radio_setup()
        s = sched.scheduler(time.time, time.sleep)
        s.enter(self.start_time, 1, self.execute_exp, ())
        s.enter(self.start_time + 18, 1, self.execute_exp, ())
        s.enter(self.start_time + 58, 1, self.execute_exp, ())
        s.enter(self.start_time + 98, 1, self.stop_exp, ())
        s.run()

        #while True:  # main loop

            # wait for the GPS thread to indicate it's time to move to the next configuration
        #    time.sleep(10)
            # FIXME: replace by an event from the GPS thread
        #    print('TIMER 10 Seconds triggers')
    
    #  ======================== public ========================================
    
    def getStats(self):
        raise NotImplementedError()

    #  ====================== private =========================================

    def _cb_rx_frame(self, pkt_rcv, rssi, crc, mcs):
        # self.count_frames_rx += 1
        self.queue_rx.put((pkt_rcv, rssi, crc, mcs))

        # re-arm the radio in RX mode
        self.radio_driver.radio_rx_now()

#  ========================== main ============================================


def main():
    # logging.basicConfig(filename='range_test_rx.log', level=logging.WARNING)
    logging.basicConfig(stream=sys.__stdout__, level=logging.WARNING)
    experimentRx = ExperimentRx(int(sys.argv[1]))

    while True:
        input = raw_input('>')
        if input == 's':
            print experimentRx.getStats()
            # print 'stats TODO'
        elif input == 'q':
            sys.exit(0)
            
if __name__ == '__main__':
    main()
