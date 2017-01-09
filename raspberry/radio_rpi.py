import spidev
import RPi.GPIO as GPIO
import at86rf215 as at86
SIZE_ITERATION = 0

def init_spi():
    spi = spidev.SpiDev()
    spi.open(0, 0)

def init_GPIO():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(3, GPIO.IN)

# address list e.g. [0x01,0x34]
# bytes quantity of bytes to receive after the address is given
def trx_spi(address, bytes=0):
    d = address[:]
    d += [0x00] * bytes
    c = spi.xfer(d)
    return c


def read_isr(channel):
    a = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    isr = trx_spi(a)
    return isr[2:]


def write_spi(a, b):
    cmd = a[:]
    cmd.append(b)
    trx_spi(cmd)


def reset():
    write_spi(at86.RG_RF_RST, at86.RST_CMD)

# channel_spacing in kHz
# frequency_0 in kHz
# channel number
#def set_frequency(channel_spacing, frequency_0, channel):
def set_frequency(channel_set_up):
    write_spi(at86.RG_RF09_CS, channel_set_up[0] / 25)
    write_spi(at86.RG_RF09_CCF0L, channel_set_up[1] & 0xFF)
    write_spi(at86.RG_RF09_CCF0H, channel_set_up[1] >> 8)
    write_spi(at86.RG_RF09_CNL, channel_set_up[2] & 0xFF)
    write_spi(at86.RG_RF09_CNM, channel_set_up[2] >> 8)


def modem_off():
    write_spi(at86.RG_RF09_CMD, at86.CMD_RF_TRXOFF)

def change_pkt_size(sizes, size):
    return sizes[size]

# TX
def load_packet(packet):
    # send the size of the packet
    fifo_tx_len = at86.RG_BBC0_TXFLL + [(len(packet) & 0xFF), ((len(packet) >> 8) & 0x07)]
    trx_spi(fifo_tx_len)
    # send the packet to the modem tx fifo
    pkt = at86.RG_BBC0_FBTXS + packet
    trx_spi(pkt)


def tx_enable():
    write_spi(at86.RG_RF09_CMD, at86.CMD_RF_TXPREP)


def tx_now():
    write_spi(at86.RG_RF09_CMD, at86.CMD_RF_TX)


# RX
def rx_enable():
    write_spi(at86.RG_RF09_CMD, at86.CMD_RF_RX)


def get_received_frame():
    rcv = trx_spi(at86.RG_BBC0_RXFLL, 2)
    len_pkt = rcv[0] | ((rcv[1] & 0x07) << 8)
    pkt_rcv = trx_spi(at86.RG_BBC0_FBRXS, len_pkt)
    rssi = trx_spi(at86.RG_RF09_EDV, 1)
    crc = (trx_spi(at86.RG_BBC0_PC)) >> 5
    mcs = trx_spi(at86.RG_BBC0_OFDMPHRRX) & at86.OFDMPHRRX_MCS_MASK
    return pkt_rcv, rssi, crc, mcs

# GPS control modulation signal


