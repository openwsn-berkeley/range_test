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
from threading import Timer

import at86rf215_defs as defs
# import RPi.GPIO as GPIO
import at86rf215_driver as radio
import GpsThread as gps
import gpio_handler as gpio

PACKET_LENGTH       = 2047
CRC_SIZE            = 4
SECURITY_TIME       = 3    # 3 seconds to give more time to TRX to complete the 400 frame bursts.
START_OFFSET        = 3.5  # 3.5 seconds after the starting time arrives.
FCS_VALID           = 1
FRAME_MINIMUM_SIZE  = 7

IDLE_STATE = 0
RX_STATE = 1


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


# class GPIO_handler(object):
#
#     def __init__(self, radio_isr_pin = 11, push_button_pin = 13, cb_pin_11 = None, cb_pin_13 = None):
#
#         self.radio_isr_pin      = radio_isr_pin
#         self.push_button_pin    = push_button_pin
#         self.cb_pin_11          = cb_pin_11
#         self.cb_pin_13          = cb_pin_13
#         self.dataLock           = threading.RLock()
#         self.toggle_LED         = False
#         self.f_reset_pin        = False
#
#
#         GPIO.setmode(GPIO.BOARD)
#         GPIO.setup(radio_isr_pin, GPIO.IN)
#         GPIO.setup(push_button_pin, GPIO.IN)
#         GPIO.add_event_detect(radio_isr_pin, GPIO.RISING, callback=self.cb_pin_11)
#         GPIO.add_event_detect(push_button_pin, GPIO.RISING, callback=self.cb_pin_13, bouncetime=150)
#
#     def init_binary_pins(self, array):
#         """
#         It initialises the set of pins for the binary counter
#         :param array: set of pins where a LED + resistor are connected.
#         :return: nothing
#         """
#         for pin in array:
#             GPIO.setup(pin, GPIO.OUT)
#             self.led_off(pin)
#
#     def binary_counter(self, number, array):
#         """
#         it switches on the LEDs according to the number, binary system.
#         :param number: The number to be shown in binary
#         :param array: amount of LEDs available
#         :return: light :)
#         """
#         for index in range(0, len(array)):
#             GPIO.output(array[index], GPIO.LOW)
#
#         # LED_val = [0 for i in range(0, len(array))]
#         for index in range(0, len(array)):
#             LED = number >> index
#             if LED & 1:
#                 GPIO.output(array[index], GPIO.HIGH)
#
#     def led_on(self, pin):
#         GPIO.output(pin, GPIO.HIGH)
#
#     def led_off(self, pin):
#         GPIO.output(pin, GPIO.LOW)
#
#     def led_toggle(self, pin):
#         if self.toggle_LED is False:
#             self.toggle_LED = True
#             GPIO.output(pin, GPIO.HIGH)
#         else:
#             self.toggle_LED = False
#             GPIO.output(pin, GPIO.LOW)
#
#     def read_reset_pin(self):
#         with self.dataLock:
#             return self.f_reset_pin
#
#     def clean_reset_pin(self):
#         with self.dataLock:
#             self.f_reset_pin = False


class ExperimentRx(object):

    def __init__(self, settings):
        # local variables
        self.settings               = settings
        
        self.hours                  = 0
        self.minutes                = 0
        self.queue_rx               = Queue.Queue()
        self.started_time           = None
        self.cumulative_time        = START_OFFSET
        self.radio_isr_pin          = 11
        self.push_button_pin        = 13
        self.led_array_pins         = [29, 31, 33, 35, 37]
        self.frame_received_pin     = [36]
        self.time_to_start          = None
        self.f_start_signal_LED     = False
        self.f_reset_button         = False
        self.f_reset_pin            = False
        self.experiment_counter     = 0
        self.state                  = IDLE_STATE
        self.experiment_scheduled   = None

        self.dataLock               = threading.RLock()

        self.radio_driver           = None
        self.gps                    = None
        self.LoggerRx               = None
        self.gpio_handler           = None

    def experiment_init(self):
        
        self.radio_setup()
        self.logger_init()
        self.gpio_handler_init()
        self.gps_init()
        self.radio_init()

    def radio_setup(self):
        """
        it initialises the radio driver, it loads the callback for the RX
        :return:
        """
        # initialize the radio driver
        logging.info('FIRST STUFF')
        self.radio_driver   = radio.At86rf215(self._cb_rx_frame)
        self.radio_driver.spi_init()

        # logging.info('out of radio_setup')

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
        self.LoggerRx       = LoggerRx(self.queue_rx, self.settings)
        logging.info('out of logger init')

    def gpio_handler_init(self):
        logging.info('in of gpio_handler_init')
        self.gpio_handler   = gpio.GPIO_handler(self.radio_isr_pin, self.push_button_pin, self.radio_driver.cb_radio_isr,
                                           self.cb_push_button)
        
        self.gpio_handler.init_binary_pins(self.led_array_pins)
        self.gpio_handler.init_binary_pins(self.frame_received_pin)
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
        self.queue_rx.put('Print last')

    def _execute_exp(self, item):
        """
        This is the functions that reconfigures the radio at each test. It gets passed to the scheduler function.
        :return: Nothing
        """
        # clean the break execute_exp flag
        self.radio_driver.clean_reset_pin()

        # reset the radio to erase previous configuration
        self.radio_driver.radio_reset()
        self.radio_driver.LED_OFF(self.frame_received_pin)

        self.radio_driver.radio_write_config(defs.modulations_settings[item['modulation']])
        self.radio_driver.radio_set_frequency((item['channel_spacing_kHz'],
                                               item['frequency_0_kHz'],
                                               item['channel']))

        self.gpio_handler.binary_counter(item['index'], self.led_array_pins)
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

    def radio_configure_RX(self):
        self.radio_driver.radio_reset()
        self.gpio_handler.led_off(self.frame_received_pin)

        self.radio_driver.radio_write_config(defs.modulations_settings[self.settings['test_settings'][self.experiment_counter]['modulation']])
        self.radio_driver.radio_set_frequency((self.settings['test_settings'][self.experiment_counter]['channel_spacing_kHz'],
                                               self.settings['test_settings'][self.experiment_counter]['frequency_0_kHz'],
                                               self.settings['test_settings'][self.experiment_counter]['channel']))

        self.gpio_handler.binary_counter(self.settings['test_settings'][self.experiment_counter]['index'], self.led_array_pins)
        logging.info('modulation: {0}'.format(self.settings['test_settings'][self.experiment_counter]["modulation"]))

        # sends the signal to the logger class through queue, letting it know a new experiment just started.
        self.queue_rx.put('Start')

        # sends the config to the logger class through queue
        self.queue_rx.put(self.settings['test_settings'][self.experiment_counter])

        # sends the  GPS info to the logger class through queue
        self.queue_rx.put(self.gps.gps_info_read())

        # put the radio into RX mode
        self.radio_driver.radio_trx_enable()
        self.radio_driver.radio_rx_now()
        self.queue_rx.put(time.time() - self.started_time)


    #  ======================== public ========================================

    def getStats(self):
        # logging.warning('Results ongoing {0}'.format(self.LoggerRx.results))
        logging.warning('TO IMPLEMENT')

    #  ====================== private =========================================

    def cb_push_button(self, channel = 13):

        self.started_time = time.time()
        self.hours, self.minutes = self.start_time_experiment()
        self.time_to_start = dt.combine(dt.now(), datetime.time(self.hours, self.minutes))
        if self.experiment_scheduled:
            self.experiment_scheduled.cancel()
            self.experiment_counter = 0
        self.experiment_scheduled = Timer(
            time.mktime(self.time_to_start.timetuple()) + START_OFFSET  - time.time(),
            self._experiment_scheduling, ())
        self.experiment_scheduled.start()
        logging.info('time for the experiment to start: {0}'.format(time.mktime(self.time_to_start.timetuple())
                                                                    + START_OFFSET  - time.time()))
        logging.info('self.state = RX_STATE')


    def _cb_rx_frame(self, frame_rcv, rssi, crc, mcs):
        self.gpio_handler.led_toggle(self.frame_received_pin)
        # self.count_frames_rx += 1
        self.queue_rx.put((frame_rcv, rssi, crc, mcs))

        # re-arm the radio in RX mode
        self.radio_driver.radio_rx_now()

    def _experiment_scheduling(self):

        if self.experiment_counter < 31:
            self.radio_configure_RX()
            self.cumulative_time = self.settings['test_settings'][self.experiment_counter][
                                        'durationtx_s'] + SECURITY_TIME

            self.experiment_scheduled = Timer(self.cumulative_time, self._experiment_scheduling, ())
            self.experiment_scheduled.start()
            self.experiment_counter += 1
        else:
            self.stop_exp()
            self.radio_driver.radio_off()

# ========================== main ============================================

def load_experiment_details():
    with open('/home/pi/range_test/raspberry/experiment_settings.json', 'r') as f:
        settings = f.read().replace('\n', ' ').replace('\r', '')
        settings = json.loads(settings)
        return settings

def main():

    logging.basicConfig(stream=sys.__stdout__, level=logging.DEBUG)
    experimentRx = ExperimentRx(load_experiment_details())
    experimentRx.experiment_init()
    while True:
        # for item in
        input = raw_input('>')
        if input == 's':
            print experimentRx.getStats()
        elif input == 'q':
            sys.exit(0)

if __name__ == '__main__':
    main()
