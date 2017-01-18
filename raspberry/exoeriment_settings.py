"""
Lists of frequencies and modulations to be used in the range test.

\author Jonathan Munoz (jonathan.munoz@inria.fr), January 2017
"""

import at86rf215 as at86

frame_lengths = [6, 127, 1000, 2047]
BURST_SIZE    = 100
ie154g.IFS_S  = 0.5

radio_frequencies = [
    #(channel_spacing, frequency_0, channel)
    (             200,      863125,       0),  # fsk operating mode 1
    (             400,      863225,       0),  # fsk operating mode 2-3
    (            1200,      863625,       0),  # ofdm option 1
    (             800,      863425,       0),  # ofdm option 2
    (             400,      863225,       0),  # ofdm option 3
    (             200,      863125,       0),  # ofdm option 4
    (             600,     868300,        0),  # oqpsk
    (             200,      863125,      17),  # fsk operating mode 1
    (             400,      863225,       9),  # fsk operating mode 2-3
    (            1200,      863625,       2),  # ofdm option 1
    (             800,      863425,       4),  # ofdm option 2
    (             400,      863225,       8),  # ofdm option 3
    (             200,      863125,      17),  # ofdm option 4
    (             600,      868950,       0),  # oqpsk
]

radio_configs_tx = [
    at86.fsk_option1_FEC,
    at86.fsk_option2_FEC,
    at86.fsk_option1,
    at86.fsk_option2,
    at86.ofdm_1_mcs0,
    at86.ofdm_2_mcs0,
    at86.ofdm_1_mcs1,
    at86.ofdm_2_mcs1,
    at86.ofdm_3_mcs1,
    at86.ofdm_1_mcs2,
    at86.ofdm_2_mcs2,
    at86.ofdm_3_mcs2,
    at86.ofdm_4_mcs2,
    at86.ofdm_1_mcs3,
    at86.ofdm_2_mcs3,
    at86.ofdm_3_mcs3,
    at86.ofdm_4_mcs3,
    at86.ofdm_2_mcs4,
    at86.ofdm_3_mcs4,
    at86.ofdm_4_mcs4,
    at86.ofdm_2_mcs5,
    at86.ofdm_3_mcs5,
    at86.ofdm_4_mcs5,
    at86.ofdm_3_mcs6,
    at86.ofdm_4_mcs6,
    at86.oqpsk_rate1,
    at86.oqpsk_rate2,
    at86.oqpsk_rate3,
    at86.oqpsk_rate4,
    at86.fsk_option3_FEC,
    at86.fsk_option3,
]

radio_configs_rx = [
    at86.fsk_option1_FEC,
    at86.fsk_option2_FEC,
    at86.fsk_option1,
    at86.fsk_option2,
    at86.ofdm_1_mcs0,
    at86.ofdm_2_mcs0,
    at86.ofdm_3_mcs1,
    at86.ofdm_4_mcs2,
    at86.oqpsk_rate1
]
