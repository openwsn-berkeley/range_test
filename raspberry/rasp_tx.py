import radio_rpi as radio
import at86rf215 as at86
import time
PACKET_LENGTH = 2047
CRC_SIZE = 4
radio.at86_state = 0
def main():
    radio.init_spi()
    radio.init_GPIO()
    radio.reset()
    radio.read_isr()
    pkt_nb = 0
    packet = [i&0xFF for i in range(PACKET_LENGTH)]
    print (packet[:15])
    for modulations_tx in at86.modulation_list_tx:
        radio.write_config(modulations_tx)
        for i in range(len(at86.frequencies_setup)):
            radio.modem_off()
            radio.set_frequency(at86.frequencies_setup[i])
            radio.modem_off()
            for i in at86.packet_sizes :
                pkt_size = radio.change_pkt_size(at86.packet_sizes, i%4)
                for i in range(100):
                    pkt_nb += 1
                    packet = [pkt_nb&0xFF, pkt_nb>>8] + packet
                    radio.load_packet(packet[:pkt_size - CRC_SIZE])
                    radio.tx_enable()
                    print('radio enabled')
                    radio.tx_now()
                    print('packet sent')
            #radio.gps_next_mod()


#GPIO.add_event_detect(3,GPIO.RISING,read_isr)

if __name__ == '__main__':
    main()
