import sys

import spidev
import RPi.GPIO as GPIO


def check_state(spi):
    state = [0, 0, 0, 0, 0, 0]
    return spi.xfer(state)[2:]


def check_radio(spi):
    radio_state = [0x01, 0x02, 0x00]
    return spi.xfer(radio_state)[2:]


def check_radio_2ghz(spi):
    radio_state = [0x02, 0x02, 0x00]
    return spi.xfer(radio_state)[2:]


def sleep(spi):
    to_write = [0x81, 0x03, 0x01]
    print spi.xfer(to_write)[2:]
    to_write = [0x82, 0x03, 0x01]
    print spi.xfer(to_write)[2:]
    return ('maybe sleeping')

def main():
    spi = spidev.SpiDev()
    spi.open(0, 0)
    GPIO.setmode(GPIO.BOARD)

    while True:
        input = raw_input('>')
        if input == 's':
            print check_state(spi)
        elif input == 'q':
            sys.exit(0)
        elif input == 'r':
            print check_radio(spi)
        elif input == 'p':
            print check_radio_2ghz(spi)
        elif input == 'sleep':
            print (sleep(spi))


if __name__ == '__main__':
    main()