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
import json
from datetime import datetime as dt
import datetime
import socket

import at86rf215_defs as defs
import at86rf215_driver as radio
import GpsThread as gps

PACKET_LENGTH       = 2047
CRC_SIZE            = 4
SECURITY_TIME       = 3    # 3 seconds to give more time to TRX to complete the 400 frame bursts.
START_OFFSET        = 3.5  # 3.5 seconds after the starting time arrives.
FCS_VALID           = 1
FRAME_MINIMUM_SIZE  = 7


class LoggerRx(threading.Thread):
    def __init__(self, queue, settings):

        # store parameters
        self.queue              = queue
        self.settings           = settings

        # local variables
        self.rx_string          = ['!' for i in range(len(self.settings['frame_lengths'])*self.settings['numframes'])]
        self.rssi_values        = [None for i in range(len(self.settings['frame_lengths'])*self.settings['numframes'])]
        self.name_file          = '/home/pi/range_test_raw_data/experiments_results_' + socket.gethostname() + '.json'
        self.results            = {'type': 'end_of_cycle_rx', 'start_time_str': time.strftime(
            "%a, %d %b %Y %H:%M:%S UTC", time.gmtime()), 'start_time_epoch': time.time(), 'version': self.settings[
            'version'], 'position_description': None, 'radio_settings': None, 'rx_frames_count': 0, 'RSSI_by_length': None,
                        'rx_string': None, 'GPSinfo_at_start': None, 'channel': None, 'frequency_0': None,
                                   'burst_size': self.settings['numframes'], 'id': socket.gethostname(),
                                   'rx_frames_wrong_fcs_count': 0, 'rx_frames_wrong_fcs_sequence_number': []}

        # start the thread
        threading.Thread.__init__(self)
        self.name               = 'LoggerRx'
        self.daemon             = True
        self.start()

    def rx_frames_psize(self):
        """
        It assigns the values to the result dictionary by separating the burst of 400 frames into 4 groups of 100 frames
        each, knowing the first 100 correspond to 8 bytes long, 100-199 frames number correspond to 127 bytes long,
        200-299 to 1000 bytes long and 300-399 to 2047 bytes long. Also assigns the RSSI average value during the
        experiment and the modulation used.
        :returns: Nothing
        """

        self.results['RSSI_by_length'] = {
                '8':    self.rssi_values[0:self.settings['numframes']],
                '127':  self.rssi_values[self.settings['numframes']:2*self.settings['numframes']],
                '1000': self.rssi_values[2*self.settings['numframes']:3*self.settings['numframes']],
                '2047': self.rssi_values[3*self.settings['numframes']:4*self.settings['numframes']]
            },
        self.results['rx_string'] = {
                '8':    ''.join(self.rx_string[0:self.settings['numframes']]),
                '127':  ''.join(self.rx_string[self.settings['numframes']:2*self.settings['numframes']]),
                '1000': ''.join(self.rx_string[2*self.settings['numframes']:3*self.settings['numframes']]),
                '2047': ''.join(self.rx_string[3*self.settings['numframes']:4*self.settings['numframes']])
        }

    def print_results(self):
        """
        it will print the results of the previous experiment in the output file
        :return:
        """
        self.rx_frames_psize()
        with open(self.name_file, 'a') as f:
            f.write(json.dumps(self.results.copy())+'\n')

    def run(self):
        """
        analyses the frames received by the radio that are put in the logger queue. It stars filling the results of
        the current experiment.
        :return:
        """

        while True:
            item = self.queue.get()
            if item == 'Start':
                if self.results['radio_settings']:  # to know if this is the first time I pass in the logger
                    self.print_results()  # print to log file
                self.rx_string = ['!' for i in range(len(self.settings['frame_lengths']) * self.settings['numframes'])]
                self.rssi_values = [None for i in
                                    range(len(self.settings['frame_lengths']) * self.settings['numframes'])]
                self.results['rx_frames_count'] = 0
                self.results['start_time_str'] = time.strftime("%a, %d %b %Y %H:%M:%S UTC", time.gmtime())
                self.results['start_time_epoch'] = time.time()
                self.results['rx_frames_wrong_fcs_count'] = 0
                self.results['rx_frames_wrong_fcs_sequence_number'] = []

            elif type(item) is tuple:
                # verify size of the tuple
                if len(item) == 4:
                    if item[2] is FCS_VALID:  # check frame correctness.
                        if len(item[0]) > FRAME_MINIMUM_SIZE:
                            try:
                                if item[0][0] * 256 + item[0][1] < 400 and (item[0][2], item[0][3]) == (0x00, 0x01):
                                    self.rx_string[item[0][0] * 256 + item[0][1]] = '.'
                                    self.rssi_values[item[0][0] * 256 + item[0][1]] = float(item[1])
                                    self.results['rx_frames_count'] += 1
                                else:
                                    logging.warning('UNKNOWN ITEM (frame_rcv, rssi, crc, mcs): {0}'.format(item))

                            except IndexError as err:
                                logging.warning('item: {0}'.format(item))
                                logging.warning('frame not sent within the experiment, unknown sender')
                                logging.warning(err)
                    else:
                        try:
                            self.results['rx_frames_wrong_fcs_sequence_number'].append(item[0][0] * 256 + item[0][1])

                        except IndexError as err:
                            logging.warning('UNKNOWN: {0}'.format(item))
                            logging.warning(err)
                        self.results['rx_frames_wrong_fcs_count'] += 1  # Frame received but wrong.

                else:
                    logging.error('UNKNOWN OBJECT IN THE QUEUE: {0}'.format(item))

            elif item == 'Print last':
                self.print_results()
                self.results['radio_settings'] = None  # by doing this I won't print twice the last set of settings.

            elif type(item) == float:
                logging.info('TIME: {0}'.format(item))

            elif type(item) is dict:
                if item.get('frequency_0_kHz') is not None:
                    self.results['frequency_0'] = item['frequency_0_kHz']
                    self.results['channel'] = item['channel']
                    self.results['radio_settings'] = item['modulation']

                else:
                    self.results['GPSinfo_at_start'] = item
            else:
                logging.error('UNKNOWN ITEM IN THE QUEUE: {0}'.format(item))


class ExperimentRx(threading.Thread):

    def __init__(self, settings):
        # local variables
        self.radio_driver       = None
        self.settings           = settings
        self.hours              = 0
        self.minutes            = 0
        self.first_run          = False
        self.queue_rx           = Queue.Queue()
        self.started_time       = None
        self.cumulative_time    = 0
        self.led_array_pins     = [29, 31, 33, 35, 37]
        self.frame_received_pin = [36]
        self.scheduler          = sched.scheduler(time.time, time.sleep)
        self.list_events_sched  = [None for i in range(len(self.settings["test_settings"]))]
        self.scheduler_aux      = None
        self.schedule_time      = [None for i in range(len(self.settings["test_settings"]))]
        self.time_to_start      = None
        self.f_start_signal_LED = False
        self.f_break_rx         = False

        # start the threads
        self.start_experiment   = threading.Event()
        self.end_of_series      = threading.Event()
        self.f_schedule         = threading.Event()
        self.dataLock           = threading.RLock()
        self.start_experiment.clear()
        self.end_of_series.clear()
        self.f_schedule.clear()
        self.gps                = None
        self.LoggerRx           = None

        threading.Thread.__init__(self)
        self.name = 'ExperimentRx_'
        self.daemon = True
        self.start()

    def radio_setup(self):
        """
        it initialises the radio driver, it loads the callback for the RX
        :return:
        """
        # initialize the radio driver
        self.radio_driver   = radio.At86rf215(self._cb_rx_frame, self.start_experiment, self.end_of_series)
        self.radio_driver.radio_init(11, 13)

        # initializes the LoggerRx thread
        self.LoggerRx       = LoggerRx(self.queue_rx, self.settings)

        # # start the gps thread
        self.gps            = gps.GpsThread()

        # init LED's pins
        self.radio_driver.init_binary_pins(self.led_array_pins)
        self.radio_driver.init_binary_pins(self.frame_received_pin)
        self.radio_driver.radio_reset()
        self.radio_driver.read_isr_source()  # no functional role, just clear the pending interrupt flag

        # waiting until the GPS time is valid
        logging.info('waiting for valid GPS time...')
        while self.gps.is_gps_time_valid() is False:
            time.sleep(1)
        logging.info('... time valid')

    def time_experiment(self):
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

    def stop_exp(self):
        """
        it makes print the last modulation results
        """
        self.queue_rx.put('Print last')
        with self.dataLock:
            self.end_of_series.set()

    def experiment_scheduling(self):
        """
        it schedules each set of settings to be run
        :return: Nothing
        """

        logging.info('entering the experiment_scheduling')
        while True:
            logging.info('IN THE experiment_scheduling WAITING FOR THE self.f_schedule.set')
            self.f_schedule.wait()
            self.f_schedule.clear()
            logging.info('START SCHEDULING STUFF')
            if self.first_run is False:
                offset = START_OFFSET
                self.first_run = True
                logging.info('TIME THREAD experiment_scheduling time_to_start: {0}'.format(self.time_to_start))
            else:
                offset = self.cumulative_time + 2
            for item in self.settings['test_settings']:
                self.list_events_sched[self.settings['test_settings'].index(item)] = self.scheduler.enterabs(
                    time.mktime(self.time_to_start.timetuple()) + offset, 1, self.execute_exp, (item,))
                self.schedule_time[self.settings['test_settings'].index(item)] = offset
                offset += item['durationtx_s'] + SECURITY_TIME
            self.cumulative_time = offset
            logging.info('time for each set of settings: {0}'.format(self.schedule_time))
            self.scheduler.enterabs(time.mktime(self.time_to_start.timetuple()) + offset, 1, self.stop_exp, ())
            self.scheduler.run()
            logging.info('END OF THE experiment_scheduling')

    def execute_exp(self, item):
        """
        This is the functions that reconfigures the radio at each test. It gets passed to the scheduler function.
        :return: Nothing
        """
        # clean the break execute_exp flag
        self.radio_driver.clean_reset_cmd()

        # reset the radio to erase previous configuration
        self.radio_driver.radio_reset()
        self.radio_driver.LED_OFF(self.frame_received_pin)

        self.radio_driver.radio_write_config(defs.modulations_settings[item['modulation']])
        self.radio_driver.radio_set_frequency((item['channel_spacing_kHz'],
                                               item['frequency_0_kHz'],
                                               item['channel']))

        self.radio_driver.binary_counter(item['index'], self.led_array_pins)
        logging.info('modulation: {0}'.format(item["modulation"]))

        # sends the signal to the logger class through queue, letting it know a new experiment just started.
        self.queue_rx.put('Start')

        # sends the config to the logger class through queue
        self.queue_rx.put(item)

        # sends the  GPS info to the logger class through queue
        self.queue_rx.put(self.gps.gps_info_read())

        # put the radio into RX mode
        self.radio_driver.radio_trx_enable()
        self.radio_driver.radio_rx_now()
        self.queue_rx.put(time.time() - self.started_time)

        # while True:
        #     time.sleep(1)
        #     # logging.info('listening')
        #     if self.f_break_rx:
        #         self.f_break_rx = False
        #         break
        # while True:  # main loop
        # wait for the GPS thread to indicate it's time to move to the next configuration
        #    time.sleep(10)
        # FIXME: replace by an event from the GPS thread
        #    print('TIMER 10 Seconds triggers')

    def remove_scheduled_experiment(self):
        events = self.scheduler.queue
        # get the scheduled events
        logging.info('events: {0}'.format(events))
        for ev in events:
            self.scheduler.cancel(ev)
        logging.info('events in queue: {0}'.format(self.scheduler.queue))
        # self.radio_driver.clean_reset_cmd()

    def LED_start_exp(self):
        """
        it lights on a LED if the experiment will take place in the next minute
        it uses the frame receive LED to indicate whether the experiment is going to start the next minute or not.
        :return:
        """
        while not self.f_start_signal_LED:
            now = time.gmtime()
            if self.minutes - now[4] == 1 or self.minutes - now[4] == -59:
                self.radio_driver.LED_ON(self.frame_received_pin)
                self.f_start_signal_LED = True
                continue
            time.sleep(1)
        self.f_start_signal_LED = False

    def run(self):
        # setup the radio
        self.radio_setup()
        logging.info('WAITING FOR THE START BUTTON TO BE PRESSED')

        # push button signal
        self.start_experiment.wait()
        self.start_experiment.clear()

        # gets current time and determines the running time for the experiment to start
        self.started_time = time.time()
        self.hours, self.minutes = self.time_experiment()
        self.time_to_start = dt.combine(dt.now(), datetime.time(self.hours, self.minutes))

        # it start the scheduler thread
        self.scheduler_aux = threading.Thread(target=self.experiment_scheduling)
        self.scheduler_aux.start()
        self.scheduler_aux.name = 'Scheduler Rx'
        logging.info('waiting the end of the experiment')

        # gives the signal to the scheduler to start scheduling the 31 experiments
        with self.dataLock:
            self.f_schedule.set()

        # it will switch on the LED frame_received_pin to let the user know the experiment will start the following
        # minute
        self.LED_start_exp()

        while True:

            # it waits for the self.end_of_series signal that can be triggered at the end of the 31st experiment
            # or when the push button is pressed
            self.end_of_series.wait()
            self.end_of_series.clear()

            # if push button, removes all the experiments scheduled
            if self.radio_driver.read_reset_cmd():
                self.radio_driver.LED_OFF(self.frame_received_pin)
                self.f_break_rx = True
                logging.info('button pressed')
                logging.info('RESETTING SCHEDULE')
                self.remove_scheduled_experiment()
                logging.info('removed items in the queue')
                self.radio_driver.radio_off()
                self.started_time = time.time()

                # determines the starting time for the new set of experiments
                self.hours, self.minutes = self.time_experiment()
                self.time_to_start = dt.combine(dt.now(), datetime.time(self.hours, self.minutes))
                logging.info('WITHIN THE WHILE TRUE MAIN --->> self.time_to_start: {0}'.format(self.time_to_start))
                logging.info('removed items in the queue')
                self.cumulative_time = 0
                self.first_run = False
                self.radio_driver.binary_counter(0, self.led_array_pins)
                logging.info('before self.LED_start_exp()')
                self.LED_start_exp()
                logging.info('after self.LED_start_exp()')

            # gives the signal to the scheduler thread to re-schedule the experiments
            with self.dataLock:
                self.f_schedule.set()

    #  ======================== public ========================================

    def getStats(self):
        # logging.warning('Results ongoing {0}'.format(self.LoggerRx.results))
        logging.warning('TO IMPLEMENT')

    #  ====================== private =========================================

    def _cb_rx_frame(self, frame_rcv, rssi, crc, mcs):
        self.radio_driver.LED_toggle(self.frame_received_pin)
        # self.count_frames_rx += 1
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

    logging.basicConfig(stream=sys.__stdout__, level=logging.DEBUG)
    experimentRx = ExperimentRx(load_experiment_details())

    while True:
        input = raw_input('>')
        if input == 's':
            print experimentRx.getStats()
        elif input == 'q':
            sys.exit(0)

if __name__ == '__main__':
    main()
