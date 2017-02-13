"""
Radio driver for the AT86RF215, for the rPi 3.

Connections

| rPi pin | ATREB215-XPRO Extension Board pin |
|---------|-----------------------------------|
| 01- +3V |  20 - VCC                         |
| 03-     |  09 - IRQ                         |
| 09- GND |  19 - GND                         |
| 19-     |  16 - SPI_MOSI                    |
| 21-     |  17 - SPI_MISO                    |
| 23-     |  18 - SPI_SCK                     |
| 24-     |  15 - SPI_SS_A                    |

\author Jonathan Munoz (jonathan.munoz@inria.fr), January 2017.
"""

import threading
import time
import logging
import sys
import Queue

import spidev
import RPi.GPIO as GPIO

import at86rf215_defs as defs

RADIOSTATE_RFOFF = 0x00  # ///< Completely stopped.
RADIOSTATE_FREQUENCY_SET = 0x01  # ///< Listening for commands, but RF chain is off.
RADIOSTATE_PACKET_LOADED = 0x02  # ///< Configuring the frequency.
RADIOSTATE_TRX_ENABLED = 0x03  # ///< Done configuring the frequency.
RADIOSTATE_RECEIVING = 0x04  # ///< Loading packet into the radio's TX buffer.
RADIOSTATE_TXRX_DONE = 0x05  # ///< Packet is fully loaded in the radio's TX buffer.


class Processing(threading.Thread):

    def __init__(self, queue):

        # store parameters
        self.queue = queue

        # local variables

        # start the thread
        threading.Thread.__init__(self)
        self.name = 'processRx'
        self.daemon = True
        self.start()

        # configure the logging module
        logging.basicConfig(stream=sys.__stdout__, level=logging.WARNING)

    def run(self):

        while True:
            item = self.queue.get()
            if type(item) is tuple:
                logging.info('FRAME number: {0}, frame size: {1}, RSSI: {2} dBm,  CRC: {3}, MCS: {4}\n'.
                            format((item[0][0] * 256 + item[0][1]), len(item[0]), item[1], item[2], item[3]))
            else:
                logging.info('Time in the ISR is {0} seconds\n'.format(item))


class At86rf215(object):
    
    def __init__(self, cb):
        
        # store params
        self.cb = cb
        self.queue = Queue.Queue()
        
        # local variables
        self.at86_state         = RADIOSTATE_RFOFF
        self.spi                = spidev.SpiDev()
        self.state_trx_prep     = threading.Event()
        self.state_tx_now       = threading.Event()
        self.state_IFS          = threading.Event()
        self.count              = 0

        self.processing = Processing(self.queue)
        self.state              = {'state_TRXprep': self.state_trx_prep, 'state_TXnow': self.state_tx_now}
        self.state['state_TRXprep'].clear()
        self.state['state_TXnow'].clear()

        # configure the logging module
        logging.basicConfig(stream= sys.__stdout__, level=logging.WARNING)
    
    # ======================== public ==========================================
    
    # ======================== private =========================================
    
    def read_isr_source(self):
        """
        Read the interruption source from the radio.

        This function is called typically after the interrupt pin triggers.
        The CPU then called this function the read the 4 RG_RFXX_IRQS registers
        to figure out the reason for the interrupt.

        FIXME: document parameter "channel"
        """
        now = time.time()
        isr = self.radio_read_spi(defs.RG_RF09_IRQS, 4)
        if isr[0] & defs.IRQS_TRXRDY_MASK:
            self.at86_state = RADIOSTATE_TRX_ENABLED
            self.state['state_TRXprep'].set()

        if isr[2] & defs.IRQS_TXFE_MASK:
            self.at86_state = RADIOSTATE_TXRX_DONE
            self.state['state_TXnow'].set()
            self.count += 1
            self.queue.put(self.count)

        if isr[2] & defs.IRQS_RXFE_MASK:
            self.count += 1
            self.at86_state = RADIOSTATE_TXRX_DONE
            (pkt_rcv, rssi, crc, mcs) = self.radio_get_received_frame()
            self.cb(pkt_rcv, rssi, crc, mcs)
            self.queue.put((pkt_rcv, rssi, crc, mcs))

        self.queue.put(time.time() - now)
        logging.debug('ISR values: {0}'.format(isr[:]))

    def cb_gpio(self, channel = 3):
        self.read_isr_source()

    def radio_init(self, channel=3):
        """
        Initialize the GPIO and SPI modules.
        :param channel: the number of the GPIO-pin which receives the IRQ pin from the radio.
        :return:
        """
        self.spi.open(0, 0)

        # spi speed TEST
        self.spi.max_speed_hz = 7800000

        GPIO.cleanup()
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(channel, GPIO.IN)
        GPIO.add_event_detect(channel, GPIO.RISING, self.cb_gpio)

    def radio_reset(self):
        """
        It reset the radio.
        :return: Nothing
        """
        self.radio_write_spi(defs.RG_RF_RST, defs.RST_CMD)

    def radio_set_frequency(self, channel_set_up):
        """
        # channel_spacing in kHz
        # frequency_0 in kHz
        # channel number
        # def set_frequency(channel_spacing, frequency_0, channel):
        """
        frequency_0 = channel_set_up[1] / 25
        self.radio_write_spi(defs.RG_RF09_CS, channel_set_up[0] / 25)
        self.radio_write_spi(defs.RG_RF09_CCF0L, frequency_0 & 0xFF)
        self.radio_write_spi(defs.RG_RF09_CCF0H, frequency_0 >> 8)
        self.radio_write_spi(defs.RG_RF09_CNL, channel_set_up[2] & 0xFF)
        self.radio_write_spi(defs.RG_RF09_CNM, channel_set_up[2] >> 8)

    # FIXME: rename to radio_off
    def radio_off(self):
        """
        Puts the radio in the TRXOFF mode.
        :return: Nothing
        """
        self.radio_write_spi(defs.RG_RF09_CMD, defs.CMD_RF_TRXOFF)

    # TX
    def radio_load_packet(self, packet):
        """
        Sends a packet to the buffer of the radio.
        :param packet: the packet to be sent.
        :return: Nothing
        """
        # send the size of the packet + size of the CRC (4 bytes)
        fifo_tx_len = defs.RG_BBC0_TXFLL[:] + [((len(packet) + 4) & 0xFF), (((len(packet) + 4) >> 8) & 0x07)]
        fifo_tx_len[0] |= 0x80
        self.radio_write_spi(fifo_tx_len)
        # send the packet to the modem tx fifo
        pkt = defs.RG_BBC0_FBTXS[:] + packet
        pkt[0] |= 0x80
        self.radio_write_spi(pkt)

    def radio_trx_enable(self):
        """
        Puts the radio in the TRXPREP, previous state to send/receive. It waits until receives a signal from the radio.
        :return: Nothing
        """
        self.radio_write_spi(defs.RG_RF09_CMD, defs.CMD_RF_TXPREP)
        #while self.at86_state != RADIOSTATE_TRX_ENABLED:
            #pass
        self.state['state_TRXprep'].wait()
        self.state['state_TRXprep'].clear()

    def radio_tx_now(self):
        """
        Commands the radio to send a previous loaded packet. It waits until the radio confirms the success.
        :return: Nothing
        """
        self.radio_write_spi(defs.RG_RF09_CMD, defs.CMD_RF_TX)
        # while self.at86_state != RADIOSTATE_TXRX_DONE:
        #    pass
            # TODO: foreseen the case when there is a failure in the tx -TXRERR.
        self.state['state_TXnow'].wait()
        self.state['state_TXnow'].clear()

    # RX
    def radio_rx_now(self):
        """
        Puts the radio in reception mode, listening for frames.
        :return:
        """
        self.radio_write_spi(defs.RG_RF09_CMD, defs.CMD_RF_RX)
        #while self.check_radio_state_rf09() is not defs.RF_STATE_RX:
        #    self.radio_write_spi(defs.RG_RF09_CMD, defs.CMD_RF_RX)

    def radio_get_received_frame(self):
        """
        Demands to the radio the received packet
        :return: a tuple with 1) packet received, 2) rssi, 3) crc(boolean) 4) mcs (valid for OFDM).
        """
        # get the length of the frame
        rcv = self.radio_read_spi(defs.RG_BBC0_RXFLL, 2)
        len_pkt = rcv[0] + ((rcv[1] & 0x07) << 8)

        logging.warning('length is {0}'.format(len_pkt))

        # read the packet
        pkt_rcv = self.radio_read_spi(defs.RG_BBC0_FBRXS, len_pkt)
        logging.warning('frame number: {0}'.format(pkt_rcv[0:2]))
        # read from metadata
        rssi = self.radio_read_spi(defs.RG_RF09_EDV, 1)[0]
        crc = ((self.radio_read_spi(defs.RG_BBC0_PC, 1))[0] >> 5) & 0x01
        mcs = self.radio_read_spi(defs.RG_BBC0_OFDMPHRRX, 1)[0] & defs.OFDMPHRRX_MCS_MASK

        # representing the RSSI value in dBm
        if rssi == 127:
            rssi = 'not valid'

        if rssi >= 128:
            rssi = (((~rssi)& 0xFF) + 1) * -1

        return pkt_rcv, rssi, crc, mcs

    def radio_write_config(self, settings):
        """
        It writes a given configuration to the radio, contained in the list of tuples passed as parameters.
        :param settings: a list of tuples containing the address of the registers [0] and the value to write [1]
        :return: nothing
        """
        for reg in settings:
            self.radio_write_spi(reg[0], reg[1])

    def radio_read_spi(self, address, nb_bytes):
        """
        It gets a value or values of the registers starting at the address given.
        :param address: the register to be read
        :param nb_bytes: the amount of bytes to read starting at that address
        :return: the value(s) of the register(s)
        """
        reg = address[:]
        reg += [0x00] * nb_bytes
        data = self.spi.xfer2(reg)
        return data[2:]

    def radio_write_spi(self, address, value=None):
        """
        It writes a value to a register.
        :param address: the register to be written
        :param value: the value to be written
        :return: nothing
        """
        reg = address[:]
        if value is not None:
            reg = address[:] + [value]
        reg[0] |= 0x80
        self.spi.xfer2(reg)

    def check_radio_state_rf09(self):
        """
        It reads the radio state value
        :return: that read value
        """
        add = defs.RG_RF09_STATE[:] + [0x00]
        return self.spi.xfer2(add)[2]
