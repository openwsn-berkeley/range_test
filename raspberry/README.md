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

# button

## meaning

* pressing at boot: start the experiment
* pressing when experiment running: restart experiment

An experiment starts at the at the next minute transition after button press.
Example: button pressed at 15:44:30, experiment starts at 15:45:00.

Exception: if button pressed less than 10s before minute transition, start alternate minute.
Example: button pressed at 15:44:55, experiment starts at 15:46:00

## pinout

See https://az835927.vo.msecnd.net/sites/iot/Resources/images/PinMappings/RP2_Pinout.png

Button connected to pin 13.

# LEDs

## meaning

* start LED: on between moment button is pressed and moment experiment starts
* 5 additional LEDs: binary counter of the active radio setting

## pinout

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
