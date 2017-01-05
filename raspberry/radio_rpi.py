#tx
#ofdm1 -> 65  -> 80
#ofdm2 -> 129 -> 140
#ofdm3 -> 135 -> 150
#ofdm4 -> 137 -> 150

#	fsk-1 NFEC -> 56 -> 70
#	fsk-2 NFEC -> 30 -> 40

#	fsk1 FEC -> 107 -> 120
#	fsk2 FEC -> 56  -> 70

#	o-qpsk1 -> 448 -> 460
#	o-qpsk2 -> 230 -> 240
#	o-qpsk3 -> 122 -> 130
#	o-qpsk4 -> 67  -> 80

#	TOTAL 1730 -> 28 min, 



#	TODO 04/01/17
#	1) GPS reading from raspberry pi and updating time system
#	2) GPIO and spi raspberry pi - atmel. Solve this question.S

import spidev
import RPi.GPIO as GPIO
import at86rf215 as at86

spi = spidev.SpiDev()
spi.open(0,0)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(3, GPIO.IN)

#address list e.g. [0x01,0x34]
#bytes quantity of bytes to receive after the address is given
def trx_spi(address, bytes = 0):
	d = address[:]
	for i in range(b):
		d.append(0x00)
	c = spi.xfer(d) 
	return c

def read_isr(channel):
	a = [0x00,0x00,0x00,0x00,0x00,0x00]
	isr = trx_spi(a)
	return isr[2:]

def write_spi(a, b):
	cmd = a[:]
	cmd.append(b)
	trx_spi(cmd)

def reset():
	trx_spi(RG_RF_RST, RST_CMD)

#channel_spacing in kHz
#frequency_0 in kHz
#channel number
def radio_set_frequency(channel_spacing, frequency_0, channel):
	write_spi(RG_RF09_CS, channel_spacing/25)
	write_spi(RG_RF09_CCF0L, frequency_0 & 0xFF)
	write_spi(RG_RF09_CCF0H, frequency_0 >> 8)
	write_spi(RG_RF09_CNL, channel & 0xFF)
	write_spi(RG_RF09_CNM, channel >>8)

def modem_off():
	write_spi(RG_RF09_CMD, CMD_RF_TRXOFF)

# TX

def load_packet():







