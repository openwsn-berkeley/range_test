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
import socket
from threading import Timer

import at86rf215_defs as defs
# import RPi.GPIO as GPIO
import at86rf215_driver as radio
import GpsThread as gps
import gpio_handler as gpio

FRAME_LENGTH  = 2047
CRC_SIZE      = 4
SECURITY_TIME = 3  # 3 seconds to give more time to TRX to complete the 400 frame bursts.
START_OFFSET  = 4.5  # 4.5 seconds after the starting time arrives.


class LoggerTx(threading.Thread):

    def __init__(self, queue, settings):

        # store parameters
        self.queue = queue
        self.settings = settings

        # local variables
        self.name_file = '/home/pi/range_test_raw_data/experiments_results_' + socket.gethostname() + '.json'
        self.results = {'type': 'end_of_cycle_tx', 'start_time_str': time.strftime("%a, %d %b %Y %H:%M:%S UTC", time.gmtime()),
                        'start_time_epoch': time.time(), 'radio_settings': None, 'GPSinfo_at_start': None,
                        'version': self.settings['version'], 'channel': None, 'frequency_0': None,
                        'burst_size': self.settings['numframes'], 'id': socket.gethostname()}

        # start the thread
        threading.Thread.__init__(self)
        self.name = 'LoggerTx'
        self.daemon = True
        self.start()

        logging.basicConfig(stream=sys.__stdout__, level=logging.DEBUG)

    def run(self):
        while True:
            item = self.queue.get()
            if item == 'Start':
                if self.results['radio_settings']:
                    with open(self.name_file, 'a') as f:
                        f.write(json.dumps(self.results.copy())+'\n')
                self.results['start_time_str'] = time.strftime("%a, %d %b %Y %H:%M:%S UTC", time.gmtime())
                self.results['start_time_epoch'] = time.time()

            elif item == 'Print last':
                with open(self.name_file, 'a') as f:
                    f.write(json.dumps(self.results.copy())+'\n')

            elif type(item) is tuple:
                logging.info('Time to send the frames {0} - {1} was {2} seconds\n'.format(item[0] - 100, item[0],
                                                                                             item[1]))
            elif type(item) is dict:
                if item.get('frequency_0_kHz') is not None:
                    self.results['frequency_0'] = item['frequency_0_kHz']
                    self.results['channel'] = item['channel']
                    self.results['radio_settings'] = item['modulation']
                else :
                    self.results['GPSinfo_at_start'] = item
            elif type(item) is float:
                logging.info('Time {0}'.format(item))
            else:
                logging.error('UNKNOWN ITEM IN THE QUEUE: {0}.'.format(item))


class ExperimentTx(threading.Thread):

    def __init__(self, settings):
        
        # local variables

        self.settings               = settings
        self.hours                  = 0
        self.minutes                = 0
        self.first_run              = False
        self.queue_tx               = Queue.Queue()
        self.started_time           = None
        self.f_start_signal_LED     = False
        self.f_reset_button         = False
        self.f_reset                = False
        self.cumulative_time        = 0
        self.radio_isr_pin          = 11
        self.push_button_pin        = 13
        self.scheduler              = sched.scheduler(time.time, time.sleep)
        self.list_events_sched      = [None for i in range(len(self.settings["test_settings"]))]
        self.schedule_time          = ['time' for i in range(len(self.settings["test_settings"]))]
        self.led_array_pins         = [29, 31, 33, 35, 37]
        self.frame_sent_pin         = [36]
        self.scheduler_aux          = None
        self.time_to_start          = None
        self.dataLock               = threading.RLock()

        # start the threads
        self.end_experiment          = threading.Event()
        self.start_experiment       = threading.Event()
        self.f_schedule             = threading.Event()
        self.end_experiment.clear()
        self.start_experiment.clear()
        self.f_schedule.clear()

        # start the thread
        threading.Thread.__init__(self)
        self.name = 'ExperimentTx_'
        self.daemon = True
        self.start()

        self.radio_driver           = None
        self.LoggerTx               = None
        self.gps                    = None
        self.gpio_handler           = None

        # start all the drivers
        self.radio_setup()
        self.logger_init()
        self.gpio_handler_init()
        self.gps_init()
        self.radio_init()

        # configure the logging module
        logging.basicConfig(stream=sys.__stdout__, level=logging.WARNING)

    def radio_setup(self):

        # initialize the radio driver
        self.radio_driver = radio.At86rf215(None)
        self.radio_driver.spi_init()

    def radio_init(self):
        self.radio_driver.radio_reset()
        self.radio_driver.read_isr_source()  # no functional role, just clear the pending interrupt flag

    def gps_init(self):
        logging.info('in of GPS init')
        # start the gps thread
        self.gps            = gps.GpsThread()
        # waiting until the GPS time is valid
        logging.info('waiting for valid GPS time...')
        while self.gps.is_gps_time_valid() is False:
            time.sleep(1)
        logging.info('... time valid')
        logging.info('out of GPS init')

    def logger_init(self):
        logging.info('in of logger init')
        # initializes the LoggerRx thread
        self.LoggerTx = LoggerTx(self.queue_tx, self.settings)
        logging.info('out of logger init')

    def gpio_handler_init(self):
        logging.info('in of gpio_handler_init')
        self.gpio_handler = gpio.GPIO_handler(self.radio_isr_pin, self.push_button_pin,
                                              self.radio_driver.cb_radio_isr,
                                              self._cb_push_button)

        self.gpio_handler.init_binary_pins(self.led_array_pins)
        self.gpio_handler.init_binary_pins(self.frame_sent_pin)
        logging.info('out of gpio_handler_init')

    def start_time_experiment(self):
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
        self.queue_tx.put('Print last')
        with self.dataLock:
            self.end_experiment.set()

    def experiment_scheduling(self):

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
                self.list_events_sched[self.settings['test_settings'].index(item)] = self.scheduler.enterabs(time.mktime(self.time_to_start.timetuple()) + offset, 1, self.execute_exp, (item,))
                self.schedule_time[self.settings['test_settings'].index(item)] = offset
                offset += item['durationtx_s'] + SECURITY_TIME
            self.cumulative_time = offset
            logging.info('time for each set of settings: {0}'.format(self.schedule_time))
            self.scheduler.enterabs(time.mktime(self.time_to_start.timetuple()) + offset, 1, self.stop_exp, ())
            self.scheduler.run()
            logging.info('END OF THE experiment_scheduling')

    def execute_exp(self, item):
        """"
        :param item

        """
        self.gpio_handler.led_off(self.frame_sent_pin)
        # clean the break execute_exp flag
        self.f_reset = False

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

        self.gpio_handler.binary_counter(item['index'], self.led_array_pins)
        logging.info('modulation: {0}'.format(item["modulation"]))
        # let know to the informative class the beginning of a new experiment
        self.queue_tx.put('Start')

        # log the config name
        self.queue_tx.put(item)

        # log GPS info
        self.queue_tx.put(self.gps.gps_info_read())

        # loop through packet lengths
        for frame_length, ifs in zip(self.settings["frame_lengths"], self.settings["IFS"]):

            # check if the reset button has been pressed
            # logging.warning('self.radio_driver.read_reset_cmd(): {0}'.format(self.radio_driver.read_reset_cmd()))
            if self.f_reset:
                break

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
                self.gpio_handler.led_toggle(self.frame_sent_pin)
                # logging.warning('self.radio_driver.read_reset_cmd(): {0}'.format(self.radio_driver.read_reset_cmd()))
                if self.f_reset:
                    break

    def remove_scheduled_experiment(self):
        events = self.scheduler.queue

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
                self.gpio_handler.led_on(self.frame_sent_pin)
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
        self.hours, self.minutes = self.start_time_experiment()
        self.time_to_start = dt.combine(dt.now(), datetime.time(self.hours, self.minutes))

        # it start the scheduler thread
        self.scheduler_aux = threading.Thread(target=self.experiment_scheduling)
        self.scheduler_aux.start()
        self.scheduler_aux.name = 'Scheduler Tx'
        logging.info('waiting the end of the experiment')

        # gives the signal to the scheduler to start scheduling the 31 experiments
        with self.dataLock:
            self.f_schedule.set()

        # it will switch on the LED frame_received_pin to let the user know the experiment will start the following
        # minute
        self.LED_start_exp()

        while True:

            # it waits for the self.end_experiment signal that can be triggered at the end of the 31st experiment
            # or when the push button is pressed
            self.end_experiment.wait()
            self.end_experiment.clear()

            # if push button, removes all the experiments scheduled
            if self.f_reset:
                self.gpio_handler.led_off(self.frame_sent_pin)
                logging.info('button pressed')
                logging.info('RESETTING SCHEDULE')
                self.remove_scheduled_experiment()
                logging.info('removed items in the queue')
                self.started_time = time.time()

                # determines the starting time for the new set of experiments
                self.hours, self.minutes = self.start_time_experiment()
                self.time_to_start = dt.combine(dt.now(), datetime.time(self.hours, self.minutes))
                logging.info('WITHIN THE WHILE TRUE MAIN --->> self.time_to_start: {0}'.format(self.time_to_start))
                logging.info('removed items in the queue')
                self.cumulative_time = 0
                self.first_run = False
                self.gpio_handler.binary_counter(0, self.led_array_pins)
                logging.info('before self.LED_start_exp()')
                self.LED_start_exp()
                logging.info('after self.LED_start_exp()')

            # gives the signal to the scheduler thread to re-schedule the experiments
            with self.dataLock:
                self.f_schedule.set()

    #  ======================== private =======================================
    
    def _cb_push_button(self, channel = 13):
        if not self.f_reset_button:
            with self.dataLock:
                self.start_experiment.set()
            self.f_reset_button         = True

        else:
            logging.warning('RESET BUTTON PRESSED')
            with self.dataLock:
                self.end_experiment.set()
                self.f_reset        = True
                logging.warning('self.f_reset_cmd set to true?: {0}'.format(self.f_reset))

#  ============================ main ==========================================


def load_experiment_details():
    with open('/home/pi/range_test/raspberry/experiment_settings.json', 'r') as f:
        settings = f.read().replace('\n', ' ').replace('\r', '')
        settings = json.loads(settings)
        return settings


def main():

    logging.basicConfig(stream=sys.__stdout__, level=logging.DEBUG)
    experimentTx = ExperimentTx(load_experiment_details())

    while True:
        input = raw_input('>')
        if input == 's':
            # print experimentTx.getStats()
            # print 'print stats TX'
            logging.warning('TO IMPLEMENT')
        if input == 'q':
            sys.exit(0)

if __name__ == '__main__':
    main()
