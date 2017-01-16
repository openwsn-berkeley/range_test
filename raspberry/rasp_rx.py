import radio_rpi as radio
import at86rf215 as at86
import time
import sys
import logging

PACKET_LENGTH = 2047
CRC_SIZE = 4

def main():
    spi = radio.init_spi()
    radio.init_GPIO()
    radio.reset()

    radio.write_config(at86.modulation_list_rx[0])
    radio.set_frequency(at86.frequencies_setup[0])
    
    radio.trx_enable()
    print('radio enable')
    radio.rx_now()

    while 1:
        #global at86_state
        radio.at86_state = 0
        print (radio.at86_state)
        radio.rx_done = 0
        while radio.at86_state != radio.RADIOSTATE_TXRX_DONE:
            pass
        
        print (radio.at86_state)
        print('hola')
        (pkt_rcv, rssi, crc, mcs) = radio.get_received_frame()
        print(pkt_rcv, rssi, crc, mcs)
        radio.rx_now()


if __name__ == '__main__':
    main()
