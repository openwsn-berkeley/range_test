import radio_rpi as radio
import at86rf215 as at86
import time
import sys
import logging

PACKET_LENGTH = 2047
CRC_SIZE = 4

##def main():
#    spi = radio.init_spi()
#    radio.init_GPIO()
#    radio.reset()
#    pkt_nb = 0
#    packet = [i&0xFF for i in range(PACKET_LENGTH)]

#    for modulations_rx in at86.modulation_list_rx:
#        radio.write_config(modulations_rx)
#        for freq_setup in at86.frequencies_setup:
#            radio.modem_off()
#            radio.set_frequency(freq_setup)
#            #while(!next_freq)
#                radio.trx_enable()
#                radio.rx_enable()
#                #(isr receive packet)
#                    (pkt_rcv, rssi, crc, mcs) = radio.get_received_frame()

spi = radio.init_spi()
radio.init_GPIO()
radio.reset()
