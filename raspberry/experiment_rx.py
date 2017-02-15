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
import json

import at86rf215_driver as radio
import experiment_settings as settings

PACKET_LENGTH = 2047
CRC_SIZE = 4


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
        self.rx_frames_eight = []
        self.rx_frames_hundred = []
        self.rx_frames_thousand = []
        self.rx_frames_two_thousand = []
        self.results = {'Time:': None, 'Modulation used is:': None, 'Results: frames received:': self.count_rx,
                        'Frames received    8 bytes long:': None,
                        'Frames received  127 bytes long:': None, 'Frames received 1000 bytes long:': None,
                        'Frames received 2047 bytes long:': None, 'RSSI average value:': None}

        # start the thread
        threading.Thread.__init__(self)
        self.name = 'InformativeRx'
        self.daemon = True
        self.start()

    def rssi_avg_func(self):
        avg = 0
        val = 0
        for rssi_val in self.rssi_values:
            val += 1
            if rssi_val < -4 and rssi_val is not 127:
                avg += rssi_val
        return avg / val

    def rx_frames_psize(self):
        """
        It assigns the values to the result dictionary by separating the burst of 400 frames into 4 groups of 100 frames
        each, knowing the first 100 correspond to 8 bytes long, 100-199 frames number correspond to 127 bytes long,
        200-299 to 1000 bytes long and 300-399 to 2047 bytes long. Also assigns the RSSI average value during the
        experiment and the modulation used.
        :returns: Nothing
        """
        # rx_frames_eight = [''.join(self.rx_frames[0:100])]
        # rx_frames_hundred = [''.join(self.rx_frames[100:200])]
        # rx_frames_thousand = [''.join(self.rx_frames[200:300])]
        # rx_frames_two_thousand = [''.join(self.rx_frames[300:400])]
        # return rx_frames_eight, rx_frames_hundred, rx_frames_thousand, rx_frames_two_thousand
        self.results['Modulation used is:'] = self.current_modulation
        self.results['Results: frames received:'] = self.count_rx
        self.results['Frames received    8 bytes long:'] = ''.join(self.rx_frames[0:100])
        self.results['Frames received  127 bytes long:'] = ''.join(self.rx_frames[100:200])
        self.results['Frames received 1000 bytes long:'] = ''.join(self.rx_frames[200:300])
        self.results['Frames received 2047 bytes long:'] = ''.join(self.rx_frames[300:400])
        self.results['RSSI average value:'] = round(self.rssi_avg_func(), 2)

    def show_results(self):
        # results = self.rx_frames_psize()
        self.rx_frames_psize()
        with open('results_rx.json', 'a') as f:
            f.write(json.dumps(self.results))

        #logging.debug('Results: frames received {4}/400\n'
        #              'Frames received    8 bytes long: {0}\n'
        #              'Frames received  127 bytes long: {1}\n'
        #              'Frames received 1000 bytes long: {2}\n'
        #              'Frames received 2047 bytes long: {3}\n'.format(results[0],
        #                                                              results[1],
        #                                                              results[2],
        #                                                              results[3],
        #                                                              self.count_rx))

        logging.debug('RSSI average value: {0}\n'.format(self.rssi_avg_func()))

    def run(self):
        self.rx_analitics.wait()
        self.rx_analitics.clear()
        while True:

            item = self.queue.get()
            if item == 'Start':
                if self.current_modulation is not None:
                    self.show_results()
                    self.rx_frames = ['!' for i in range(400)]
                    self.rssi_values *= 0
                    self.count_rx = 0
                else:
                    with open('results_rx.json', 'w') as f:
                        f.write(json.dumps('Range Test Experiment:'))
                        self.results['Time:'] = time.time()

            else:
                if type(item) is tuple:
                    logging.debug('FRAME number: {0}, frame size: {1}, RSSI: {2} dBm,  CRC: {3}, MCS: {4}\n'.
                                  format(item[0][0] * 256 + item[0][1], len(item[0]), item[1], item[2], item[3]))

                    if item[0][0] * 256 + item[0][1] < 400:
                        self.rx_frames[item[0][0] * 256 + item[0][1]] = '.'
                        self.rssi_values[item[0][0] * 256 + item[0][1]] = float(item[1])
                        self.count_rx += 1

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

        # start the threads
        threading.Thread.__init__(self)
        self.name = 'ExperimentRx'
        self.daemon = True
        self.start()

        self.rxAnalitics = threading.Event()
        self.rxAnalitics.clear()

        # initializes the InformativeRx class, in charge of the logging part
        self.informativeRx = InformativeRx(self.queue_rx, self.rxAnalitics)

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
        """
        This is the functions that reconfigures the radio at each test. It gets passed to the scheduler function.
        :return: Nothing
        """
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
        self.rxAnalitics.set()
        self.radio_driver.radio_rx_now()

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

        # while True:  # main loop

        # wait for the GPS thread to indicate it's time to move to the next configuration
        #    time.sleep(10)
        # FIXME: replace by an event from the GPS thread
        #    print('TIMER 10 Seconds triggers')

    #  ======================== public ========================================

    def getStats(self):
        raise NotImplementedError()

    #  ====================== private =========================================

    def _cb_rx_frame(self, pkt_rcv, rssi, crc, mcs):
        self.count_frames_rx += 1
        self.queue_rx.put((pkt_rcv, rssi, crc, mcs))

        # re-arm the radio in RX mode
        self.radio_driver.radio_rx_now()


# ========================== main ============================================


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
