"""
Lists of frequencies and modulations to be used in the range test.

\author Jonathan Munoz (jonathan.munoz@inria.fr), January 2017
"""

#FIXME: change to .json file

import at86rf215_defs as defs
import json

frame_lengths = [8, 127, 1000, 2047]
BURST_SIZE    = 100

'''
time between frames
FIXME change name
'''
IFS = {
    # frame length IFS seconds
    8:             0.0020,
    127:           0.0030,
    1000:          0.0050,
    2047:          0.0065,
}

radio_settings = [
    #(channel_spacing, frequency_0, channel)
    (             200,      863125,       0),  # fsk operating mode 1
    (             400,      863225,       0),  # fsk operating mode 2
    (             400,      863225,       0),  # fsk operating mode 3
    #(             200,      863125,       0),  # fsk operating mode 1
    #(             400,      863225,       0),  # fsk operating mode 2
    #(             400,      863225,       0),  # fsk operating mode 3
    (            1200,      863625,       0),  # ofdm option 1 MCS 0
    (            1200,      863625,       0),  # ofdm option 1 MCS 1
    (            1200,      863625,       0),  # ofdm option 1 MCS 2
    (            1200,      863625,       0),  # ofdm option 1 MCS 3
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
    'fsk operating mode 1': ( 200, 863125, 0),
    'fsk operating mode 2': ( 400, 863225, 0),
    'fsk operating mode 3': ( 400, 863225, 0),
    'ofdm option 1':        (1200, 863625, 0),
    'ofdm option 2':        ( 800, 863425, 0),
    'ofdm option 3':        ( 400, 863225, 0),
    'ofdm option 4':        ( 200, 863125, 0),
    'o-qpsk':               ( 600, 868300, 0),
}

radio_trx_mod_order = [
    'FSK operating mode 1 FEC',
    'FSK operating mode 2 FEC',
    'FSK operating mode 3 FEC',
    'FSK operating mode 1 no FEC',
    'FSK operating mode 2 no FEC',
    'FSK operating mode 3 no FEC',
    'OFDM Option 1 MCS 0',
    'OFDM Option 1 MCS 1', u'OFDM Option 1 MCS 2',
                                  u'OFDM Option 1 MCS 3', u'OFDM Option 2 MCS 0', u'OFDM Option 2 MCS 1',
                                  u'OFDM Option 2 MCS 2', u'OFDM Option 2 MCS 3', u'OFDM Option 2 MCS 4',
                                  u'OFDM Option 2 MCS 5', u'OFDM Option 3 MCS 1', u'OFDM Option 3 MCS 2',
                                  u'OFDM Option 3 MCS 3', u'OFDM Option 3 MCS 4', u'OFDM Option 3 MCS 5',
                                  u'OFDM Option 3 MCS 6', u'OFDM Option 4 MCS 2', u'OFDM Option 4 MCS 3',
                                  u'OFDM Option 4 MCS 4', u'OFDM Option 4 MCS 5', u'OFDM Option 4 MCS 6',
                                  u'O-QPSK rate mode 0', u'O-QPSK rate mode 1', u'O-QPSK rate mode 2',
                                  u'O-QPSK rate mode 3']

time_mod = {
    u'FSK operating mode 1 FEC': 106,
    u'FSK operating mode 2 FEC': 54,
    u'FSK operating mode 3 FEC': 29,
    u'FSK operating mode 1 no FEC': 55,
    u'FSK operating mode 2 no FEC': 29,
    u'FSK operating mode 3 no FEC': 17,
    u'OFDM Option 1 MCS 0': 30,
    u'OFDM Option 1 MCS 1': 17,
    u'OFDM Option 1 MCS 2': 11,
    u'OFDM Option 1 MCS 3': 8,
    u'OFDM Option 2 MCS 0': 56,
    u'OFDM Option 2 MCS 1': 30,
    u'OFDM Option 2 MCS 2': 18,
    u'OFDM Option 2 MCS 3': 11,
    u'OFDM Option 2 MCS 4': 9,
    u'OFDM Option 2 MCS 5': 9,
    u'OFDM Option 3 MCS 1': 56,
    u'OFDM Option 3 MCS 2': 30,
    u'OFDM Option 3 MCS 3': 18,
    u'OFDM Option 3 MCS 4': 13,
    u'OFDM Option 3 MCS 5': 11,
    u'OFDM Option 3 MCS 6': 9,
    u'OFDM Option 4 MCS 2': 56,
    u'OFDM Option 4 MCS 3': 30,
    u'OFDM Option 4 MCS 4': 22,
    u'OFDM Option 4 MCS 5': 18,
    u'OFDM Option 4 MCS 6': 13,
    u'O-QPSK rate mode 0': 450,
    u'O-QPSK rate mode 1': 230,
    u'O-QPSK rate mode 2': 122,
    u'O-QPSK rate mode 3': 67
}

test_settings = [
    {'channel_spacing_kHz': 200, 'frequency_0_kHz': 863125, 'channel': 0, 'modulation': defs.fsk_option1_FEC, 'numframes': BURST_SIZE, 'durationtx_s': 106},
    {'channel_spacing_kHz': 400, 'frequency_0_kHz': 863225, 'channel': 0, 'modulation': defs.fsk_option2_FEC, 'numframes': BURST_SIZE, 'durationtx_s': 54},
    {'channel_spacing_kHz': 400, 'frequency_0_kHz': 863225, 'channel': 0, 'modulation': defs.fsk_option3_FEC, 'numframes': BURST_SIZE, 'durationtx_s': 29},
    {'channel_spacing_kHz': 200, 'frequency_0_kHz': 863125, 'channel': 0, 'modulation': defs.fsk_option1, 'numframes': BURST_SIZE, 'durationtx_s': 55},
    {'channel_spacing_kHz': 400, 'frequency_0_kHz': 863225, 'channel': 0, 'modulation': defs.fsk_option2, 'numframes': BURST_SIZE, 'durationtx_s': 29},
    {'channel_spacing_kHz': 400, 'frequency_0_kHz': 863225, 'channel': 0, 'modulation': defs.fsk_option3, 'numframes': BURST_SIZE, 'durationtx_s': 17},
    {'channel_spacing_kHz': 1200, 'frequency_0_kHz': 863625, 'channel': 0, 'modulation': defs.ofdm_1_mcs0, 'numframes': BURST_SIZE, 'durationtx_s': 30},
    {'channel_spacing_kHz': 1200, 'frequency_0_kHz': 863625, 'channel': 0, 'modulation': defs.ofdm_1_mcs1, 'numframes': BURST_SIZE, 'durationtx_s': 17},
    {'channel_spacing_kHz': 1200, 'frequency_0_kHz': 863625, 'channel': 0, 'modulation': defs.ofdm_1_mcs2, 'numframes': BURST_SIZE, 'durationtx_s': 11},
    {'channel_spacing_kHz': 1200, 'frequency_0_kHz': 863625, 'channel': 0, 'modulation': defs.ofdm_1_mcs3, 'numframes': BURST_SIZE, 'durationtx_s': 8},
    {'channel_spacing_kHz': 800, 'frequency_0_kHz': 863425, 'channel': 0, 'modulation': defs.ofdm_2_mcs0, 'numframes': BURST_SIZE, 'durationtx_s': 56},
    {'channel_spacing_kHz': 800, 'frequency_0_kHz': 863425, 'channel': 0, 'modulation': defs.ofdm_2_mcs1, 'numframes': BURST_SIZE, 'durationtx_s': 30},
    {'channel_spacing_kHz': 800, 'frequency_0_kHz': 863425, 'channel': 0, 'modulation': defs.ofdm_2_mcs2, 'numframes': BURST_SIZE, 'durationtx_s': 18},
    {'channel_spacing_kHz': 800, 'frequency_0_kHz': 863425, 'channel': 0, 'modulation': defs.ofdm_2_mcs3, 'numframes': BURST_SIZE, 'durationtx_s': 11},
    {'channel_spacing_kHz': 800, 'frequency_0_kHz': 863425, 'channel': 0, 'modulation': defs.ofdm_2_mcs4, 'numframes': BURST_SIZE, 'durationtx_s': 9},
    {'channel_spacing_kHz': 800, 'frequency_0_kHz': 863425, 'channel': 0, 'modulation': defs.ofdm_2_mcs5, 'numframes': BURST_SIZE, 'durationtx_s': 9},
    {'channel_spacing_kHz': 400, 'frequency_0_kHz': 863225, 'channel': 0, 'modulation': defs.ofdm_3_mcs1, 'numframes': BURST_SIZE, 'durationtx_s': 56},
    {'channel_spacing_kHz': 400, 'frequency_0_kHz': 863225, 'channel': 0, 'modulation': defs.ofdm_3_mcs2, 'numframes': BURST_SIZE, 'durationtx_s': 30},
    {'channel_spacing_kHz': 400, 'frequency_0_kHz': 863225, 'channel': 0, 'modulation': defs.ofdm_3_mcs3, 'numframes': BURST_SIZE, 'durationtx_s': 18},
    {'channel_spacing_kHz': 400, 'frequency_0_kHz': 863225, 'channel': 0, 'modulation': defs.ofdm_3_mcs4, 'numframes': BURST_SIZE, 'durationtx_s': 13},
    {'channel_spacing_kHz': 400, 'frequency_0_kHz': 863225, 'channel': 0, 'modulation': defs.ofdm_3_mcs5, 'numframes': BURST_SIZE, 'durationtx_s': 11},
    {'channel_spacing_kHz': 400, 'frequency_0_kHz': 863225, 'channel': 0, 'modulation': defs.ofdm_3_mcs6, 'numframes': BURST_SIZE, 'durationtx_s': 9},
    {'channel_spacing_kHz': 200, 'frequency_0_kHz': 863125, 'channel': 0, 'modulation': defs.ofdm_4_mcs2, 'numframes': BURST_SIZE, 'durationtx_s': 56},
    {'channel_spacing_kHz': 200, 'frequency_0_kHz': 863125, 'channel': 0, 'modulation': defs.ofdm_4_mcs3, 'numframes': BURST_SIZE, 'durationtx_s': 30},
    {'channel_spacing_kHz': 200, 'frequency_0_kHz': 863125, 'channel': 0, 'modulation': defs.ofdm_4_mcs4, 'numframes': BURST_SIZE, 'durationtx_s': 22},
    {'channel_spacing_kHz': 200, 'frequency_0_kHz': 863125, 'channel': 0, 'modulation': defs.ofdm_4_mcs5, 'numframes': BURST_SIZE, 'durationtx_s': 18},
    {'channel_spacing_kHz': 200, 'frequency_0_kHz': 863125, 'channel': 0, 'modulation': defs.ofdm_4_mcs6, 'numframes': BURST_SIZE, 'durationtx_s': 13},
    {'channel_spacing_kHz': 600, 'frequency_0_kHz': 868300, 'channel': 0, 'modulation': defs.oqpsk_rate0, 'numframes': BURST_SIZE, 'durationtx_s': 450},
    {'channel_spacing_kHz': 600, 'frequency_0_kHz': 868300, 'channel': 0, 'modulation': defs.oqpsk_rate1, 'numframes': BURST_SIZE, 'durationtx_s': 230},
    {'channel_spacing_kHz': 600, 'frequency_0_kHz': 868300, 'channel': 0, 'modulation': defs.oqpsk_rate2, 'numframes': BURST_SIZE, 'durationtx_s': 122},
    {'channel_spacing_kHz': 600, 'frequency_0_kHz': 868300, 'channel': 0, 'modulation': defs.oqpsk_rate3, 'numframes': BURST_SIZE, 'durationtx_s': 67}
]
"""
d = [t['channel'] for channel in test_settings.items()]
d = test_settings.keys()

for test_setting in test_settings:
   one_run(**test_setting)
   
def one_run(channel_spacing_kHz=None, frequency_0_kHz=None, channel=None, modulation=None, numframes=None, durationtx_s=None):
    pass

"""
