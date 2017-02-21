"""
Lists of frequencies and modulations to be used in the range test.

\author Jonathan Munoz (jonathan.munoz@inria.fr), January 2017
"""

import at86rf215_defs as defs
import json

frame_lengths = [8, 127, 1000, 2047]
BURST_SIZE    = 100
IFS_S         = 0.1

radio_TRX_parameters = {
    'frame size 8 bytes': (8, 0.002),
    'frame size 127 bytes': (127, 0.003),
    'frame size 1000 bytes': (1000, 0.005),
    'frame size 2047 bytes': (2047, 0.0065),
}
radio_TRX_order = {'order': [radio_TRX_parameters['frame size 8 bytes'], radio_TRX_parameters['frame size 127 bytes'],
                             radio_TRX_parameters['frame size 1000 bytes'],
                             radio_TRX_parameters['frame size 2047 bytes']]}

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


radio_freq_setup = {
    u'fsk operating mode 1': (200, 863125, 0), u'fsk operating mode 2': (400, 863225, 0),
    u'fsk operating mode 3': (400, 863225, 0), u'ofdm option 1': (1200, 863625, 0),
    u'ofdm option 2': (800, 863425, 0), u'ofdm option 3': (400, 863225, 0), u'ofdm option 4': (200, 863125, 0),
    u'o-qpsk': (600, 868300, 0)
}

radio_trx_mod_order = {u'order': [u'FSK operating mode 1 FEC', u'FSK operating mode 2 FEC',
                                  u'FSK operating mode 3 FEC', u'FSK operating mode 1 no FEC',
                                  u'FSK operating mode 2 no FEC', u'FSK operating mode 3 no FEC',
                                  u'OFDM Option 1 MCS 0', u'OFDM Option 1 MCS 1', u'OFDM Option 1 MCS 2',
                                  u'OFDM Option 1 MCS 3', u'OFDM Option 2 MCS 0', u'OFDM Option 2 MCS 1',
                                  u'OFDM Option 2 MCS 2', u'OFDM Option 2 MCS 3', u'OFDM Option 2 MCS 4',
                                  u'OFDM Option 2 MCS 5', u'OFDM Option 3 MCS 1', u'OFDM Option 3 MCS 2',
                                  u'OFDM Option 3 MCS 3', u'OFDM Option 3 MCS 4', u'OFDM Option 3 MCS 5',
                                  u'OFDM Option 3 MCS 6', u'OFDM Option 4 MCS 2', u'OFDM Option 4 MCS 3',
                                  u'OFDM Option 4 MCS 4', u'OFDM Option 4 MCS 5', u'OFDM Option 4 MCS 6',
                                  u'O-QPSK rate mode 0', u'O-QPSK rate mode 1', u'O-QPSK rate mode 2',
                                  u'O-QPSK rate mode 3']}

time_mod = {
    u'FSK operating mode 1 FEC': 106, u'FSK operating mode 2 FEC': 54, u'FSK operating mode 3 FEC': 29,
    u'FSK operating mode 1 no FEC': 55, u'FSK operating mode 2 no FEC': 29, u'FSK operating mode 3 no FEC': 17,
    u'OFDM Option 1 MCS 0': 30, u'OFDM Option 1 MCS 1': 17, u'OFDM Option 1 MCS 2': 11, u'OFDM Option 1 MCS 3': 8,
    u'OFDM Option 2 MCS 0': 56, u'OFDM Option 2 MCS 1': 30, u'OFDM Option 2 MCS 2': 18, u'OFDM Option 2 MCS 3': 11,
    u'OFDM Option 2 MCS 4': 9, u'OFDM Option 2 MCS 5': 9, u'OFDM Option 3 MCS 1': 56, u'OFDM Option 3 MCS 2': 30,
    u'OFDM Option 3 MCS 3': 18, u'OFDM Option 3 MCS 4': 13, u'OFDM Option 3 MCS 5': 11, u'OFDM Option 3 MCS 6': 9,
    u'OFDM Option 4 MCS 2': 56, u'OFDM Option 4 MCS 3': 30, u'OFDM Option 4 MCS 4': 22, u'OFDM Option 4 MCS 5': 18,
    u'OFDM Option 4 MCS 6': 13, u'O-QPSK rate mode 0': 450, u'O-QPSK rate mode 1': 230, u'O-QPSK rate mode 2': 122,
    u'O-QPSK rate mode 3': 67
}

test_settings = {
    u'FSK operating mode 1 FEC':
        {'frequency set up': radio_freq_setup[u'fsk operating mode 1'], 'configuration': defs.fsk_option1_FEC,
         'time': time_mod[u'FSK operating mode 1 FEC'], 'id': 'FSK operating mode 1 FEC'},
    u'FSK operating mode 2 FEC':
        {'frequency set up': radio_freq_setup[u'fsk operating mode 2'], 'configuration': defs.fsk_option2_FEC,
         'time': time_mod[u'FSK operating mode 2 FEC'], 'id': 'FSK operating mode 2 FEC'},
    u'FSK operating mode 3 FEC':
        {'frequency set up': radio_freq_setup[u'fsk operating mode 3'], 'configuration': defs.fsk_option3_FEC,
         'time': time_mod[u'FSK operating mode 3 FEC'], 'id': 'FSK operating mode 3 FEC'},
    u'FSK operating mode 1 no FEC':
        {'frequency set up': radio_freq_setup[u'fsk operating mode 1'], 'configuration': defs.fsk_option1,
         'time': time_mod[u'FSK operating mode 1 no FEC'], 'id': 'FSK operating mode 1 no FEC'},
    u'FSK operating mode 2 no FEC':
        {'frequency set up': radio_freq_setup[u'fsk operating mode 2'], 'configuration': defs.fsk_option2,
         'time': time_mod[u'FSK operating mode 2 no FEC'], 'id': 'FSK operating mode 2 no FEC'},
    u'FSK operating mode 3 no FEC':
        {'frequency set up': radio_freq_setup[u'fsk operating mode 3'], 'configuration': defs.fsk_option3,
         'time': time_mod[u'FSK operating mode 3 no FEC'], 'id': 'FSK operating mode 3 no FEC'},
    u'OFDM Option 1 MCS 0':
        {'frequency set up': radio_freq_setup[u'ofdm option 1'], 'configuration': defs.ofdm_1_mcs0,
         'time': time_mod[u'OFDM Option 1 MCS 0'], 'id': 'OFDM Option 1 MCS 0'},
    u'OFDM Option 1 MCS 1':
        {'frequency set up': radio_freq_setup[u'ofdm option 1'], 'configuration': defs.ofdm_1_mcs1,
         'time': time_mod[u'OFDM Option 1 MCS 1'], 'id': 'OFDM Option 1 MCS 1'},
    u'OFDM Option 1 MCS 2':
        {'frequency set up': radio_freq_setup[u'ofdm option 1'], 'configuration': defs.ofdm_1_mcs2,
         'time': time_mod[u'OFDM Option 1 MCS 2'], 'id': 'OFDM Option 1 MCS 2'},
    u'OFDM Option 1 MCS 3':
        {'frequency set up': radio_freq_setup[u'ofdm option 1'], 'configuration': defs.ofdm_1_mcs3,
         'time': time_mod[u'OFDM Option 1 MCS 3'], 'id': 'OFDM Option 1 MCS 3'},
    u'OFDM Option 2 MCS 0':
        {'frequency set up': radio_freq_setup[u'ofdm option 2'], 'configuration': defs.ofdm_2_mcs0,
         'time': time_mod[u'OFDM Option 2 MCS 0'], 'id': 'OFDM Option 2 MCS 0'},
    u'OFDM Option 2 MCS 1':
        {'frequency set up': radio_freq_setup[u'ofdm option 2'], 'configuration': defs.ofdm_2_mcs1,
         'time': time_mod[u'OFDM Option 2 MCS 1'], 'id': 'OFDM Option 2 MCS 1'},
    u'OFDM Option 2 MCS 2':
        {'frequency set up': radio_freq_setup[u'ofdm option 2'], 'configuration': defs.ofdm_2_mcs2,
         'time': time_mod[u'OFDM Option 2 MCS 2'], 'id': 'OFDM Option 2 MCS 2'},
    u'OFDM Option 2 MCS 3':
        {'frequency set up': radio_freq_setup[u'ofdm option 2'], 'configuration': defs.ofdm_2_mcs3,
         'time': time_mod[u'OFDM Option 2 MCS 3'], 'id': 'OFDM Option 2 MCS 3'},
    u'OFDM Option 2 MCS 4':
        {'frequency set up': radio_freq_setup[u'ofdm option 2'], 'configuration': defs.ofdm_2_mcs4,
         'time': time_mod[u'OFDM Option 2 MCS 4'], 'id': 'OFDM Option 2 MCS 4'},
    u'OFDM Option 2 MCS 5':
        {'frequency set up': radio_freq_setup[u'ofdm option 2'], 'configuration': defs.ofdm_2_mcs5,
         'time': time_mod[u'OFDM Option 2 MCS 5'], 'id': 'OFDM Option 2 MCS 5'},
    u'OFDM Option 3 MCS 1':
        {'frequency set up': radio_freq_setup[u'ofdm option 3'], 'configuration': defs.ofdm_3_mcs1,
         'time': time_mod[u'OFDM Option 3 MCS 1'], 'id': 'OFDM Option 3 MCS 1'},
    u'OFDM Option 3 MCS 2':
        {'frequency set up': radio_freq_setup[u'ofdm option 3'], 'configuration': defs.ofdm_3_mcs2,
         'time': time_mod[u'OFDM Option 3 MCS 2'], 'id': 'OFDM Option 3 MCS 2'},
    u'OFDM Option 3 MCS 3':
        {'frequency set up': radio_freq_setup[u'ofdm option 3'], 'configuration': defs.ofdm_3_mcs3,
         'time': time_mod[u'OFDM Option 3 MCS 3'], 'id': 'OFDM Option 3 MCS 3'},
    u'OFDM Option 3 MCS 4':
        {'frequency set up': radio_freq_setup[u'ofdm option 3'], 'configuration': defs.ofdm_3_mcs4,
         'time': time_mod[u'OFDM Option 3 MCS 4'], 'id': 'OFDM Option 3 MCS 4'},
    u'OFDM Option 3 MCS 5':
        {'frequency set up': radio_freq_setup[u'ofdm option 3'], 'configuration': defs.ofdm_3_mcs5,
         'time': time_mod[u'OFDM Option 3 MCS 5'], 'id': 'OFDM Option 3 MCS 5'},
    u'OFDM Option 3 MCS 6':
        {'frequency set up': radio_freq_setup[u'ofdm option 3'], 'configuration': defs.ofdm_3_mcs6,
         'time': time_mod[u'OFDM Option 3 MCS 6'], 'id': 'OFDM Option 3 MCS 6'},
    u'OFDM Option 4 MCS 2':
        {'frequency set up': radio_freq_setup[u'ofdm option 4'], 'configuration': defs.ofdm_4_mcs2,
         'time': time_mod[u'OFDM Option 4 MCS 2'], 'id': 'OFDM Option 4 MCS 2'},
    u'OFDM Option 4 MCS 3':
        {'frequency set up': radio_freq_setup[u'ofdm option 4'], 'configuration': defs.ofdm_4_mcs3,
         'time': time_mod[u'OFDM Option 4 MCS 3'], 'id': 'OFDM Option 4 MCS 3'},
    u'OFDM Option 4 MCS 4':
        {'frequency set up': radio_freq_setup[u'ofdm option 4'], 'configuration': defs.ofdm_4_mcs4,
         'time': time_mod[u'OFDM Option 4 MCS 4'], 'id': 'OFDM Option 4 MCS 4'},
    u'OFDM Option 4 MCS 5':
        {'frequency set up': radio_freq_setup[u'ofdm option 4'], 'configuration': defs.ofdm_4_mcs5,
         'time': time_mod[u'OFDM Option 4 MCS 5'], 'id': 'OFDM Option 4 MCS 5'},
    u'OFDM Option 4 MCS 6':
        {'frequency set up': radio_freq_setup[u'ofdm option 4'], 'configuration': defs.ofdm_4_mcs6,
         'time': time_mod[u'OFDM Option 4 MCS 6'], 'id': 'OFDM Option 4 MCS 6'},
    u'O-QPSK rate mode 0':
        {'frequency set up': radio_freq_setup[u'o-qpsk'], 'configuration': defs.oqpsk_rate0,
         'time': time_mod[u'O-QPSK rate mode 0'], 'id': 'O-QPSK rate mode 0'},
    u'O-QPSK rate mode 1':
        {'frequency set up': radio_freq_setup[u'o-qpsk'], 'configuration': defs.oqpsk_rate1,
         'time': time_mod[u'O-QPSK rate mode 1'], 'id': 'O-QPSK rate mode 1'},
    u'O-QPSK rate mode 2':
        {'frequency set up': radio_freq_setup[u'o-qpsk'], 'configuration': defs.oqpsk_rate2,
         'time': time_mod[u'O-QPSK rate mode 2'], 'id': 'O-QPSK rate mode 2'},
    u'O-QPSK rate mode 3':
        {'frequency set up': radio_freq_setup[u'o-qpsk'], 'configuration': defs.oqpsk_rate3,
         'time': time_mod[u'O-QPSK rate mode 3'], 'id': 'O-QPSK rate mode 3'},
}
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
