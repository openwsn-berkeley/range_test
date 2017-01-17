'''
Lists of frequencies and modulations to be used in the range test.

\author Jonathan Munoz (jonathan.munoz@inria.fr), January 2017
'''

# set_frequency(channel_spacing, frequency_0, channel)
frequencies_setup = [
    (200, 863125, 0),  # fsk operating mode 1
    (400, 863225, 0),  # fsk operating mode 2-3
    (1200, 863625, 0),  # ofdm option 1
    (800, 863425, 0),  # ofdm option 2
    (400, 863225, 0),  # ofdm option 3
    (200, 863125, 0),  # ofdm option 4
    (600, 868300, 0),  # oqpsk
    (200, 863125, 17),  # fsk operating mode 1
    (400, 863225, 9),  # fsk operating mode 2-3
    (1200, 863625, 2),  # ofdm option 1
    (800, 863425, 4),  # ofdm option 2
    (400, 863225, 8),  # ofdm option 3
    (200, 863125, 17),  # ofdm option 4
    (600, 868950, 0)  # oqpsk
]

modulation_list_rx = [
    (fsk_option1_FEC),
    (fsk_option2_FEC),
    (fsk_option1),
    (fsk_option2),
    (ofdm_1_mcs0),
    (ofdm_2_mcs0),
    (ofdm_3_mcs1),
    (ofdm_4_mcs2),
    (oqpsk_rate1)
]

modulation_list_tx = [
    (fsk_option1_FEC),  # 01
    (fsk_option2_FEC),  # 02
    (fsk_option1),  # 03
    (fsk_option2),  # 04
    (ofdm_1_mcs0),  # 05
    (ofdm_2_mcs0),  # 06
    (ofdm_1_mcs1),  # 07
    (ofdm_2_mcs1),  # 08
    (ofdm_3_mcs1),  # 09
    (ofdm_1_mcs2),  # 10
    (ofdm_2_mcs2),  # 11
    (ofdm_3_mcs2),  # 12
    (ofdm_4_mcs2),  # 13
    (ofdm_1_mcs3),  # 14
    (ofdm_2_mcs3),  # 15
    (ofdm_3_mcs3),  # 16
    (ofdm_4_mcs3),  # 17
    (ofdm_2_mcs4),  # 18
    (ofdm_3_mcs4),  # 19
    (ofdm_4_mcs4),  # 20
    (ofdm_2_mcs5),  # 21
    (ofdm_3_mcs5),  # 22
    (ofdm_4_mcs5),  # 23
    (ofdm_3_mcs6),  # 24
    (ofdm_4_mcs6),  # 25
    (oqpsk_rate1),  # 26
    (oqpsk_rate2),  # 27
    (oqpsk_rate3),  # 28
    (oqpsk_rate4),  # 29
    (fsk_option3_FEC),  # 30
    (fsk_option3),  # 31
]

packet_sizes = [6, 127, 1000, 2047]