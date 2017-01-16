'''
Radio driver for the AT86RF215, for the rPi 3.

Connections

| rPi pin | ATREB215-XPRO Extension Board pin |
|---------|-----------------------------------|
| TODO    | TODO                              |

\author Jonathan Munoz (jonathan.munoz@inria.fr), January 2017
'''

import spidev
import RPi.GPIO as GPIO
import at86rf215 as at86
import time
global at86_state 
global rx_done

RADIOSTATE_RFOFF = 0x00  # ///< Completely stopped.
RADIOSTATE_FREQUENCY_SET = 0x01  # ///< Listening for commands, but RF chain is off.
RADIOSTATE_PACKET_LOADED = 0x02  # ///< Configuring the frequency.
RADIOSTATE_TRX_ENABLED = 0x03  # ///< Done configuring the frequency.
RADIOSTATE_RECEIVING = 0x04  # ///< Loading packet into the radio's TX buffer.
RADIOSTATE_TXRX_DONE = 0x05  # ///< Packet is fully loaded in the radio's TX buffer.

# FIXME: remove those lines

# modem states
RF_STATE_TRXOFF = 0x2
RF_STATE_TXPREP = 0x3
RF_STATE_TX = 0x4
RF_STATE_RX = 0x5
RF_STATE_TRANSITION = 0x6
RF_STATE_RESET = 0x7

# Baseband IRQ Status
IRQS_RXFS = 0x01
IRQS_RXFE = 0x02
IRQS_RXAM = 0x04
IRQS_RXEM = 0x08
IRQS_TXFE = 0x10
IRQS_AGCH = 0x20
IRQS_AGCR = 0x40
IRQS_FBLI = 0x80

IRQS_TXFE_MASK = 0x10
IRQS_TRXRDY_MASK = 0x02
IRQS_RXFS_MASK = 0x01
IRQS_RXFE_MASK = 0x02

# FIXME: turn code in this file into a class

class At86rf215(object):
    var1 = 1
    var2 = 2
    
    def __init__(self):
        pass
    
    #======================== public ==========================================
    
    def method1(self,param1):
        pass
    
    #======================== private =========================================
    
    def _method2(self,param1):
        pass

at86_state = RADIOSTATE_RFOFF
rx_done    = 0

def read_isr():
    '''
    Read the interruption source from the radio.
    
    This function is called typically after the interrupt pin triggers.
    The CPU then called this function the read the 4 RG_RFXX_IRQS registers
    to figure out the reason for the interrupt.
    
    FIXME: document parameter "channel"
    '''
    global at86_state
    global rx_done
    a   = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00] # FIXME: unused
    isr = trx_spi(at86.RG_RF09_IRQS, 4)
    if isr[2] & IRQS_TRXRDY_MASK:
        at86_state = RADIOSTATE_TRX_ENABLED
        # FIXME: use logging module, see https://github.com/openwsn-berkeley/openwsn-sw/blob/develop/software/openvisualizer/openvisualizer/openTun/openTun.py#L6
        # debug, info, warning, error, critical
        print('at86 state is {0}'.format(at86_state)) #FIXME: change string formatting
    if isr[4] & IRQS_RXFS_MASK:
        at86_state = RADIOSTATE_RECEIVING
        print('at86 state is %d' %at86_state )
    if isr[4] & IRQS_TXFE_MASK:
        at86_state = RADIOSTATE_TXRX_DONE
        print('at86 state is %d' %at86_state )
    if isr[4] & IRQS_RXFE_MASK:
        at86_state = RADIOSTATE_TXRX_DONE
        rx_done = 1
        
        print('at86 state is %d' %at86_state )

def cb_gpio(channel = 3):
    read_isr()

def init_spi():
    global spi
    spi = spidev.SpiDev()
    spi.open(0, 0)

def init_GPIO():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(3, GPIO.IN)
    GPIO.add_event_detect(3, GPIO.RISING, cb_gpio)

def trx_spi(address, bytes=0):
    '''
    # address list e.g. [0x01,0x34]
    # bytes quantity of bytes to receive after the address is given
    '''
    d  = address[:]
    d += [0x00] * bytes
    c  = spi.xfer(d)
    return c

def write_spi(a, b):
    cmd = a[:]
    cmd.append(b)
    cmd[0] |= 0x80
    trx_spi(cmd)

# FIXME: rename to radio_reset
def reset():
    write_spi(at86.RG_RF_RST, at86.RST_CMD)

def set_frequency(channel_set_up):
    '''
    # channel_spacing in kHz
    # frequency_0 in kHz
    # channel number
    # def set_frequency(channel_spacing, frequency_0, channel):
    '''
    frequency_0 = channel_set_up[1] / 25
    write_spi(at86.RG_RF09_CS, channel_set_up[0] / 25)
    write_spi(at86.RG_RF09_CCF0L, frequency_0 & 0xFF)
    write_spi(at86.RG_RF09_CCF0H, frequency_0 >> 8)
    write_spi(at86.RG_RF09_CNL, channel_set_up[2] & 0xFF)
    write_spi(at86.RG_RF09_CNM, channel_set_up[2] >> 8)

# FIXME: rename to radio_off
def modem_off():
    write_spi(at86.RG_RF09_CMD, at86.CMD_RF_TRXOFF)

# FIXME: unclear what this is used for
def change_pkt_size(sizes, size):
    return sizes[size]

# TX
def load_packet(packet):
    # send the size of the packet + size of the CRC (4 bytes)
    fifo_tx_len = at86.RG_BBC0_TXFLL[:] + [((len(packet) + 4) & 0xFF), (((len(packet) + 4) >> 8) & 0x07)]
    fifo_tx_len[0] |= 0x80
    trx_spi(fifo_tx_len)
    # send the packet to the modem tx fifo
    pkt = at86.RG_BBC0_FBTXS[:] + packet
    pkt[0] |= 0x80
    trx_spi(pkt)

def trx_enable():
    global at86_state
    write_spi(at86.RG_RF09_CMD, at86.CMD_RF_TXPREP)
    print('Im sending %d'%at86.CMD_RF_TXPREP)
    while at86_state != RADIOSTATE_TRX_ENABLED:
        pass

def tx_now():
    write_spi(at86.RG_RF09_CMD, at86.CMD_RF_TX)
    while at86_state != RADIOSTATE_TXRX_DONE:
        pass

# RX
def rx_now():
    write_spi(at86.RG_RF09_CMD, at86.CMD_RF_RX)

def get_received_frame():
    # get the length of the frame
    rcv     = trx_spi(at86.RG_BBC0_RXFLL, 2)
    len_pkt = rcv[2] + ((rcv[3] & 0x07) << 8)
    
    print (type(len_pkt))
    print('length is %03d' %len_pkt)
    
    # read the packet
    pkt_rcv = trx_spi(at86.RG_BBC0_FBRXS, len_pkt)
    
    # read from metadata
    rssi    = trx_spi(at86.RG_RF09_EDV, 1)[2]
    crc     = ((trx_spi(at86.RG_BBC0_PC, 1))[2] >> 5) & 0x01
    mcs     = trx_spi(at86.RG_BBC0_OFDMPHRRX, 1)[2] & at86.OFDMPHRRX_MCS_MASK
    
    return (pkt_rcv,rssi,crc,mcs)

def write_config(settings):
    for reg in settings:
        write_spi(reg[0], reg[1])
