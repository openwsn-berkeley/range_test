"""
Lists of frequencies and modulations to be used in the range test.

\author Jonathan Munoz (jonathan.munoz@inria.fr), January 2017
"""
import at86rf215 as at86

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
    (at86.fsk_option1_FEC),
    (at86.fsk_option2_FEC),
    (at86.fsk_option1),
    (at86.fsk_option2),
    (at86.ofdm_1_mcs0),
    (at86.ofdm_2_mcs0),
    (at86.ofdm_3_mcs1),
    (at86.ofdm_4_mcs2),
    (at86.oqpsk_rate1)
]

modulation_list_tx = [
    (at86.fsk_option1_FEC),  # 01
    (at86.fsk_option2_FEC),  # 02
    (at86.fsk_option1),  # 03
    (at86.fsk_option2),  # 04
    (at86.ofdm_1_mcs0),  # 05
    (at86.ofdm_2_mcs0),  # 06
    (at86.ofdm_1_mcs1),  # 07
    (at86.ofdm_2_mcs1),  # 08
    (at86.ofdm_3_mcs1),  # 09
    (at86.ofdm_1_mcs2),  # 10
    (at86.ofdm_2_mcs2),  # 11
    (at86.ofdm_3_mcs2),  # 12
    (at86.ofdm_4_mcs2),  # 13
    (at86.ofdm_1_mcs3),  # 14
    (at86.ofdm_2_mcs3),  # 15
    (at86.ofdm_3_mcs3),  # 16
    (at86.ofdm_4_mcs3),  # 17
    (at86.ofdm_2_mcs4),  # 18
    (at86.ofdm_3_mcs4),  # 19
    (at86.ofdm_4_mcs4),  # 20
    (at86.ofdm_2_mcs5),  # 21
    (at86.ofdm_3_mcs5),  # 22
    (at86.ofdm_4_mcs5),  # 23
    (at86.ofdm_3_mcs6),  # 24
    (at86.ofdm_4_mcs6),  # 25
    (at86.oqpsk_rate1),  # 26
    (at86.oqpsk_rate2),  # 27
    (at86.oqpsk_rate3),  # 28
    (at86.oqpsk_rate4),  # 29
    (at86.fsk_option3_FEC),  # 30
    (at86.fsk_option3),  # 31
]

packet_sizes = [6, 127, 1000, 2047]
