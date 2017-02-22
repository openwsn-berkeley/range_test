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
# import experiment_settings as settings

FRAME_LENGTH  = 2047
CRC_SIZE      = 4
SECURITY_TIME = 3 # 3 seconds to give more time to TRX to complete the 400 frame bursts.


class InformativeTx(threading.Thread):

    def __init__(self, queue):

        # store parameters
        self.queue = queue
        self.results = {'Time Experiment:': time.strftime("%a, %d %b %Y %H:%M:%S UTC", time.gmtime()),
                        'Time for this set of settings:': None}

        # local variables

        # start the thread
        threading.Thread.__init__(self)
        self.name = 'InformativeTx'
        self.daemon = True
        self.start()

        logging.basicConfig(stream=sys.__stdout__, level=logging.WARNING)
        # logging.basicConfig(filename='range_test_tx.log', level=logging.WARNING)

    def run(self):

        while True:
            item = self.queue.get()
            if type(item) is tuple:
                logging.warning('Time to send the frames {0} - {1} was {2} seconds\n'.format(item[0] - 100, item[0],
                                                                                             item[1]))

            else:
                logging.warning('Modulation used is: {0}\n'.format(item))

"""
class TxTimer(threading.Thread):

    TIMER_PERIOD = 0.0200

    def __init__(self, event):

        # store parameters
        self.event = event
        # self.timer_period
        # local variables

        # start the thread
        threading.Thread.__init__(self)
        self.name = 'TxTimer'
        self.daemon = True
        self.start()

    def run(self):
        while True:
            time.sleep(self.TIMER_PERIOD)
            self.event.set()

"""


class ExperimentTx(threading.Thread):
    
    def __init__(self, hours, minutes, settings):
        
        # local variables
        self.radio_driver = None
        self.settings = settings
        self.hours = hours
        self.minutes = minutes
        # self.start_time = start_time
        self.index = 0
        self.queue_tx = Queue.Queue()
        self.started_time = time.time()
        self.chronogramme = ['time' for i in range(31)]
        
        # start the thread
        threading.Thread.__init__(self)
        self.name = 'ExperimentTx_'
        self.daemon = True
        self.start()

        self.txEvent = threading.Event()
        self.txEvent.clear()

        self.informativeTx = InformativeTx(self.queue_tx)
        # self.txTimer = TxTimer(self.txEvent)

        # configure the logging module
        logging.basicConfig(stream= sys.__stdout__, level=logging.WARNING)
        # logging.basicConfig(filename='range_test_tx.log', level=logging.WARNING)

    def radio_setup(self):

        # initialize the radio driver
        self.radio_driver = radio.At86rf215(self._cb_rx_frame)
        self.radio_driver.radio_init(3)
        self.radio_driver.radio_reset()
        self.radio_driver.read_isr_source()  # no functional role, just clear the pending interrupt flag

    def experiment_scheduling(self):
        s = sched.scheduler(time.time, time.sleep)
        time_to_start = dt.combine(dt.now(), datetime.time(self.hours, self.minutes))
        offset = 3
        for item in self.settings['test_settings']:
            # s.enter(offset, 1, self.execute_exp, (item,))
            s.enterabs(time.mktime(time_to_start.timetuple()) + offset, 1, self.execute_exp, (item,))
            self.chronogramme[self.settings['test_settings'].index(item)] = offset
            offset += item['durationtx_s'] + SECURITY_TIME
        logging.warning(self.chronogramme)
        s.run()

    def execute_exp(self, item):
        self.queue_tx.put(time.time() - self.started_time)
        # initialize the frame counter
        frame_counter = 0

        # re-configure the radio
        # self.radio_driver.radio_write_config(settings.radio_configs_tx[self.index])
        self.radio_driver.radio_write_config(defs.modulations_settings[item['modulation']])

        # select the frequency
        self.radio_driver.radio_off()
        # self.radio_driver.radio_set_frequency(settings.radio_frequencies[self.index])
        self.radio_driver.radio_set_frequency((item['channel_spacing_kHz'],
                                               item['frequency_0_kHz'],
                                               item['channel']))

        # log the config name
        # self.queue_tx.put(settings.radio_configs_name[self.index])
        # self.queue_tx.put(settings.test_settings[item]['id'])
        self.queue_tx.put(item)

        noww = time.time()
        # loop through packet lengths
        # for frame_length in settings.frame_lengths:
        for frame_length, ifs in zip(self.settings["frame_lengths"], self.settings["IFS"]):
            # logging.debug('frame length {0}, thread name: {1}'.format(frame_length, self.name))
            now = time.time()
            self.radio_driver.radio_trx_enable()

            # send burst of frames

            for i in range(item["numframes"]):
                # logging.debug('frame burst {0}'.format(i))

                # create frame
                frameToSend = [frame_counter >> 8, frame_counter & 0xFF] + [i & 0xFF for i in range(FRAME_LENGTH - 2)]

                # logging.debug('three first bytes, frame counter: {0}.\n'.format(frameToSend[0:3]))

                # increment the frame counter
                frame_counter += 1

                # send frame
                # self.radio_driver.radio_load_packet(frameToSend[:frame_length - CRC_SIZE])
                self.radio_driver.radio_load_packet(frameToSend[:frame_length - CRC_SIZE])
                self.radio_driver.radio_tx_now()

                # wait for a timeout (to allow the receiver to handle the RX'ed frame)
                # self.txEvent.wait()
                # self.txEvent.clear()
                time.sleep(ifs)

            self.queue_tx.put((frame_counter, time.time() - now))
        # logging.debug('FINAL')
        self.queue_tx.put(time.time() - noww)
        self.index += 1
    
    def run(self):
        # time.sleep(self.start_time)
        self.radio_setup()
        # s = sched.scheduler(time.time, time.sleep)
        # s.enter(self.start_time, 1, self.execute_exp, ())
        # s.run()
        self.experiment_scheduling()


    #  ======================== private =======================================
    
    def _cb_rx_frame(self, frame_rcv, rssi, crc, mcs):
        raise SystemError("frame received on transmitting mote")

#  ============================ main ==========================================

def load_json_files():
    with open('/home/pi/range_test/raspberry/experiment_settings.json', 'r') as f:
        settings = f.read().replace('\n', ' ').replace('\r', '')
        settings = json.loads(settings)
        return settings


def main():
    hours = int(sys.argv[1])
    minutes = int(sys.argv[2])
    # logging.basicConfig(filename='range_test_tx.log', level=logging.WARNING)
    # experimentTx = ExperimentTx(int(sys.argv[1]))
    experimentTx = ExperimentTx(hours, minutes, load_json_files())
    while True:
        input = raw_input('>')
        if input == 's':
            print experimentTx.getStats()
            # print 'print stats TX'
        if input == 'q':
            sys.exit(0)

if __name__ == '__main__':
    main()
