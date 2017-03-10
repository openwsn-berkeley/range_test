# range_test
Here lives the code to perform IEEE802.15.4-SUN range test.

IEEE802.15.4g defines 3 PHY, each with a specific modulation FSK, O-QPSK and OFDM. Each of them presents a set of options, giving as a result a total of 31 combinations. 

The range test consists on having at least a couple of nodes, one running a TX program and the other a RX program. All nodes performing the test will loop over all combinations, synchronized by a GPS module, and writing into a file the results of each combination TRX exchange.

The following is an example of what each node will write at the end of each range test combination:

{<br />
    'type'                 'end_of_cycle_rx',<br />
    'version'              1,<br />
    'id'                   'rpi_10',<br />
    'role'                 'RX',<br />
    'radiosettings'        'ofdm_1_mcs0',<br />
    'numframes'            100,<br />
    'starttime_epoch'      1489196635.438927,<br />
    'starttime_string'     '2017-09-04 10:45:21',<br />
    'nmea_at_start'        '$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,47',<br />
    'position_description' None,<br />
    'frequency'            863.625 MHz<br />
    'channel'              0<br />
    'rssi_by_length'       {<br />
        8    [ -95, -98, None, -89, -101, ...], (as many values as numframes)<br />
        127  [ -97, -102, None, -89, -101, ...], (as many values as numframes)<br />
        1000 [ -95, None, None, -89, -101, ...], (as many values as numframes)v
        2047 [ -95, -98, None, -89, -101, ...], (as many values as numframes)<br />
    },<br />
    'rstring'             {<br />
        8    '...............!.......................................................!............................',<br />
        127  '..........................................!.........................................................',<br />
        1000 '.......................!............................................................................',<br />
        2047 '................................................................................!....!..............'<br />
    },<br />
}<br />
    
======

{<br />
    'type'                 'end_of_cycle_tx',<br />
    'version'              1,<br />
    'id'                   'rpi_5',<br />
    'role'                 'TX',<br />
    'radiosettings'        'ofdm_1_mcs0',<br />
    'starttime_epoch'      1489196636.938927,<br />
    'starttime_string'     '2017-09-04 10:45:22',<br />
    'nmea_at_start'        '$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,47',<br />
    'position_description' None,<br />
    'frequency'            863.625 MHz<br />
    'channel'              0<br />
    'numframes'            100,<br />
}<br />