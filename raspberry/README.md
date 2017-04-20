# starting

Tx side:

```
sudo python raspberryPi_tx.py
```

Rx side:

```
sudo python raspberryPi_rx.py
```

Once the scripts are running, the rPi waits for the user to press the start button.

Note: on the rPi, `supervisor` starts the scripts automatically.

# LEDs

## meaning

* start LED: on to indicate the experiment is starting at the next minute transition; off when started
    * When the start button is pressed before the 50th second of the current minute, the experiment starts the following minute
    * If not, the experiment starts at current minute + 2
    * example 1: start button pressed at 15:44:30, experiment starts at 15:45:00
    * example 2: start button pressed at 15:44:55, experiment starts at 15:46:00
* 5 additional LEDs: binary counter of the active radio setting

## pinout

See https://az835927.vo.msecnd.net/sites/iot/Resources/images/PinMappings/RP2_Pinout.png

| LED name   | rPi pin(s)                           |
| ---------- | ------------------------------------ |
| start      | pin 36                               |
| counter    | pins 29 (lsb), 31, 33, 35, 37 (msb)  |

```
---------- pin
         |
        ###
        ### 330 Ohm resistor
        ###
         |
        ###
        ### LED
        ###
         |
---------- GND

```
