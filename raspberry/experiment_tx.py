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
import json
from datetime import datetime as dt
import datetime

import at86rf215_defs as defs
import at86rf215_driver as radio

FRAME_LENGTH  = 2047
CRC_SIZE      = 4
SECURITY_TIME = 3  # 3 seconds to give more time to TRX to complete the 400 frame bursts.
START_OFFSET  = 4.5  # 4.5 seconds after the starting time arrives.


class InformativeTx(threading.Thread):

    def __init__(self, queue, end, settings):

        # store parameters
        self.queue = queue
        self.results = {'Time Experiment:': time.strftime("%a, %d %b %Y %H:%M:%S UTC", time.gmtime()),
                        'Time for this set of settings:': None}
        self.settings = settings
        self.end = end
        # local variables
        self.name_file = '/home/pi/range_test_raw_data/experiments.json'
        # self.current_modulation = None
        self.results = {'type': 'end_of_cycle_tx', 'start_time_str': time.strftime("%a, %d %b %Y %H:%M:%S UTC", time.gmtime()),
                        'start_time_epoch': time.time(), 'radio_settings': None, 'nmea_at_start': None,
                        'version': self.settings['version'], 'channel': None, 'frequency_0': None}

        # start the thread
        threading.Thread.__init__(self)
        self.name = 'InformativeTx'
        self.daemon = True
        self.start()

        logging.basicConfig(stream=sys.__stdout__, level=logging.WARNING)

    def run(self):
        logging.warning('THREAD INFORMATIVE TX 1')
        # while not self.end:
        while True:
            item = self.queue.get()
            if item == 'Start':
                self.results['start_time_str'] = time.strftime("%a, %d %b %Y %H:%M:%S UTC", time.gmtime())
                self.results['start_time_epoch'] = time.time()
                if self.results['radio_settings'] is not None:
                    with open(self.name_file, 'a') as f:
                        f.write(json.dumps(self.results.copy()))

            elif item == 'Print last':
                with open(self.name_file, 'a') as f:
                    f.write(json.dumps(self.results.copy()))

            elif type(item) is tuple:
                logging.warning('Time to send the frames {0} - {1} was {2} seconds\n'.format(item[0] - 100, item[0],
                                                                                             item[1]))
            elif type(item) is dict:
                self.results['frequency_0'] = item['frequency_0_kHz']
                self.results['channel'] = item['channel']
                self.results['radio_settings'] = item['modulation']
            elif type(item) is float:
                logging.warning('Time {0}'.format(item))
            else:
                logging.warning('UNKNOWN ITEM')


class ExperimentTx(threading.Thread):
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
        self.queue_tx = Queue.Queue()
        self.started_time = time.time()
        self.schedule = ['time' for i in range(len(self.settings["test_settings"]))]
        # self.program_running = threading.Event()
        # self.program_running.clear()
        self.end = threading.Event()
        self.end.clear()
        # start the thread
        threading.Thread.__init__(self)
        self.name = 'ExperimentTx_'
        self.daemon = True
        self.start()

        self.informativeTx = InformativeTx(self.queue_tx, self.end, self.settings)

        # configure the logging module
        logging.basicConfig(stream=sys.__stdout__, level=logging.WARNING)

    def radio_setup(self):

        # initialize the radio driver
        self.radio_driver = radio.At86rf215(self._cb_rx_frame)
        self.radio_driver.radio_init(3)
        self.radio_driver.radio_reset()
        # self.radio_driver.read_isr_source()  # no functional role, just clear the pending interrupt flag

    def next_run_time(self):
        """
        it sets the next runtime for the whole experiment sequence in hours, minutes
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

    def stop_exp(self):
        """
        it makes print the last modulation results
        """
        self.queue_tx.put('Print last')
        self.end.set()

    def experiment_scheduling(self):
        s = sched.scheduler(time.time, time.sleep)
        time_to_start = dt.combine(dt.now(), datetime.time(self.hours, self.minutes))
        if self.first_run is False:
            offset = START_OFFSET
            self.first_run = True
        else:
            offset = 0
        for item in self.settings['test_settings']:
            s.enterabs(time.mktime(time_to_start.timetuple()) + offset, 1, self.execute_exp, (item,))
            self.schedule[self.settings['test_settings'].index(item)] = offset
            offset += item['durationtx_s'] + SECURITY_TIME
        logging.warning(self.schedule)
        s.enterabs(time.mktime(time_to_start.timetuple()) + offset, 1, self.stop_exp, ())
        s.run()

    def execute_exp(self, item):
        self.queue_tx.put(time.time() - self.started_time)
        # initialize the frame counter
        frame_counter = 0

        # reset the radio to erase previous configuration
        self.radio_driver.radio_reset()

        # re-configure the radio
        self.radio_driver.radio_write_config(defs.modulations_settings[item['modulation']])

        # select the frequency
        self.radio_driver.radio_off()
        self.radio_driver.radio_set_frequency((item['channel_spacing_kHz'],
                                               item['frequency_0_kHz'],
                                               item['channel']))

        # let know to the informative class the beginning of a new experiment
        self.queue_tx.put('Start')

        # log the config name
        self.queue_tx.put(item)

        # loop through packet lengths
        for frame_length, ifs in zip(self.settings["frame_lengths"], self.settings["IFS"]):

            # now = time.time()
            self.radio_driver.radio_trx_enable()
            # send burst of frames
            for i in range(self.settings['numframes']):

                # create frame
                frameToSend = [frame_counter >> 8, frame_counter & 0xFF] + [i & 0xFF for i in range(FRAME_LENGTH - 2)]

                # increment the frame counter
                frame_counter += 1

                # send frame
                self.radio_driver.radio_load_packet(frameToSend[:frame_length - CRC_SIZE])
                self.radio_driver.radio_tx_now()

                # IFS
                time.sleep(ifs)
    
    def run(self):
        self.radio_setup()
        while True:
            # logging.warning('THREAD EXPERIMENT TX')
            self.experiment_scheduling()
            self.end.wait()
            self.end.clear()
            # self.hours, self.minutes = self.next_run_time()

    #  ======================== private =======================================
    
    def _cb_rx_frame(self, frame_rcv, rssi, crc, mcs):
        raise SystemError("frame received on transmitting mote")

#  ============================ main ==========================================


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
    experimentTx = ExperimentTx(following_time_to_run(), load_experiment_details())

    while True:
        input = raw_input('>')
        if input == 's':
            print experimentTx.getStats()
            # print 'print stats TX'
        if input == 'q':
            sys.exit(0)

if __name__ == '__main__':
    main()
