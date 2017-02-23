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
from datetime import datetime as dt
import datetime

import at86rf215_defs as defs
import at86rf215_driver as radio
# import experiment_settings as settings

PACKET_LENGTH = 2047
CRC_SIZE = 4
SECURITY_TIME = 3


class InformativeRx(threading.Thread):
    def __init__(self, queue):

        # store parameters
        self.queue = queue

        # local variables
        self.rssi_avg = 0
        self.rssi_max = 0
        self.rssi_min = 0
        self.count_rx = 0
        self.frame_last_rx = 0
        self.rx_frames = ['!' for i in range(400)]
        self.rssi_values = np.zeros(400)
        self.name_file = '/home/pi/results/' + dt.now().strftime("%D_%H_%M_%S").replace('/', '_') + '_results.json'
        self.current_modulation = None
        self.rx_frames_eight = []
        self.rx_frames_hundred = []
        self.rx_frames_thousand = []
        self.rx_frames_two_thousand = []
        self.results = {'Time Experiment:': time.strftime("%a, %d %b %Y %H:%M:%S UTC", time.gmtime()),
                        'Time for this set of settings:': None,
                        'Modulation used is:': None, 'Results: frames received:': self.count_rx,
                        'Frames received    8 bytes long:': None, 'Frames received  127 bytes long:': None,
                        'Frames received 1000 bytes long:': None, 'Frames received 2047 bytes long:': None,
                        'RSSI average value:': None}

        self.results_per_settings = {}
        # start the thread
        threading.Thread.__init__(self)
        self.name = 'InformativeRx'
        self.daemon = True
        self.start()

    def rssi_avg_func(self):
        avg = 0
        val = 0
        for rssi_val in self.rssi_values:
            if rssi_val < -4 and rssi_val is not 127:
                val += 1
                avg += rssi_val
        if val != 0:
            result = avg / val
        else:
            result = 0
        # logging.warning(self.rssi_values)
        return result

    def rx_frames_psize(self):
        """
        It assigns the values to the result dictionary by separating the burst of 400 frames into 4 groups of 100 frames
        each, knowing the first 100 correspond to 8 bytes long, 100-199 frames number correspond to 127 bytes long,
        200-299 to 1000 bytes long and 300-399 to 2047 bytes long. Also assigns the RSSI average value during the
        experiment and the modulation used.
        :returns: Nothing
        """
        self.results['Modulation used is:'] = self.current_modulation
        self.results['Results: frames received:'] = self.count_rx
        self.results['Frames received    8 bytes long:'] = ''.join(self.rx_frames[0:100])
        self.results['Frames received  127 bytes long:'] = ''.join(self.rx_frames[100:200])
        self.results['Frames received 1000 bytes long:'] = ''.join(self.rx_frames[200:300])
        self.results['Frames received 2047 bytes long:'] = ''.join(self.rx_frames[300:400])
        self.results['RSSI average value:'] = round(self.rssi_avg_func(), 2)

    def show_results(self):
        self.rx_frames_psize()
        self.results_per_settings[self.results['Modulation used is:']] = self.results

    def run(self):

        self.results['Time for this set of settings:'] = time.strftime("%a, %d %b %Y %H:%M:%S UTC", time.gmtime())

        while True:

            item = self.queue.get()
            if item == 'Start':
                if self.current_modulation is not None:
                    self.show_results()
                    self.rx_frames = ['!' for i in range(400)]
                    self.rssi_values *= 0
                    self.count_rx = 0

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
                    with open(self.name_file, 'a') as f:
                        f.write(json.dumps(self.results_per_settings))

                elif type(item) == float:
                    logging.warning('TIME: {0}'.format(item))
                else:
                    logging.warning('Modulation used is: {0}'.format(item))
                    self.current_modulation = item


class ExperimentRx(threading.Thread):
    def __init__(self, hours, minutes, settings):
        # local variables
        self.radio_driver = None
        self.settings = settings
        self.hours = hours
        self.minutes = minutes
        self.end = False
        self.queue_rx = Queue.Queue()
        self.count_frames_rx = 0
        self.started_time = time.time()
        self.schedule = ['time' for i in range(31)]

        # start the threads
        threading.Thread.__init__(self)
        self.name = 'ExperimentRx'
        self.daemon = True
        self.start()

        # initializes the InformativeRx class, in charge of the logging part
        self.informativeRx = InformativeRx(self.queue_rx)

    def radio_setup(self):
        """
        it initialises the radio driver, it loads the callback for the RX
        :return:
        """
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
        self.end = True

    def experiment_scheduling(self):
        """
        it schedules each set of settings to be run
        :return: Nothing
        """
        s = sched.scheduler(time.time, time.sleep)
        time_to_start = dt.combine(dt.now(), datetime.time(self.hours, self.minutes))
        logging.warning('TIME: {0}'.format(time_to_start))
        offset = 1.5
        for item in self.settings['test_settings']:
            s.enterabs(time.mktime(time_to_start.timetuple()) + offset, 1, self.execute_exp, (item,))
            self.schedule[self.settings['test_settings'].index(item)] = offset
            offset += item['durationtx_s'] + SECURITY_TIME
        logging.warning(self.schedule)
        s.enterabs(time.mktime(time_to_start.timetuple()) + offset, 1, self.stop_exp, ())
        s.run()

    def execute_exp(self, item):
        """
        This is the functions that reconfigures the radio at each test. It gets passed to the scheduler function.
        :return: Nothing
        """
        self.radio_driver.radio_write_config(defs.modulations_settings[item['modulation']])
        self.radio_driver.radio_set_frequency((item['channel_spacing_kHz'],
                                               item['frequency_0_kHz'],
                                               item['channel']))

        # RX counter to zero
        self.count_frames_rx = 0
        self.queue_rx.put('Start')

        # show the config
        self.queue_rx.put(item['modulation'])

        # put the radio into RX mode
        self.radio_driver.radio_trx_enable()
        self.radio_driver.radio_rx_now()
        self.queue_rx.put(time.time() - self.started_time)

        # while True:  # main loop
        # wait for the GPS thread to indicate it's time to move to the next configuration
        #    time.sleep(10)
        # FIXME: replace by an event from the GPS thread
        #    print('TIMER 10 Seconds triggers')

    def run(self):
        self.radio_setup()
        self.experiment_scheduling()

        # FIXME: replace by an event from the GPS thread

    #  ======================== public ========================================

    def getStats(self):
        logging.warning('Results ongoing {0}'.format(self.informativeRx.results_per_settings))

    #  ====================== private =========================================

    def _cb_rx_frame(self, frame_rcv, rssi, crc, mcs):
        self.count_frames_rx += 1
        self.queue_rx.put((frame_rcv, rssi, crc, mcs))

        # re-arm the radio in RX mode
        self.radio_driver.radio_rx_now()

# ========================== main ============================================


def load_experiment_details():
    with open('/home/pi/range_test/raspberry/experiment_settings.json', 'r') as f:
        settings = f.read().replace('\n', ' ').replace('\r', '')
        settings = json.loads(settings)
        return settings


def main():
    hours = int(sys.argv[1])
    minutes = int(sys.argv[2])
    # logging.basicConfig(filename='range_test_rx.log', level=logging.WARNING)
    logging.basicConfig(stream=sys.__stdout__, level=logging.WARNING)
    experimentRx = ExperimentRx(hours, minutes, load_experiment_details())

    while experimentRx.end is False:
        input = raw_input('>')
        if input == 's':
            print experimentRx.getStats()
        elif input == 'q':
            sys.exit(0)
    logging.warning('Experiment END Variable: {0}'.format(experimentRx.end))
    sys.exit(0)

if __name__ == '__main__':
    main()
