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

\author Jonathan Munoz (jonathan.munoz@inria.fr), January 2017
"""

import threading
import time
import logging

import spidev
import RPi.GPIO as GPIO

import at86rf215 as at86

RADIOSTATE_RFOFF = 0x00  # ///< Completely stopped.
RADIOSTATE_FREQUENCY_SET = 0x01  # ///< Listening for commands, but RF chain is off.
RADIOSTATE_PACKET_LOADED = 0x02  # ///< Configuring the frequency.
RADIOSTATE_TRX_ENABLED = 0x03  # ///< Done configuring the frequency.
RADIOSTATE_RECEIVING = 0x04  # ///< Loading packet into the radio's TX buffer.
RADIOSTATE_TXRX_DONE = 0x05  # ///< Packet is fully loaded in the radio's TX buffer.


# FIXME: turn code in this file into a class

class At86rf215(object):
    at86_state = RADIOSTATE_RFOFF
    #rx_done = 0
    #spi = 0

    def __init__(self, cb):
        self.cb = cb

    # ======================== public ==========================================

    def method1(self, param1):
        pass

    # ======================== private =========================================

    def _method2(self, param1):
        pass

    def read_isr(self):
        """
        Read the interruption source from the radio.

        This function is called typically after the interrupt pin triggers.
        The CPU then called this function the read the 4 RG_RFXX_IRQS registers
        to figure out the reason for the interrupt.

        FIXME: document parameter "channel"
        """

        isr = self.radio_read_spi(at86.RG_RF09_IRQS, 4)
        if isr[0] & at86.IRQS_TRXRDY_MASK:
            self.at86_state = RADIOSTATE_TRX_ENABLED
            # FIXME: use logging module, see https://github.com/openwsn-berkeley/openwsn-sw/blob/develop/software/openvisualizer/openvisualizer/openTun/openTun.py#L6
            # debug, info, warning, error, critical
            print('at86 state is {0}'.format(self.at86_state))  # FIXME: change string formatting
        if isr[2] & at86.IRQS_RXFS_MASK:
            self.at86_state = RADIOSTATE_RECEIVING
            print('at86 state is {0}'.format(self.at86_state))
        if isr[2] & at86.IRQS_TXFE_MASK:
            self.at86_state = RADIOSTATE_TXRX_DONE
            print('at86 state is {0}'.format(self.at86_state))
        if isr[2] & at86.IRQS_RXFE_MASK:
            self.at86_state = RADIOSTATE_TXRX_DONE
            print('at86 state is {0}'.format(self.at86_state))
            (pkt_rcv, rssi, crc, mcs) = self.radio_get_received_frame()
            self.cb(pkt_rcv, rssi, crc, mcs)
            self.radio_rx_now()

    def cb_gpio(self, channel = 3):
        self.read_isr()

    def radio_init(self, channel=3):
        """
        Initialize the GPIO and SPI modules.
        :param channel: the number of the GPIO-pin which receives the IRQ pin from the radio.
        :return:
        """

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(channel, GPIO.IN)
        GPIO.add_event_detect(channel, GPIO.RISING, self.cb_gpio)

    def radio_reset(self):
        """
        It reset the radio.
        :return: Nothing
        """
        self.radio_write_spi(at86.RG_RF_RST, at86.RST_CMD)

    def radio_set_frequency(self, channel_set_up):
        """
        # channel_spacing in kHz
        # frequency_0 in kHz
        # channel number
        # def set_frequency(channel_spacing, frequency_0, channel):
        """
        frequency_0 = channel_set_up[1] / 25
        self.radio_write_spi(at86.RG_RF09_CS, channel_set_up[0] / 25)
        self.radio_write_spi(at86.RG_RF09_CCF0L, frequency_0 & 0xFF)
        self.radio_write_spi(at86.RG_RF09_CCF0H, frequency_0 >> 8)
        self.radio_write_spi(at86.RG_RF09_CNL, channel_set_up[2] & 0xFF)
        self.radio_write_spi(at86.RG_RF09_CNM, channel_set_up[2] >> 8)

    # FIXME: rename to radio_off
    def radio_off(self):
        """
        Puts the radio in the TRXOFF mode.
        :return: Nothing
        """
        self.radio_write_spi(at86.RG_RF09_CMD, at86.CMD_RF_TRXOFF)

    # FIXME: unclear what this is used for
    def change_pkt_size(self, sizes, size):
        return sizes[size]

    # TX
    def radio_load_packet(self, packet):
        """
        Sends a packet to the buffer of the radio.
        :param packet: the packet to be sent.
        :return: Nothing
        """
        # send the size of the packet + size of the CRC (4 bytes)
        fifo_tx_len = at86.RG_BBC0_TXFLL[:] + [((len(packet) + 4) & 0xFF), (((len(packet) + 4) >> 8) & 0x07)]
        fifo_tx_len[0] |= 0x80
        self.radio_write_spi(fifo_tx_len)
        # send the packet to the modem tx fifo
        pkt = at86.RG_BBC0_FBTXS[:] + packet
        pkt[0] |= 0x80
        self.radio_write_spi(pkt)

    def radio_trx_enable(self):
        """
        Puts the radio in the TRXPREP, previous state to send/receive. It waits until receives a signal from the radio.
        :return: Nothing
        """
        self.radio_write_spi(at86.RG_RF09_CMD, at86.CMD_RF_TXPREP)
        while self.at86_state != RADIOSTATE_TRX_ENABLED:
            pass

    def radio_tx_now(self):
        """
        Commands the radio to send a previous loaded packet. It waits until the radio confirms the success.
        :return: Nothing
        """
        self.radio_write_spi(at86.RG_RF09_CMD, at86.CMD_RF_TX)
        while self.at86_state != RADIOSTATE_TXRX_DONE:
            pass
            # TODO: foreseen the case when there is a failure in the tx -TXRERR.

    # RX
    def radio_rx_now(self):
        """
        Puts the radio in reception mode, listening for packets.
        :return:
        """
        self.radio_write_spi(at86.RG_RF09_CMD, at86.CMD_RF_RX)

    def radio_get_received_frame(self):
        """
        Demands to the radio the received packet
        :return: a tuple with 1) packet received, 2) rssi, 3) crc(boolean) 4) mcs (valid for OFDM).
        """
        # get the length of the frame
        rcv = self.radio_read_spi(at86.RG_BBC0_RXFLL, 2)
        len_pkt = rcv[0] + ((rcv[1] & 0x07) << 8)

        print('length is {0}'.format(len_pkt))

        # read the packet
        pkt_rcv = self.radio_read_spi(at86.RG_BBC0_FBRXS, len_pkt)

        # read from metadata
        rssi = self.radio_read_spi(at86.RG_RF09_EDV, 1)[0]
        crc = ((self.radio_read_spi(at86.RG_BBC0_PC, 1))[0] >> 5) & 0x01
        mcs = self.radio_read_spi(at86.RG_BBC0_OFDMPHRRX, 1)[0] & at86.OFDMPHRRX_MCS_MASK

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
        data = self.spi.xfer(reg)
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
        self.spi.xfer(reg)
