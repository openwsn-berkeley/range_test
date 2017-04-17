import os
import pynmea2
import serial
import threading
import time

# =========================== classes =========================================


class GpsThread(threading.Thread):
    
    SERIAL_PORT        = '/dev/ttyS0'
    SERIAL_BAUDRATE    = 9600
    SYSTIMESYNCPERIOD  = 60 # sec
    
    def __init__(self):
        
        # Initialize the Thread class
        threading.Thread.__init__(self)
        self.name                 = 'GpsThread'
        
        # local variables
        self.cmd_output           = True
        self.tsLastSysTimeSync    = 0
        self.serial               = None
        self.update_counter       = 0

        # start myself
        self.start()
    
    def run(self):
        # connect to serial port of the GPS
        self.serial = serial.Serial(self.SERIAL_PORT, self.SERIAL_BAUDRATE)
        
        gpsData = {}
        
        while True:
            # each second, the GPS module prints >5 lines over it serial port, containing the
            # same info, but formatted differently. This loop merges the info contained in the
            # GGA and RMC formats, then calls self._handleGpsData()
            
            # read a line from the GPS
            line = self.serial.readline()
            
            # extract GGA messages "essential fix data which provide 3D location and accuracy data".
            # See http://www.gpsinformation.org/dale/nmea.htm#GGA.
            # raw string from serial:
            #   $GPGGA,143432.000,4850.5490,N,00223.0651,E,1,04,4.6,96.7,M,47.3,M,,0000*61
            # fields:
            #   - age_gps_data        :
            #   * lon_dir             :E
            #   * timestamp           :143432.000
            #   - altitude            :96.7
            #   * lon                 :00223.0651
            #   - gps_qual            :1
            #   - ref_station_id      :0000
            #   - geo_sep_units       :M
            #   - num_sats            :04
            #   - altitude_units      :M
            #   - geo_sep             :47.3
            #   * lat                 :4850.5490
            #   - horizontal_dil      :4.6
            #   * lat_dir             :N
            if line.startswith("$GPGGA"):
                gpsData = {}
                try:
                    message = pynmea2.parse(line)
                except Exception as err:
                    print err
                    continue
                else:
                    if not message.is_valid:
                       continue
                    for n in message.name_to_idx.keys():
                        gpsData[n] = getattr(message,n)
            
            # Extract RMC "recommended minimum data for gps" messages
            # http://www.gpsinformation.org/dale/nmea.htm#RMC
            # raw string from serial:
            #    $GPRMC,143432.000,A,4850.5490,N,00223.0651,E,2.21,261.63,270616,,,A*68
            # fields:
            #    - status              :A
            #    - true_course         :261.63
            #    * lon_dir             :E
            #    * timestamp           :143432.000
            #    - mag_variation       :
            #    * lon                 :00223.0651
            #    - mag_var_dir         :
            #    - datestamp           :270616
            #    * lat                 :4850.5490
            #    - spd_over_grnd       :2.21
            #    * lat_dir             :N
            if line.startswith("$GPRMC"):
                try:
                    message = pynmea2.parse(line)
                except Exception as err:
                    print err
                    gpsData = {}
                    continue
                else:
                    if not message.is_valid:
                       gpsData = {}
                       continue
                    if not gpsData:
                       gpsData = {}
                       continue
                    
                    same = True
                    for i in ['lon_dir','timestamp','lon','lat','lat_dir']:
                        if getattr(message,i)!=gpsData[i]:
                            same = False
                    if not same:
                        gpsData = {}
                        continue
                    
                    for (n,i) in message.name_to_idx.items():
                        gpsData[n] = message.data[i]
                    
                    self._handleGpsData(gpsData)
                    gpsData = {}
    
    # ======================= private =========================================
    
    def _handleGpsData(self,gpsData):
        """
        gpsData contains the union of the GGA and RMC formats. Example:
        {
            'status': 'A',
            'geo_sep_units': 'M',
            'true_course': '325.47',
            'datestamp': '270616',
            'lon_dir': 'E',
            'timestamp': '151411.000',
            'altitude': 95.0,
            'lon': '00223.0662',
            'gps_qual': 1,
            'lat_dir': 'N',
            'mag_var_dir': '',
            'lat': '4850.5661',
            'age_gps_data': '',
            'num_sats': '04',
            'ref_station_id': '0000',
            'geo_sep': '47.3',
            'horizontal_dil': '2.6',
            'spd_over_grnd': '1.03',
            'altitude_units': 'M', 
            'mag_variation': '',
        }
        """
        
        # log
        # self.logger.writeLine(
        #     type   = JsonFileLogger.JsonFileLogger.TYPE_GPSDATA,
        #     params = gpsData,
        # )
        
        # reset system time
        now = time.time()
        if now-self.tsLastSysTimeSync>self.SYSTIMESYNCPERIOD:
            self._syncSysTime(gpsData['datestamp'],gpsData['timestamp'])
            self.tsLastSysTimeSync = now

    def format_unix_date(self, datestamp, timestamp):
        """
        datestamp: '270616' (string)
        timestamp: '152912.000'  (string)
        returnVal: "2016-06-27 15:29:12"
        """

        day = datestamp[0:2]
        month = datestamp[2:4]
        year = datestamp[4:6]
        # if year == 17:
        #     with self.dataLock:
        #         self.f_gps_time = True

        timestamp = timestamp.split('.')[0]
        hour = timestamp[0:2]
        minute = timestamp[2:4]
        second = timestamp[4:6]

        return "20{YEAR}-{MONTH}-{DAY} {HOUR}:{MINUTE}:{SECOND}".format(
            DAY=day,
            MONTH=month,
            YEAR=year,
            HOUR=hour,
            MINUTE=minute,
            SECOND=second,
        )
    
    # == parsing
    
    def _syncSysTime(self, datestamp,timestamp):
        unixData = self.format_unix_date(datestamp, timestamp)
        os.system('date --s "{0}"'.format(unixData))
        print 'System time set to {0}'.format(unixData)

# =========================== main ============================================

def main():
    gpsThread = GpsThread()

if __name__=="__main__":
    main()
