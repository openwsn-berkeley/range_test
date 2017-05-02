# range_test
Here lives the code to perform IEEE802.15.4-SUN range test.

IEEE802.15.4g defines 3 PHY, each with a specific modulation FSK, O-QPSK and OFDM. Each of them presents a set of options, giving as a result a total of 31 combinations. 

The range test consists on having at least a couple of nodes, one running a TX program and the other a RX program. All nodes performing the test will loop over all combinations, synchronized by a GPS module, and writing into a file the results of each combination TRX exchange.

The following is an example of what each node will write at the end of each range test combination:

```
{
    'type'                 'end_of_cycle_rx',
    'version'              1,
    'id'                   'openpi-9',
    'role'                 'RX',
    'radiosettings'        'ofdm_1_mcs0',
    'numframes'            100,
    'starttime_epoch'      1489196635.438927,
    'starttime_string'     '2017-09-04 10:45:21',
    'GPSinfo_at_start'     {"status": "A", "geo_sep_units": "M", "true_course": "317.77", "datestamp": "200417", "lon_dir": "E",
				"timestamp": "141642.000", "altitude": 15.3, "lon": "00223.0842", "gps_qual": 2, 
				"lat_dir": "N", 	"mag_var_dir": "", "lat": "4850.5432", "age_gps_data": "0000", 
				"num_sats": "09", "ref_station_id": "0000", "geo_sep": "47.3", "horizontal_dil": "0.93", 
				"spd_over_grnd": "0.02", "altitude_units": "M", "mag_variation": ""}
    'position_description' None,
    'frequency'            863.625 MHz
    'channel'              0
    'rssi_by_length'       {
        8    [ -95, -98, None, -89, -101, ...], (as many values as numframes)
        127  [ -97, -102, None, -89, -101, ...], (as many values as numframes)
        1000 [ -95, None, None, -89, -101, ...], (as many values as numframes)
        2047 [ -95, -98, None, -89, -101, ...], (as many values as numframes)
    },
    'rx_string'             {
        8    '...............!.......................................................!............................',
        127  '..........................................!.........................................................',
        1000 '.......................!............................................................................',
        2047 '................................................................................!....!..............'
    },
    'rx_frames': 394
    'rx_frames_wrong_fcs': 3
    'rx_frames_wrong_fcs_sq': [15, 142, 385], 
}
``` 
======

```
{
    'type'                 'end_of_cycle_tx',
    'version'              1,
    'id'                   'openpi-8',
    'role'                 'TX',
    'radiosettings'        'ofdm_1_mcs0',
    'starttime_epoch'      1489196636.938927,
    'starttime_string'     '2017-09-04 10:45:22',
    'nmea_at_start'        {"status": "A", "geo_sep_units": "M", "true_course": "317.77", "datestamp": "200417", "lon_dir": "E",
				"timestamp": "141642.000", "altitude": 15.3, "lon": "00223.0842", "gps_qual": 2, 
				"lat_dir": "N", 	"mag_var_dir": "", "lat": "4850.5432", "age_gps_data": "0000", 
				"num_sats": "09", "ref_station_id": "0000", "geo_sep": "47.3", "horizontal_dil": "0.93", 
				"spd_over_grnd": "0.02", "altitude_units": "M", "mag_variation": ""}
    'position_description' None,
    'frequency'            863.625 MHz
    'channel'              0
    'numframes'            100,
}
```
