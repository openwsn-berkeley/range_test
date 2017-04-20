# range_test
This project has been created to be launched at boot time under the Supervisor client/server system.

You could also run the experiment for either the Tx or Rx part from your console. To do so, go to the location where the repository has been downloaded (e.g. /home/pi/range_test/raspberry) and run the following command:
'''
sudo python raspberryPi_tx.py
'''
for the Tx part of the experiment and 
'''
sudo python raspberryPi_rx.py
'''
for the Rx part. 

Once the scripts have been run, the Rpi's will be waiting for the user to press the start button.

There are 6 LEDs. One of them is the start LED, which will be on to indicate that the experiment is starting the next minute.

When the start button is pressed before the 50th second of the current minute, the experiment will be start the following minute. If not, the experiment will start at the current minute + 2. 

For example:
If the start button is pressed at 15:44:55, the experiment is scheduled to 15:46:00. So the start LED will be lighted just from 15:45:00. If the start button is pressed at 15:44:30, the experiment will start at 15:45:00 and the start LED will be on from that moment until the start of the experiment.  

The code will schedule a new experiment right after having finished the current one. 