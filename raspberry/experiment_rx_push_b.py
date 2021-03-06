"""
Reception script of the range test.

\ author Jonathan Munoz (jonathan.munoz@inria.fr), January 2017
"""

import time
import sys
import logging
import threading
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

PACKET_LENGTH       = 2047
CRC_SIZE            = 4
SECURITY_TIME       = 3  # 5 seconds to give more time to TRX to complete the 400 frame bursts.
START_OFFSET        = 1  # 1 second after the starting time arrives.
FCS_VALID           = 1
FRAME_MINIMUM_SIZE  = 123
MODEM_SUB_GHZ       = 0
MODEM_2GHZ          = 1
FRAME_COUNT         = 1000


class LoggerRx(threading.Thread):
    def __init__(self, queue, settings):

        # store parameters
        self.queue              = queue
        self.settings           = settings

        # local variables
        self.rx_string      = ['!' for i in range(len(self.settings['frame_lengths_15.4g'])*self.settings[
                'numframes'])]
        self.rssi_values    = [None for i in range(len(self.settings['frame_lengths_15.4g'])*self.settings[
                'numframes'])]
        self.name_file          = '/home/pi/range_test_outdoors/experiments_results_' + \
                                  socket.gethostname() + '.json'
        self.results            = {'type': 'end_of_cycle_rx', 'start_time_str': time.strftime(
            "%a, %d %b %Y %H:%M:%S UTC", time.gmtime()), 'start_time_epoch': time.time(), 'version': self.settings[
            'version'], 'position_description': None, 'radio_settings': None, 'rx_frames_count': 0, 'RSSI_by_length':
            None, 'rx_string': None, 'GPSinfo_at_start': None, 'channel': None, 'frequency_0': None, 'burst_size':
            self.settings['numframes'], 'id': socket.gethostname(), 'rx_frames_wrong_fcs_count': 0,
            'rx_frames_wrong_fcs_sequence_number': []}

        # start the thread
        threading.Thread.__init__(self)
        self.name               = 'LoggerRx'
        self.daemon             = True
        self.start()

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
                    self._print_results()  # print to log file
                    pass
                self.rx_string = ['!' for i in range(len(self.settings['frame_lengths_15.4g']) * self.settings['numframes'])]
                self.rssi_values = [None for i in
                                    range(len(self.settings['frame_lengths_15.4g']) * self.settings['numframes'])]
                self.results['rx_frames_count'] = 0
                self.results['start_time_str'] = time.strftime("%a, %d %b %Y %H:%M:%S UTC", time.gmtime())
                self.results['start_time_epoch'] = time.time()
                self.results['rx_frames_wrong_fcs_count'] = 0
                self.results['rx_frames_wrong_fcs_sequence_number'] = []
                self.results['rx_frames_wrong'] = []

            elif type(item) is tuple:
                # verify size of the tuple
                if len(item) == 4:
                    if item[2] is FCS_VALID:  # check frame correctness.
                        if len(item[0]) > FRAME_MINIMUM_SIZE:
                            try:
                                if item[0][0] * 256 + item[0][1] < FRAME_COUNT and (item[0][2], item[0][3]) == (0x00,
                                                                                                                0x01):
                                    self.rx_string[item[0][0] * 256 + item[0][1]] = '.'
                                    self.rssi_values[item[0][0] * 256 + item[0][1]] = float(item[1])
                                    self.results['rx_frames_count'] += 1
                                else:
                                    # logging.warning('UNKNOWN ITEM (frame_rcv, rssi, crc, mcs): {0}'.format(item))
                                    logging.warning('.....')

                            except IndexError as err:
                                logging.warning('item: {0}'.format(item))
                                logging.warning('frame not sent within the experiment, unknown sender')
                                logging.warning(err)
                    else:
                        try:
                            self.results['rx_frames_wrong_fcs_sequence_number'].append(item[0][0] * 256 + item[0][1])
                            # uncomment if you want to save the wrong frames. Takes a lot of CPU power.
                            # self.results['rx_frames_wrong'].append(item[0])

                        except IndexError as err:
                            logging.warning('UNKNOWN: {0}'.format(item))
                            logging.warning(err)
                        self.results['rx_frames_wrong_fcs_count'] += 1  # Frame received but wrong.

                else:
                    logging.error('UNKNOWN OBJECT IN THE QUEUE: {0}'.format(item))

            elif item == 'Print last':
                # self._print_results()
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

#  ====================== private =========================================

    def _print_results(self):
        """
        it will print the results of the previous experiment in the output file
        :return:
        """
        self._rx_frames_psize()
        with open(self.name_file, 'a') as f:
            f.write(json.dumps(self.results.copy())+'\n')

    def _rx_frames_psize(self):
        # TODO: fix this shit
        """
        It assigns the values to the result dictionary by separating the burst of 400 frames into 4 groups of 100 frames
        each, knowing the first 100 correspond to 8 bytes long, 100-199 frames number correspond to 127 bytes long,
        200-299 to 1000 bytes long and 300-399 to 2047 bytes long. Also assigns the RSSI average value during the
        experiment and the modulation used.
        :returns: Nothing
        """

        self.results['RSSI_by_length'] = {
                '127':  self.rssi_values[0:self.settings['numframes']],
                '2047': self.rssi_values[self.settings['numframes']:2*self.settings['numframes']]
            },
        self.results['rx_string'] = {
                '127':  ''.join(self.rx_string[0:self.settings['numframes']]),
                '2047': ''.join(self.rx_string[self.settings['numframes']:2*self.settings['numframes']])
        }

# ============================== public =======================================


# =============================================================================

class ExperimentRx(threading.Thread):

    def __init__(self, settings):
        # local variables
        self.settings               = settings
        
        self.f_reset_button         = False

        self.hours                  = 0
        self.minutes                = 0
        self.queue_rx               = Queue.Queue()
        self.started_time           = None
        self.time_next_experiment   = START_OFFSET
        self.radio_isr_pin          = 11
        self.push_button_pin        = 13
        self.led_array_pins         = [29, 31, 33, 35, 37]
        self.TRX_frame_pin          = [36]
        self.time_to_start          = None
        self.f_start_signal_LED     = False
        self.led_start_indicator    = None
        self.experiment_counter     = 0
        self.experiment_scheduled   = None
        self.experiment_rx_thread   = None
        self.f_push_button          = False
        self.modem_base_band_state  = MODEM_SUB_GHZ
        # FIXME change this name variable

        self.dataLock               = threading.RLock()

        self.f_reset               = threading.Event()
        self.start_experiment      = threading.Event()
        
        self.f_reset.clear()
        self.start_experiment.clear()
        
        self.radio_driver           = None
        self.gps                    = None
        self.LoggerRx               = None
        self.gpio_handler           = None

        # start all the drivers
        self._gps_init()
        # logging.info('radio setup')
        self._radio_setup()
        # logging.info('logger init')
        self._logger_init()
        # logging.info('gpio handler init')
        self._gpio_handler_init()
        # logging.info('radio init')
        self._radio_init()

        # start the thread
        threading.Thread.__init__(self)
        self.name = 'ExperimentRx_'
        self.daemon = True
        self.start()

#  ========================== private =========================================

    def _radio_setup(self):
        """
        it initialises the radio driver, it loads the callback for the RX
        :return:
        """
        # initialize the radio driver and the spi interface
        self.radio_driver   = radio.At86rf215(self._cb_rx_frame, self.modem_base_band_state)
        self.radio_driver.spi_init()

    def _radio_init(self):
        self.radio_driver.radio_reset()
        self.radio_driver.read_isr_source()  # no functional role, just clear the pending interrupt flag

    def _gps_init(self):
        # start the gps thread
        self.gps            = gps.GpsThread()

        # waiting until the GPS time is valid
        logging.info('waiting for valid GPS time...')
        while self.gps.is_gps_time_valid() is False:
            time.sleep(1)
        logging.info('... time valid')
        logging.info('out of GPS init')

    def _logger_init(self):
        # initializes the LoggerRx thread
        self.LoggerRx       = LoggerRx(self.queue_rx, self.settings)

    def _gpio_handler_init(self):
        self.gpio_handler   = gpio.GPIO_handler(self.radio_isr_pin, self.push_button_pin,
                                                self.radio_driver.cb_radio_isr, self._cb_push_button)
        self.gpio_handler.init_binary_pins(self.led_array_pins)
        self.gpio_handler.init_binary_pins(self.TRX_frame_pin)
        for led in self.led_array_pins:
            self.gpio_handler.led_off(led)
        self.gpio_handler.led_off(self.TRX_frame_pin)

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
        self.queue_rx.put('Print last')

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
                logging.info('SWITCHING LIGHT UP led_start_experiment_signal')
                self.gpio_handler.led_on(self.TRX_frame_pin)
                self.f_start_signal_LED = True
                continue
            time.sleep(1)
        self.f_start_signal_LED = False
        logging.debug('OUTING led_start_experiment_signal')

    def _led_end_experiment_signal(self):
        i = 0
        for led in self.led_array_pins:
            self.gpio_handler.led_off(led)
        while i < 20 and not self.f_push_button:
            for led in self.led_array_pins:
                self.gpio_handler.led_toggle(led)
            time.sleep(1)
            i += 1

    def _execute_experiment_rx(self, item):
        logging.info('start time RX 1000 : {0}'.format(time.time()))
        logging.debug('item to configure the radio: {0}'.format(item))
        self.radio_driver.radio_off_2_4ghz()
        self.radio_driver.radio_off()
        self.f_push_button = False
        logging.debug('entering execute_experiment_rx, time: {0}'.format(time.time()))
        self.radio_driver.radio_reset()
        self.gpio_handler.led_off(self.TRX_frame_pin)
        self.gpio_handler.binary_counter(0, self.led_array_pins)

        # the radio configuration is the same procedure, despite modem or frequency band
        self.radio_driver.radio_write_config(defs.modulations_settings[item['modulation']])
        if item['modem'] == 'subGHz':
            self.modem_base_band_state = MODEM_SUB_GHZ
            self.radio_driver.radio_set_frequency((item['channel_spacing_kHz'],
                                                       item['frequency_0_kHz'],
                                                       item['channel']))
            # put the radio into RX mode
            logging.info('LISTENING IN 863MHz')
            self.radio_driver.radio_trx_enable()
            logging.debug('putting radio to listen!')
            self.radio_driver.radio_rx_now()
            logging.debug('RADIO STATE: {0}'.format(self.radio_driver.check_radio_state_rf09()))
            logging.debug('radio listening!')
        else:
            # logging.debug('LEGACY set up')
            self.modem_base_band_state = MODEM_2GHZ
            self.radio_driver.radio_set_frequency_2_4ghz((item['channel_spacing_kHz'],
                                                              item['frequency_0_kHz'],
                                                              item['channel']))
            # put the radio into RX mode
            logging.info('LISTENING IN 2.4GHz')
            self.radio_driver.radio_trx_enable_2_4ghz()
            logging.debug('putting radio to listen!')
            self.radio_driver.radio_rx_now_2_4ghz()
            logging.debug('RADIO STATE: {0}'.format(self.radio_driver.check_radio_state_rf24()))
            logging.debug('radio listening!')

        self.gpio_handler.binary_counter(item['index'], self.led_array_pins)
        logging.info('modulation: {0}, channel: {1}'.format(item["modulation"], item["channel"]))
        # sends the signal to the logger class through queue, letting it know a new experiment just started.
        self.queue_rx.put('Start')
        # sends the config to the logger class through queue
        self.queue_rx.put(item)
        self.queue_rx.put(time.time())

    def run(self):
        # setup the radio
        # self._radio_setup()
        logging.info('current thread: {0}'.format(threading.current_thread()))
        logging.info('WAITING FOR THE START BUTTON TO BE PRESSED')

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
            logging.info('time to start experiment: {0}'.format(self.time_to_start.timetuple()))
            self.led_start_indicator = threading.Thread(target=self._led_start_experiment_signal)
            self.led_start_indicator.start()
            self.led_start_indicator.name = 'RX start led signal'
            logging.info('Experiment loaded')  
            logging.info('current thread: {0}'.format(threading.current_thread()))        
            logging.info('thread enumerate: {0}'.format(threading.enumerate()))
            self.f_reset.wait()
            self.f_reset.clear()    
            logging.info('reset button pressed')


    # ========================= callbacks =====================================

    def _cb_push_button(self, channel = 13):
        logging.info('PUSH BUTTON PRESSED')
        # pass
        self.gpio_handler.clear_cb(13)
        # switch on all leds to let the user know the push button has been pressed and it got the signal.
        self.gpio_handler.binary_counter(31, self.led_array_pins)
        if not self.f_reset_button:
            with self.dataLock:
                self.start_experiment.set()
            self.f_reset_button         = True
            logging.info('START BUTTON PRESSED')
        
        else:
            
            with self.dataLock:
                # self.end_experiment.set()
                # self.f_schedule.set()
                logging.warning('RESET BUTTON PRESSED')
                self.f_reset.set()
                # self.f_cancel_exp   = True
                # self.experiment_scheduled.cancel()

            logging.info('f_reset set to true?: {0}'.format(self.f_reset.isSet()))
            
            # sys.exit(0)
        time.sleep(5)
        self.gpio_handler.add_cb(self._cb_push_button, self.push_button_pin)


    def _cb_rx_frame(self, frame_rcv, rssi, crc, mcs):
        self.gpio_handler.led_toggle(self.TRX_frame_pin)
        # self.count_frames_rx += 1
        self.queue_rx.put((frame_rcv, rssi, crc, mcs))
        logging.debug('counter frame received: {0} , RSSI: {1}, MCS: {2}, length: {3}'
                      .format(frame_rcv[:2], rssi, mcs, len(frame_rcv)))

        # re-arm the radio in RX mode
        if self.modem_base_band_state == MODEM_2GHZ:
            self.radio_driver.radio_rx_now_2_4ghz()
        else:
            self.radio_driver.radio_rx_now()

    def _experiment_scheduling(self):

        logging.info('current thread in the scheduling: {0}'.format(threading.current_thread()))
        self.time_next_experiment = self.settings['test_settings'][self.experiment_counter % len(
            self.settings['test_settings'])]['durationtx_s'] + SECURITY_TIME
        logging.info('time of next experiment {0}, setting: {1}'.format(self.time_next_experiment,  self.settings[
            'test_settings'][self.experiment_counter % len(self.settings['test_settings'])]['modulation']))
        self.experiment_scheduled = Timer(self.time_next_experiment, self._experiment_scheduling, ())
        self.experiment_scheduled.start()
        self._execute_experiment_rx(self.settings['test_settings'][self.experiment_counter % len(
            self.settings['test_settings'])])
        self.experiment_counter += 1
#  ============================ public ========================================

    def getStats(self):
        # logging.warning('Results ongoing {0}'.format(self.LoggerRx.results))
        logging.warning('TO IMPLEMENT')

# ========================== main =============================================


def load_experiment_details():
    with open('/home/pi/range_test/raspberry/experiment_settings_outdoors_range_test.json', 'r') as f:
        settings = f.read().replace('\n', ' ').replace('\r', '')
        settings = json.loads(settings)
        return settings


def main():
    f_start = False
    logging.basicConfig(stream=sys.__stdout__, level=logging.INFO)
    logging.info('PROGRAM STARTING...')
    experimentRx = ExperimentRx(load_experiment_details())

    experimentRx.f_reset.wait()
    logging.info('PROGRAM FINISHING...')
    experimentRx.f_reset.clear()
    experimentRx.gpio_handler.clean_gpio()
    sys.exit(0)
    logging.warning('......THIS LINE SHOULD NEVER BE READ...')

    # while True:
    #     # for item in
    #     input = raw_input('>')
    #     if input == 's':
    #         if not f_start:
    #             f_start = True
    #             logging.info('PROGRAM STARTING...')
    #             # experimentRx = ExperimentRx(load_experiment_details())
    #             logging.info('PROGRAM RUNNING')
    #         else:
    #             logging.info('PROGRAM ALREADY STARTED')
    #     elif input == 'q': 
    #         if f_start:
    #             experimentRx.gpio_handler.clean_gpio()
            # sys.exit(0)

if __name__ == '__main__':
    main()
