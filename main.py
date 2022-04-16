# -*- coding: utf-8 -*-
"""
Created on Sat Apr 16 17:23:01 2022

@author: Pawlowski
"""


import RPi.GPIO as GPIO
import yaml

hook_pin = 0
led_pin = 0

def get_params(yaml_file):
    params = {}
    try:
        with open(yaml_file, 'r') as file:
            params = yaml.safe_load(file)
    except FileNotFoundError:
        print("There is no yaml file!")
        
    return params
    
def setup():
    # Get configurable parameters from yaml file
    params = get_params('./config.yaml')
    hook_pin = params['HOOK_PIN']
    led_pin = params['LED_PIN']
    
    # set up GPIO pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(hook_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(led_pin, GPIO.IN)
    GPIO.output(led_pin, GPIO.LOW)

def rx_pickup(channel):
    GPIO.output(led_pin, GPIO.HIGH)
    
def rx_hangup(channel):
    GPIO.output(led_pin, GPIO.LOW)
    
if __name__ == "__main__":
    setup()
    
    GPIO.add_event_detect(hook_pin, GPIO.RISING, callback=rx_pickup, bouncetime=300)
    GPIO.add_event_detect(hook_pin, GPIO.FALLING, callback=rx_hangup, bouncetime=300)
    

    
