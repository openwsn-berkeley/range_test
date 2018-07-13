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
import at86rf215_driver as radio
import GpsThread as gps
import gpio_handler as gpio

FRAME_LENGTH    = 2047
CRC_SIZE_LEGACY = 2
CRC_SIZE_154G   = 2
SECURITY_TIME   = 3  # 3 seconds to give more time to TRX to complete the 400 frame bursts.
START_OFFSET    = 4  # 4.5 seconds after the starting time arrives.
MODEM_SUB_GHZ   = 0
MODEM_2GHZ      = 1
COUNTER_LENGTH  = 2


class LoggerTx(threading.Thread):

    def __init__(self, queue, settings):

        # store parameters
        self.queue = queue
        self.settings = settings

        # local variables
        self.name_file = '/home/pi/range_test_outdoors/experiments_results_' + socket.gethostname() +\
                         '.json'
        self.results = {'type': 'end_of_cycle_tx', 'start_time_str': time.strftime("%a, %d %b %Y %H:%M:%S UTC",
                                                                                   time.gmtime()),
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
                else:
                    self.results['GPSinfo_at_start'] = item
            elif type(item) is float:
                logging.info('Time {0}'.format(item))
            else:
                logging.error('UNKNOWN ITEM IN THE QUEUE: {0}.'.format(item))


class ExperimentTx(threading.Thread):

    def __init__(self, settings):
        
        # local variables

        self.settings                   = settings
        self.queue_tx                   = Queue.Queue()

        self.f_start_signal_LED         = False
        self.f_reset_button             = False

        self.f_exit                     = False
        self.f_cancel_exp               = False

        self.hours                      = 0
        self.minutes                    = 0

        self.scheduler                  = sched.scheduler(time.time, time.sleep)
        self.list_events_sched          = [None for i in range(len(self.settings["test_settings"]))]
        self.schedule_time              = ['time' for i in range(len(self.settings["test_settings"]))]
        self.led_array_pins             = [29, 31, 33, 35, 37]
        self.TRX_frame_pin              = [36]
        self.radio_isr_pin              = 11
        self.push_button_pin            = 13
        self.scheduler_aux              = None
        self.time_to_start              = None
        self.started_time               = None
        self.led_start_indicator        = None
        self.experiment_scheduled       = None
        self.experiment_tx_thread       = None
        self.experiment_counter         = 0
        self.modem_base_band_state      = MODEM_SUB_GHZ

        self.dataLock                   = threading.RLock()

        # start the threads
        self.f_reset                    = threading.Event()
        self.start_experiment           = threading.Event()
        self.end_experiment             = threading.Event()
        self.f_schedule                 = threading.Event()
        self.f_reset.clear()
        self.start_experiment.clear()
        self.end_experiment.clear()
        self.f_schedule.clear()

        self.radio_driver               = None
        self.LoggerTx                   = None
        self.gps                        = None
        self.gpio_handler               = None

        # start all the drivers
        # gps should be enabled
        # self._gps_init()
        # logging.debug('radio setup')
        self._radio_setup()
        # logging.info('logger init')
        self._logger_init()
        # logging.info('gpio handler init')
        self._gpio_handler_init()
        # logging.info('radio init')
        self._radio_init()
        logging.debug('INIT COMPLETE')

        # start the thread
        threading.Thread.__init__(self)
        self.name = 'ExperimentTx_'
        self.daemon = True
        self.start()

        # configure the logging module
        # logging.basicConfig(stream=sys.__stdout__, level=logging.WARNING)

    #  ====================== private =========================================

    def _radio_setup(self):

        # initialize the radio driver
        self.radio_driver = radio.At86rf215(None, None)
        self.radio_driver.spi_init()

    def _radio_init(self):
        self.radio_driver.radio_reset()
        self.radio_driver.read_isr_source()  # no functional role, just clear the pending interrupt flag

    def _gps_init(self):
        logging.debug('in of GPS init')
        # start the gps thread
        self.gps            = gps.GpsThread()
        # waiting until the GPS time is valid
        logging.info('waiting for valid GPS time...')
        while self.gps.is_gps_time_valid() is False:
            time.sleep(1)
        logging.info('... time valid')
        logging.debug('out of GPS init')

    def _logger_init(self):
        # initializes the LoggerRx thread
        self.LoggerTx = LoggerTx(self.queue_tx, self.settings)

    def _gpio_handler_init(self):

        self.gpio_handler = gpio.GPIO_handler(self.radio_isr_pin, self.push_button_pin,
                                              self.radio_driver.cb_radio_isr,
                                              self._cb_push_button)

        self.gpio_handler.init_binary_pins(self.led_array_pins)
        self.gpio_handler.init_binary_pins(self.TRX_frame_pin)
        self.gpio_handler.led_off(self.TRX_frame_pin)
        self.gpio_handler.binary_counter(0, self.led_array_pins)

    def _start_time_experiment(self):
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

    def _stop_exp(self):
        """
        it makes print the last modulation results
        """
        self.queue_tx.put('Print last')
        with self.dataLock:
            self.end_experiment.set()
        logging.info('before the led_end_experiment_signal, time: {0}, thread: {1}'.format(time.time(),
                                                                                           threading.current_thread()))
        self._led_end_experiment_signal()
        logging.debug('END OF EXPERIMENTS')

    def _modem_2ghz(self):
        self.modem_base_band_state = MODEM_2GHZ

    def _execute_experiment_tx(self, item):
        """"
        :param item

        """
        logging.info('current thread in EXPERIMENT_TX: {0}'.format(threading.current_thread()))
        logging.info('thread enumerate: {0}'.format(threading.enumerate()))
        logging.info('start time TX 100 : {0}'.format(time.time()))
        total_time = time.time()
        # logging.debug('entering _execute_experiment_tx, time: {0}, {1}'.format(time.time(), item['modulation']))
        self.gpio_handler.led_off(self.TRX_frame_pin)
        # clean the break _execute_experiment_tx flag
        self.f_cancel_exp = False

        self.queue_tx.put(time.time() - self.started_time)
        self.gpio_handler.binary_counter(0, self.led_array_pins)
        # initialize the frame counter
        frame_counter = 0

        # reset the radio to erase previous configuration
        self.radio_driver.radio_reset()

        # re-configure the radio
        self.radio_driver.radio_write_config(defs.modulations_settings[item['modulation']])

        # select the frequency
        # if self.modem_base_band_state == MODEM_SUB_GHZ:
        logging.debug('ITEM: {0}'.format(item))
        if item['modem'] == "subGHz":
            self.radio_driver.radio_off()
            self.radio_driver.radio_set_frequency((item['channel_spacing_kHz'],
                                                   item['frequency_0_kHz'],
                                                   item['channel']))
        elif item['modem'] == "2.4GHz":
            self.radio_driver.radio_off_2_4ghz()
            self.radio_driver.radio_set_frequency_2_4ghz((item['channel_spacing_kHz'],
                                                          item['frequency_0_kHz'],
                                                          item['channel']))
        else:
            logging.CRITICAL('ERROR')

        self.gpio_handler.binary_counter(item['index'], self.led_array_pins)
        logging.info('modulation: {0}, channel: {1}'.format(item["modulation"], item["channel"]))
        # let know to the informative class the beginning of a new experiment
        self.queue_tx.put('Start')

        # log the config name
        self.queue_tx.put(item)

        # log GPS info
        # self.queue_tx.put(self.gps.gps_info_read())

        # if self.modem_base_band_state == MODEM_SUB_GHZ:
        if item['standard'] == '802.15.4g':
            # loop through packet lengths
            for frame_length in self.settings["frame_lengths_15.4g"]:

                # check if the reset button has been pressed
                # logging.warning('self.radio_driver.read_reset_cmd(): {0}'.format(self.radio_driver.read_reset_cmd()))
                with self.dataLock:
                    if self.f_cancel_exp:
                        logging.warning('BREAKING EXP')
                        break

                if item['modem'] == 'subGHz':
                    self.radio_driver.radio_trx_enable()
                else:
                    self.radio_driver.radio_trx_enable_2_4ghz()
                # send burst of frames
                for i in range(self.settings['numframes']):

                    # create frame
                    frameToSend = [frame_counter >> 8, frame_counter & 0xFF] + [i & 0xFF for i in range(FRAME_LENGTH -
                                                                                                        COUNTER_LENGTH)]
                    # increment the frame counter
                    frame_counter += 1

                    # send frame
                    if item['modem'] == 'subGHz':
                        self.radio_driver.radio_load_packet(frameToSend[:frame_length - CRC_SIZE_154G], CRC_SIZE_154G)
                        self.radio_driver.radio_tx_now()

                    else:
                        self.radio_driver.radio_load_packet_2_4ghz(frameToSend[:frame_length - CRC_SIZE_154G],
                                                                   CRC_SIZE_154G)
                        self.radio_driver.radio_tx_now_2_4ghz()

                    # IFS
                    time.sleep(self.settings['IFS'])
                    self.gpio_handler.led_toggle(self.TRX_frame_pin)
                    # logging.warning('self.radio_driver.read_reset_cmd(): {0}'.format(self.radio_driver.read_reset_cmd()))
                    with self.dataLock:
                        if self.f_cancel_exp:
                            logging.warning('BREAKING EXP')
                            break
            # logging.info('EXIT FROM THE _execute_experiment_tx: {0}, {1}'.format(time.time(), item['modulation']))
            # logging.info('DURATION OF {0} is: {1}'.format(item["modulation"], (time.time() - total_time)))

        # standard is IEEE802.15.4-2006
        else:
            # loop through packet lengths
            for frame_length in self.settings["frame_lengths_15.4-2006"]:

                # check if the reset button has been pressed
                # logging.warning('self.radio_driver.read_reset_cmd(): {0}'.format(self.radio_driver.read_reset_cmd()))
                with self.dataLock:
                    if self.f_cancel_exp:
                        logging.warning('BREAKING EXP')
                        break

                self.radio_driver.radio_trx_enable_2_4ghz()
                # send burst of frames
                for i in range(self.settings['numframes']):

                    # create frame
                    frameToSend = [frame_counter >> 8, frame_counter & 0xFF] + [i & 0xFF for i in
                                                                                range(FRAME_LENGTH - COUNTER_LENGTH)]
                    # increment the frame counter
                    frame_counter += 1

                    # send frame
                    self.radio_driver.radio_load_packet_2_4ghz(frameToSend[:frame_length - CRC_SIZE_LEGACY],
                                                               CRC_SIZE_LEGACY)
                    self.radio_driver.radio_tx_now_2_4ghz()

                    # IFS
                    time.sleep(self.settings["IFS"])
                    self.gpio_handler.led_toggle(self.TRX_frame_pin)
                    # logging.warning('self.radio_driver.read_reset_cmd(): {0}'.format(self.radio_driver.read_reset_cmd()))
                    with self.dataLock:
                        if self.f_cancel_exp:
                            logging.warning('BREAKING EXP')
                            break
        # logging.info('EXIT FROM THE _execute_experiment_tx: {0}, {1}'.format(time.time(), item['modulation']))
        logging.info('DURATION OF {0} is: {1}'.format(item["modulation"], (time.time() - total_time)))
        self.radio_driver.radio_off_2_4ghz()
        self.radio_driver.radio_off()

    def _remove_scheduled_experiment(self):
        events = self.scheduler.queue
        for ev in events:
            self.scheduler.cancel(ev)

    def _led_end_experiment_signal(self):
        i = 0
        for led in self.led_array_pins:
            self.gpio_handler.led_off(led)

        while i < 20 and not self.f_reset.is_set():

            for led in self.led_array_pins:
                self.gpio_handler.led_toggle(led)
            time.sleep(1)
            i += 1

    def _led_start_experiment_signal(self):
        """
        it lights on a LED if the experiment will take place in the next minute
        it uses the frame receive LED to indicate whether the experiment is going to start the next minute or not.
        :return:
        """
        logging.debug('entering led_start_experiment_signal')
        while not self.f_start_signal_LED:
            now = time.gmtime()
            if self.minutes - now[4] == 1 or self.minutes - now[4] == -59:
                logging.debug('SWITCHING LIGHT UP led_start_experiment_signal')
                self.gpio_handler.led_on(self.TRX_frame_pin)
                self.f_start_signal_LED = True
                continue
            time.sleep(1)
        self.f_start_signal_LED = False
        logging.debug('OUTING led_start_experiment_signal')
    
    def run(self):
        # setup the radio
        # self._radio_setup()
        logging.info('current thread: {0}'.format(threading.current_thread()))
        logging.info('WAITING FOR THE START BUTTON TO BE PRESSED')
        logging.info('thread enumerate: {0}'.format(threading.enumerate()))

        # push button signal
        self.start_experiment.wait()
        self.start_experiment.clear()

        while True:
            # gets current time and determines the running time for the experiment to start
            self.started_time = time.time()
            self.hours, self.minutes = self._start_time_experiment()
            self.time_to_start = dt.combine(dt.now(), datetime.time(self.hours, self.minutes))

            self.radio_driver.radio_off()
            self.gpio_handler.led_off(self.TRX_frame_pin)
            self.gpio_handler.binary_counter(0, self.led_array_pins)
            self.experiment_counter = 0
            self.experiment_scheduled = Timer(
                time.mktime(self.time_to_start.timetuple()) + START_OFFSET - time.time(),
                self._experiment_scheduling, ())
            self.experiment_scheduled.start()
            logging.info('time left for the experiment to start: {0}'.format(time.mktime(self.time_to_start.timetuple())
                                                                    + START_OFFSET - time.time()))
            logging.info('time to start experiment: {0}'.format(self.time_to_start))
            self.led_start_indicator = threading.Thread(target=self._led_start_experiment_signal)
            self.led_start_indicator.start()
            self.led_start_indicator.name = 'TX start led signal'  
            logging.info('Experiment loaded')  
            logging.info('current thread: {0}'.format(threading.current_thread()))        
            logging.info('thread enumerate: {0}'.format(threading.enumerate()))
            self.f_reset.wait()
            self.f_reset.clear()    
            logging.info('reset button pressed')


    #  ======================== callbacks =======================================
    
    def _cb_push_button(self, channel=13):
        logging.info('PUSH BUTTON PRESSED')
        # pass
        self.gpio_handler.clear_cb(13)
        time.sleep(1)
        # switch on all leds to let the user know the push button has been pressed and it got the signal.
        self.gpio_handler.binary_counter(31, self.led_array_pins)
        if not self.f_reset_button:
            with self.dataLock:
                self.start_experiment.set()
            self.f_reset_button         = True
            logging.info('START BUTTON PRESSED')
            self.gpio_handler.add_cb(self._cb_push_button, self.push_button_pin)
        
        else:
            
            with self.dataLock:
                # self.end_experiment.set()
                # self.f_schedule.set()
                logging.info('RESET BUTTON PRESSED')
                self.f_reset.set()
                self.f_cancel_exp  = True
                logging.warning('CLEANING GPIO')
                self.gpio_handler.clean_gpio()
                logging.warning('CLEANED GPIO')
                logging.info('PROGRAM FINISHING in the ISR PUSH BUTTON...')
                sys.exit(0)
                # self.experiment_scheduled.cancel()
            logging.info('f_reset set to true?: {0}'.format(self.f_reset.isSet()))
            # self.gpio_handler.clean_gpio()
            # sys.exit(0)
       

    def _experiment_scheduling(self):

        logging.info('current thread in the scheduling: {0}'.format(threading.current_thread()))
        self.time_next_experiment = self.settings['test_settings'][self.experiment_counter % len(
            self.settings['test_settings'])]['durationtx_s'] + SECURITY_TIME
        logging.info('time of next experiment: {0}, setting: {1}'.format(self.time_next_experiment,  self.settings[
            'test_settings'][self.experiment_counter % len(self.settings['test_settings'])]['modulation']))
        self.experiment_scheduled = Timer(self.time_next_experiment, self._experiment_scheduling, ())
        self.experiment_scheduled.start()
        self.experiment_tx_thread = threading.Thread(target=self._execute_experiment_tx, args=[self.settings[
            'test_settings'][self.experiment_counter % len(self.settings['test_settings'])]])
        self.experiment_tx_thread.start()
        self.experiment_tx_thread.name = 'schedule TX _100 packets'
        self.experiment_counter += 1

#  ============================ main ==========================================


def load_experiment_details():
    with open('/home/pi/range_test/raspberry/experiment_settings_outdoors_range_test.json', 'r') as f:
        settings = f.read().replace('\n', ' ').replace('\r', '')
        settings = json.loads(settings)
        return settings


def main():
    f_start = False
    logging.basicConfig(stream=sys.__stdout__, level=logging.DEBUG)
    logging.info('PROGRAM STARTING...')
    experimentTx = ExperimentTx(load_experiment_details())

    experimentTx.f_reset.wait()
    logging.info('PROGRAM FINISHING...')
    experimentTx.f_reset.clear()
    logging.warning('CLEANING GPIO')
    experimentTx.gpio_handler.clean_gpio()
    logging.warning('CLEANED GPIO')
    logging.info('PROGRAM FINISHING... BYE BYE')
    time.sleep(2)
    sys.exit(0)
    logging.warning('.........................THIS LINE SHOULD NEVER BE READ.......')

    # while True:
    #     input = raw_input('>')
    #     if input == 's':
    #         if not f_start:
    #             f_start = True
    #             logging.info('PROGRAM STARTING...')
    #             # experimentTx = ExperimentTx(load_experiment_details())
    #             logging.info('PROGRAM RUNNING')
    #         else:
    #             logging.info('PROGRAM ALREADY STARTED')
    #     if input == 'q':
    #         if f_start:
    #             experimentTx.gpio_handler.clean_gpio()
    #         sys.exit(0)

if __name__ == '__main__':
    main()
