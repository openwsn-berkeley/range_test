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
SECURITY_TIME       = 3    # 3 seconds to give more time to TRX to complete the 400 frame bursts.
START_OFFSET        = 3.5  # 3.5 seconds after the starting time arrives.
FCS_VALID           = 1
FRAME_MINIMUM_SIZE  = 7
MODEM_SUB_GHZ       = 0
MODEM_2GHZ          = 1


class LoggerRx(threading.Thread):
    def __init__(self, queue):

        # store parameters
        self.queue              = queue

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
            # logging.warning('(frame_rcv, rssi, crc, mcs): {0}, type: {1}'.format(item, type(item[0])))
            frame = [hex(x) for x in item[0]]
            logging.debug('frame length: {0}'.format(len(frame)))
            logging.debug('frame_rcv: {0}'.format(frame))
            logging.debug('rssi, crc, mcs: {0}'.format(item[1:]))
            logging.debug('-------------------------------------------------------------------------')

# ============================== public =======================================


# =============================================================================

class Sniffer(threading.Thread):

    def __init__(self, alias, freq_band, channel):
        # local variables
        # self.settings               = settings
        self.alias                  = alias
        self.freq_band              = freq_band
        self.channel                = channel
        self.queue_rx               = Queue.Queue()
        self.radio_isr_pin          = 11
        self.push_button_pin        = 13
        self.led_array_pins         = [29, 31, 33, 35, 37]
        self.TRX_frame_pin          = [36]
        # FIXME change this name variable
        self.band                   = None
        self.modem_base_band_state  = MODEM_SUB_GHZ
        self.f_push_button          = False

        self.dataLock               = threading.RLock()

        self.radio_driver           = None
        self.LoggerRx               = None
        self.gpio_handler           = None

        # start all the drivers
        self._radio_setup()
        self._logger_init()
        self._gpio_handler_init()
        self._radio_init()
        logging.info('threads alive at the start of the program: {0}'.format(threading.enumerate()))

        # start the thread
        threading.Thread.__init__(self)
        self.name = 'sniffer_'
        self.daemon = True
        self.start()

        # self._execute_experiment_rx()

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


    def _logger_init(self):
        # initializes the LoggerRx thread
        self.LoggerRx       = LoggerRx(self.queue_rx)

    def _gpio_handler_init(self):
        self.gpio_handler   = gpio.GPIO_handler(self.radio_isr_pin, self.push_button_pin, self.radio_driver.cb_radio_isr,
                                           self._cb_push_button)
        
        self.gpio_handler.init_binary_pins(self.led_array_pins)
        self.gpio_handler.init_binary_pins(self.TRX_frame_pin)
        for led in self.led_array_pins:
            self.gpio_handler.led_off(led)
        self.gpio_handler.led_off(self.TRX_frame_pin)

    def run(self):
         # def set_frequency(channel_spacing, frequency_0, channel):
        self.radio_driver.radio_off_2_4ghz()
        self.radio_driver.radio_off()
        self.radio_driver.radio_reset()
        # the radio configuration is the same procedure, despite modem or frequency band
        self.radio_driver.radio_write_config(defs.modulations_settings[self.alias])
        if self.freq_band == 0:
            self.modem_base_band_state = MODEM_SUB_GHZ
            self.radio_driver.radio_set_frequency((defs.modulations_settings_ch_spacing[self.alias][0],
                                                   defs.modulations_settings_ch_spacing[self.alias][1],
                                                                                         self.channel))
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
            # self.radio_driver.radio_set_frequency_2_4ghz((item['channel_spacing_kHz'],
                                                              # item['frequency_0_kHz'],
                                                              # item['channel']))
            # put the radio into RX mode
            logging.info('LISTENING IN 2.4GHz')
            self.radio_driver.radio_trx_enable_2_4ghz()
            logging.debug('putting radio to listen!')
            self.radio_driver.radio_rx_now_2_4ghz()
            logging.debug('RADIO STATE: {0}'.format(self.radio_driver.check_radio_state_rf24()))
            logging.debug('radio listening!')


    # ========================= callbacks =====================================

    def _cb_rx_frame(self, frame_rcv, rssi, crc, mcs):
        self.gpio_handler.led_toggle(self.TRX_frame_pin)
        # self.count_frames_rx += 1
        self.queue_rx.put((frame_rcv, rssi, crc, mcs))

        # re-arm the radio in RX mode
        self.radio_driver.radio_rx_now()
        logging.info('GOT SOMETHING')

    def _cb_push_button(self, channel = 13):
        pass
#  ============================ public ========================================

    def getStats(self):
        # logging.warning('Results ongoing {0}'.format(self.LoggerRx.results))
        logging.warning('TO IMPLEMENT')

# ========================== main =============================================

def main():

    with open('/home/pi/range_test/raspberry/experiment_settings.json', 'r') as f:
        settings = f.read().replace('\n', ' ').replace('\r', '')
        settings = json.loads(settings)

    alias     = sys.argv[1]
    freq_band = sys.argv[2]
    channel   = sys.argv[3] 

    print('alias: {0}, freq: {1}, ch: {2}'.format(type(alias), type(int(freq_band)), type(int(channel))))

    logging.basicConfig(stream=sys.__stdout__, level=logging.DEBUG)
    sniffer = Sniffer(alias, int(freq_band), int(channel))

    while True:
        # for item in
        input = raw_input('>')
        if input == 's':
            print Sniffer.getStats()
        elif input == 'q':
            sys.exit(0)

if __name__ == '__main__':
    main()
