"""
Lists of frequencies and modulations to be used in the range test.

\author Jonathan Munoz (jonathan.munoz@inria.fr), January 2017
"""

import at86rf215_defs as defs
import json

frame_lengths = [8, 127, 1000, 2047]
BURST_SIZE    = 100
IFS_S         = 0.1

radio_frequencies = [
    #(channel_spacing, frequency_0, channel)
    (             200,      863125,       0),  # fsk operating mode 1
    (             400,      863225,       0),  # fsk operating mode 2-3
    (             400,      863225,       0),  # fsk operating mode 2-3
    (             200,      863125,       0),  # fsk operating mode 1
    (             400,      863225,       0),  # fsk operating mode 2-3
    (             400,      863225,       0),  # fsk operating mode 2-3
    (            1200,      863625,       0),  # ofdm option 1
    (            1200,      863625,       0),  # ofdm option 1
    (            1200,      863625,       0),  # ofdm option 1
    (            1200,      863625,       0),  # ofdm option 1
    (             800,      863425,       0),  # ofdm option 2
    (             800,      863425,       0),  # ofdm option 2
    (             800,      863425,       0),  # ofdm option 2
    (             800,      863425,       0),  # ofdm option 2
    (             800,      863425,       0),  # ofdm option 2
    (             800,      863425,       0),  # ofdm option 2
    (             400,      863225,       0),  # ofdm option 3
    (             400,      863225,       0),  # ofdm option 3
    (             400,      863225,       0),  # ofdm option 3
    (             400,      863225,       0),  # ofdm option 3
    (             400,      863225,       0),  # ofdm option 3
    (             400,      863225,       0),  # ofdm option 3
    (             200,      863125,       0),  # ofdm option 4
    (             200,      863125,       0),  # ofdm option 4
    (             200,      863125,       0),  # ofdm option 4
    (             200,      863125,       0),  # ofdm option 4
    (             200,      863125,       0),  # ofdm option 4
    (             600,      868300,       0),  # oqpsk
    (             600,      868300,       0),  # oqpsk
    (             600,      868300,       0),  # oqpsk
    (             600,      868300,       0),  # oqpsk
]

# range_experiment_setup =

radio_configs_tx = [
    defs.fsk_option1_FEC,
    defs.fsk_option2_FEC,
    defs.fsk_option3_FEC,
    defs.fsk_option1,
    defs.fsk_option2,
    defs.fsk_option3,
    defs.ofdm_1_mcs0,
    defs.ofdm_1_mcs1,
    defs.ofdm_1_mcs2,
    defs.ofdm_1_mcs3,
    defs.ofdm_2_mcs0,
    defs.ofdm_2_mcs1,
    defs.ofdm_2_mcs2,
    defs.ofdm_2_mcs3,
    defs.ofdm_2_mcs4,
    defs.ofdm_2_mcs5,
    defs.ofdm_3_mcs1,
    defs.ofdm_3_mcs2,
    defs.ofdm_3_mcs3,
    defs.ofdm_3_mcs4,
    defs.ofdm_3_mcs5,
    defs.ofdm_3_mcs6,
    defs.ofdm_4_mcs2,
    defs.ofdm_4_mcs3,
    defs.ofdm_4_mcs4,
    defs.ofdm_4_mcs5,
    defs.ofdm_4_mcs6,
    defs.oqpsk_rate0,
    defs.oqpsk_rate1,
    defs.oqpsk_rate2,
    defs.oqpsk_rate3,

]

radio_configs_rx = [
    defs.fsk_option1_FEC,
    defs.fsk_option2_FEC,
    defs.fsk_option3_FEC,
    defs.fsk_option1,
    defs.fsk_option2,
    defs.fsk_option3,
    defs.ofdm_1_mcs0,
    defs.ofdm_1_mcs1,
    defs.ofdm_1_mcs2,
    defs.ofdm_1_mcs3,
    defs.ofdm_2_mcs0,
    defs.ofdm_2_mcs1,
    defs.ofdm_2_mcs2,
    defs.ofdm_2_mcs3,
    defs.ofdm_2_mcs4,
    defs.ofdm_2_mcs5,
    defs.ofdm_3_mcs1,
    defs.ofdm_3_mcs2,
    defs.ofdm_3_mcs3,
    defs.ofdm_3_mcs4,
    defs.ofdm_3_mcs5,
    defs.ofdm_3_mcs6,
    defs.ofdm_4_mcs2,
    defs.ofdm_4_mcs3,
    defs.ofdm_4_mcs4,
    defs.ofdm_4_mcs5,
    defs.ofdm_4_mcs6,
    defs.oqpsk_rate0,
    defs.oqpsk_rate1,
    defs.oqpsk_rate2,
    defs.oqpsk_rate3,
]

radio_configs_name = [
    'fsk_option1_FEC',
    'fsk_option2_FEC',
    'fsk_option3_FEC',
    'fsk_option1',
    'fsk_option2',
    'fsk_option3',
    'ofdm_1_mcs0',
    'ofdm_1_mcs1',
    'ofdm_1_mcs2',
    'ofdm_1_mcs3',
    'ofdm_2_mcs0',
    'ofdm_2_mcs1',
    'ofdm_2_mcs2',
    'ofdm_2_mcs3',
    'ofdm_2_mcs4',
    'ofdm_2_mcs5',
    'ofdm_3_mcs1',
    'ofdm_3_mcs2',
    'ofdm_3_mcs3',
    'ofdm_3_mcs4',
    'ofdm_3_mcs5',
    'ofdm_3_mcs6',
    'ofdm_4_mcs2',
    'ofdm_4_mcs3',
    'ofdm_4_mcs4',
    'ofdm_4_mcs5',
    'ofdm_4_mcs6',
    'oqpsk_rate0',
    'oqpsk_rate1',
    'oqpsk_rate2',
    'oqpsk_rate3',
]
