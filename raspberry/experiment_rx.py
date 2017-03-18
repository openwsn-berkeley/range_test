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

PACKET_LENGTH = 2047
CRC_SIZE      = 4
SECURITY_TIME = 3    # 3 seconds to give more time to TRX to complete the 400 frame bursts.
START_OFFSET  = 3.5  # 3.5 seconds after the starting time arrives.


class LoggerRx(threading.Thread):
    def __init__(self, queue, settings):

        # store parameters
        self.queue = queue
        # self.end_of_series = end_of_series
        self.settings = settings
        # local variables
        self.count_rx = 0
        self.rx_frames = ['!' for i in range(len(self.settings['frame_lengths'])*self.settings['numframes'])]
        self.rssi_values = [None for i in range(len(self.settings['frame_lengths'])*self.settings['numframes'])]
        # self.name_file = '/home/pi/results/' + dt.now().strftime("%D_%H:%M:%S").replace('/', '_') + '_results.json'
        self.name_file = '/home/pi/range_test_raw_data/experiments.json'
        self.results = {'type': 'end_of_cycle_rx', 'start_time_str': time.strftime("%a, %d %b %Y %H:%M:%S UTC", time.gmtime()),
                        'start_time_epoch': time.time(), 'version': self.settings['version'], 'position_description': None,
                        'radio_settings': None, 'Rx_frames': 0, 'RSSI_by_length': None, 'RX_string': None,
                        'nmea_at_start': None, 'channel': None, 'frequency_0': None}

        # start the thread
        threading.Thread.__init__(self)
        self.name = 'LoggerRx'
        self.daemon = True
        self.start()

    def rx_frames_psize(self):
        """
        It assigns the values to the result dictionary by separating the burst of 400 frames into 4 groups of 100 frames
        each, knowing the first 100 correspond to 8 bytes long, 100-199 frames number correspond to 127 bytes long,
        200-299 to 1000 bytes long and 300-399 to 2047 bytes long. Also assigns the RSSI average value during the
        experiment and the modulation used.
        :returns: Nothing
        """
        # self.results['Frames received'] = self.count_rx
        self.results['RSSI_by_length'] = {
                '8':    self.rssi_values[0:self.settings['numframes']],
                '127':  self.rssi_values[self.settings['numframes']:2*self.settings['numframes']],
                '1000': self.rssi_values[2*self.settings['numframes']:3*self.settings['numframes']],
                '2047': self.rssi_values[3*self.settings['numframes']:4*self.settings['numframes']]
            },
        self.results['RX_string'] = {
                '8':    ''.join(self.rx_frames[0:self.settings['numframes']]),
                '127':  ''.join(self.rx_frames[self.settings['numframes']:2*self.settings['numframes']]),
                '1000': ''.join(self.rx_frames[2*self.settings['numframes']:3*self.settings['numframes']]),
                '2047': ''.join(self.rx_frames[3*self.settings['numframes']:4*self.settings['numframes']])
        }

    def show_results(self):
        self.rx_frames_psize()
        with open(self.name_file, 'a') as f:
            f.write(json.dumps([self.results.copy()]))

    def run(self):
        # logging.warning('THREAD INFORMATIVE RX 1')
        while True:
            item = self.queue.get()
            if item == 'Start':
                if self.results['radio_settings'] is not None:
                    self.show_results()  # print to log file
                    self.rx_frames = ['!' for i in range(len(self.settings['frame_lengths'])*self.settings['numframes'])]
                    self.rssi_values = [None for i in range(len(self.settings['frame_lengths'])*self.settings['numframes'])]
                    #self.count_rx = 0
                    self.results['Rx_frames'] = 0
                    self.results['start_time_str'] = time.strftime("%a, %d %b %Y %H:%M:%S UTC", time.gmtime())
                    self.results['start_time_epoch'] = time.time()
                else:
                    self.results['start_time_str'] = time.strftime("%a, %d %b %Y %H:%M:%S UTC", time.gmtime())
                    self.results['start_time_epoch'] = time.time()

            else:
                if type(item) is tuple:
                    try:
                        if item[0][0] * 256 + item[0][1] < 400:
                            self.rx_frames[item[0][0] * 256 + item[0][1]] = '.'
                            self.rssi_values[item[0][0] * 256 + item[0][1]] = float(item[1])
                            # self.count_rx += 1
                            self.results['Rx_frames'] += 1
                    except Exception:
                        logging.warning('item: {0}'.format(item))

                elif item == 'Print last':
                    self.show_results()
                    self.results['radio_settings'] = None
                    # with open(self.name_file, 'a') as f:
                    #    f.write(json.dumps(self.results))

                elif type(item) == float:
                    logging.warning('TIME: {0}'.format(item))

                elif type(item) is dict:
                    self.results['frequency_0'] = item['frequency_0_kHz']
                    self.results['channel'] = item['channel']
                    self.results['radio_settings'] = item['modulation']

                else:
                    logging.warning('UNKNOWN ITEM')

        # logging.warning('THREAD INFORMATIVE RX 2')


class ExperimentRx(threading.Thread):
    """
    :param time_to_run: tuple (hours, minutes) for the next TRX experiment to run
    """
    def __init__(self, time_to_run, settings):
        # local variables
        self.radio_driver = None
        self.settings = settings
        self.hours = time_to_run[0]
        self.minutes = time_to_run[1]
        self.first_run = False
        self.queue_rx = Queue.Queue()
        self.count_frames_rx = 0
        self.started_time = time.time()
        self.cumulative_time = 0
        self.schedule = [None for i in range(len(self.settings["test_settings"]))]

        # start the threads
        self.end_of_series = threading.Event()
        self.end_of_series.clear()
        threading.Thread.__init__(self)
        self.name = 'ExperimentRx'
        self.daemon = True
        self.start()

        # initializes the LoggerRx class, in charge of the logging part
        # self.LoggerRx = LoggerRx(self.queue_rx, self.end_of_series, self.settings)
        self.LoggerRx = LoggerRx(self.queue_rx, self.settings)

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
        self.end_of_series.set()

    def experiment_scheduling(self):
        """
        it schedules each set of settings to be run
        :return: Nothing
        """
        s = sched.scheduler(time.time, time.sleep)
        time_to_start = dt.combine(dt.now(), datetime.time(self.hours, self.minutes))
        if self.first_run is False:
            offset = START_OFFSET
            self.first_run = True
            logging.warning('TIME: {0}'.format(time_to_start))
        else:
            offset = self.cumulative_time + 2
        for item in self.settings['test_settings']:
            s.enterabs(time.mktime(time_to_start.timetuple()) + offset, 1, self.execute_exp, (item,))
            self.schedule[self.settings['test_settings'].index(item)] = offset
            offset += item['durationtx_s'] + SECURITY_TIME
        self.cumulative_time = offset
        logging.warning(self.schedule)
        s.enterabs(time.mktime(time_to_start.timetuple()) + offset, 1, self.stop_exp, ())
        s.run()

    # def next_run_time(self):
    #     """
    #     it sets the next runtime for the whole experiment sequence in hours, minutes
    #     current_time[3] = hours, current_time[4] = minutes, current_time[5] = seconds
    #     :return: hours, minutes
    #     """
    #     current_time = time.gmtime()
    #     if current_time[5] < 50:
    #         if current_time[4] is not 59:
    #             new_time = current_time[3], current_time[4]+1
    #         else:
    #             new_time = (current_time[3] + 1) % 24, 0
    #     else:
    #         if current_time[4] is 59:
    #             new_time = (current_time[3] + 1) % 24, 1
    #         else:
    #             new_time = current_time[3], current_time[4] + 2
    #
    #     return new_time

    def execute_exp(self, item):
        """
        This is the functions that reconfigures the radio at each test. It gets passed to the scheduler function.
        :return: Nothing
        """
        # reset the radio to erase previous configuration
        self.radio_driver.radio_reset()

        self.radio_driver.radio_write_config(defs.modulations_settings[item['modulation']])
        self.radio_driver.radio_set_frequency((item['channel_spacing_kHz'],
                                               item['frequency_0_kHz'],
                                               item['channel']))

        # RX counter to zero
        self.count_frames_rx = 0
        self.queue_rx.put('Start')

        # show the config
        self.queue_rx.put(item)

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
        while True:
            self.experiment_scheduling()
            self.end_of_series.wait()
            self.end_of_series.clear()
            # self.hours, self.minutes = self.next_run_time()

        # FIXME: replace by an event from the GPS thread

    #  ======================== public ========================================

    def getStats(self):
        # logging.warning('Results ongoing {0}'.format(self.LoggerRx.results_per_settings))
        logging.warning('SHOW SOMETHING HERE')


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


def following_time_to_run():
    """
    it sets the next runtime for the whole experiment sequence in hours, minutes
    current_time[3] = hours, current_time[4] = minutes, current_time[5] = seconds
    :return: hours, minutes
    """
    current_time = time.gmtime()
    if current_time[5] < 50:
        if current_time[4] is not 59:
            new_time = current_time[3], current_time[4] + 1
        else:
            new_time = (current_time[3] + 1) % 24, 0
    else:
        if current_time[4] is 59:
            new_time = (current_time[3] + 1) % 24, 1
        else:
            new_time = current_time[3], current_time[4] + 2

    return new_time


def main():

    logging.basicConfig(stream=sys.__stdout__, level=logging.WARNING)
    experimentRx = ExperimentRx(following_time_to_run(), load_experiment_details())

    while True:
        input = raw_input('>')
        if input == 's':
            print experimentRx.getStats()
        elif input == 'q':
            sys.exit(0)

if __name__ == '__main__':
    main()
