import threading
import RPi.GPIO as GPIO
import time
import logging
import sys


class GPIO_handler(object):
    def __init__(self, radio_isr_pin=11, push_button_pin=13, cb_pin_11=None, cb_pin_13=None):

        self.radio_isr_pin = radio_isr_pin
        self.push_button_pin = push_button_pin
        self.cb_pin_11 = cb_pin_11
        self.cb_pin_13 = cb_pin_13
        self.dataLock = threading.RLock()
        self.toggle_LED = False
        self.f_reset_pin = False

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(radio_isr_pin, GPIO.IN)
        GPIO.setup(push_button_pin, GPIO.IN)
        GPIO.add_event_detect(radio_isr_pin, GPIO.RISING, callback=self.cb_pin_11)
        GPIO.add_event_detect(push_button_pin, GPIO.BOTH, callback=self.cb_pin_13, bouncetime=500)

        logging.basicConfig(stream=sys.__stdout__, level=logging.DEBUG)

    def init_binary_pins(self, array):
        """
        It initialises the set of pins for the binary counter
        :param array: set of pins where a LED + resistor are connected.
        :return: nothing
        """
        for pin in array:
            GPIO.setup(pin, GPIO.OUT)
            self.led_off(pin)

    def binary_counter(self, number, array):
        """
        it switches on the LEDs according to the number, binary system.
        :param number: The number to be shown in binary
        :param array: amount of LEDs available
        :return: light :)
        """
        for index in range(0, len(array)):
            GPIO.output(array[index], GPIO.LOW)

        # LED_val = [0 for i in range(0, len(array))]
        for index in range(0, len(array)):
            LED = number >> index
            if LED & 1:
                GPIO.output(array[index], GPIO.HIGH)

    def led_on(self, pin):
        GPIO.output(pin, GPIO.HIGH)

    def led_off(self, pin):
        GPIO.output(pin, GPIO.LOW)

    def led_toggle(self, pin):
        if self.toggle_LED is False:
            self.toggle_LED = True
            GPIO.output(pin, GPIO.HIGH)
        else:
            self.toggle_LED = False
            GPIO.output(pin, GPIO.LOW)

    def read_reset_pin(self):
        with self.dataLock:
            return self.f_reset_pin

    def clean_reset_pin(self):
        with self.dataLock:
            self.f_reset_pin = False

    def clear_cb(self, channel):
        GPIO.remove_event_detect(channel)

    def add_cb(self, cb, channel):
        GPIO.add_event_detect(channel, GPIO.FALLING, callback=cb, bouncetime=500)

    def clean_gpio(self):
        GPIO.cleanup()  # clean exit


