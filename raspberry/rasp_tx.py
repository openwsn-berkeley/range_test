import radio_rpi as radio
import at86rf215 as at86
PACKET_LENGTH = 2047

def main():
    radio.init_spi()
    radio.init_GPIO()
    radio.reset()
    pkt_nb = 0
    packet = [i&0xFF for i in range(PACKET_LENGTH)]
    while(True):
        radio.modem_off()
        radio.set_frequency(at86.frequencies_setup[0])
        radio.modem_off()
        for i in at86.packet_sizes :
            for i in range(100):
                pkt_nb += 1
                packet = [pkt_nb&0xFF, pkt_nb>>8] + packet



if __name__ == '__main__':
