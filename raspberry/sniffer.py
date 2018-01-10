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
SECURITY_TIME       = 5  # 5 seconds to give more time to TRX to complete the 400 frame bursts.
START_OFFSET        = 1  # 1 second after the starting time arrives.
FCS_VALID           = 1
FRAME_MINIMUM_SIZE  = 7
MODEM_SUB_GHZ       = 0
MODEM_2GHZ          = 1

# ============================== public =======================================


class ExperimentRx(object):

    def __init__(self, settings):
        # local variables
        self.settings               = settings
        self.radio_isr_pin          = 11
        self.push_button_pin        = 13
        self.led_array_pins         = [29, 31, 33, 35, 37]
        self.TRX_frame_pin          = [36]
        self.f_push_button          = False
        self.modem_base_band_state  = MODEM_SUB_GHZ
        self.experiment_rx_printing = None
        self.queue_rx               = Queue.Queue()
        # FIXME change this name variable

        self.dataLock               = threading.RLock()

        self.radio_driver           = None
        self.gpio_handler           = None

        # start all the drivers
        self._radio_setup()
        self._gpio_handler_init()
        self._radio_init()
        self.start_exp()

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

    def _gpio_handler_init(self):
        logging.info('gpio init!')
        self.gpio_handler   = gpio.GPIO_handler(self.radio_isr_pin, self.push_button_pin, self.radio_driver.cb_radio_isr,
                                           self._cb_push_button)
        
        self.gpio_handler.init_binary_pins(self.led_array_pins)
        self.gpio_handler.init_binary_pins(self.TRX_frame_pin)
        for led in self.led_array_pins:
            self.gpio_handler.led_off(led)
        self.gpio_handler.led_off(self.TRX_frame_pin)

    def _execute_experiment_rx(self, item):
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

    def start_exp(self):
        self.gpio_handler.binary_counter(31, self.led_array_pins)
        logging.info('lights must be on')
        self._execute_experiment_rx()

    def printing_rx_frames(self):
        while True:
            item = self.queue_rx.get()


    # ========================= callbacks =====================================

    def _cb_push_button(self, channel = 13):
        pass

    def _cb_rx_frame(self, frame_rcv, rssi, crc, mcs):
        self.gpio_handler.led_toggle(self.TRX_frame_pin)
        # self.count_frames_rx += 1
        self.queue_rx.put((frame_rcv, rssi, crc, mcs))
        # show frame
        # logging.debug('frame received: {0},\
        #                RSSI: {1},         CRC: {2},          MCS: {3}'.format(
        #                 frame_rcv, rssi, crc, mcs))

        # re-arm the radio in RX modes
        if self.modem_base_band_state == MODEM_2GHZ:
            self.radio_driver.radio_rx_now_2_4ghz()
        else:
            self.radio_driver.radio_rx_now()

#  ============================ public ========================================

    def getStats(self):
        # logging.warning('Results ongoing {0}'.format(self.LoggerRx.results))
        logging.warning('TO IMPLEMENT')

# ========================== main =============================================


def load_experiment_details():
    with open('/home/pi/range_test/raspberry/experiment_settings.json', 'r') as f:
        settings = f.read().replace('\n', ' ').replace('\r', '')
        settings = json.loads(settings)
        return settings


def main():
    f_start = False

    logging.basicConfig(stream=sys.__stdout__, level=logging.DEBUG)
    # experimentRx = ExperimentRx(settings)

    while True:
        # for item in
        input = raw_input('>')
        if input == 's':
            if not f_start:
                f_start = True
                logging.info('PROGRAM STARTING...')
                experimentRx = ExperimentRx(load_experiment_details())
                logging.info('PROGRAM RUNNING')
            else:
                logging.info('PROGRAM ALREADY STARTED')
        elif input == 'q':
            if f_start:
                experimentRx.gpio_handler.clean_gpio()
            sys.exit(0)

if __name__ == '__main__':
    main()
