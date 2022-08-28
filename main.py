# -*- coding: utf-8 -*-
"""
Created on Sat Apr 16 17:23:01 2022

@author: Pawlowski
"""


import subprocess
import os
import RPi.GPIO as GPIO
import yaml

hook_pin = 0
led_pin = 0
record_thread = None

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
    global hook_pin 
    hook_pin = params['HOOK_PIN']
    global led_pin 
    led_pin = params['LED_PIN']
    print("hook_pin: " + str(hook_pin))
    print("led_pin: " + str(led_pin))

    # set up GPIO pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(hook_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(led_pin, GPIO.OUT)
    GPIO.output(led_pin, GPIO.LOW)

def rx_pickup(channel):
    if GPIO.input(hook_pin): # rising edge
        GPIO.output(led_pin, GPIO.HIGH)
        print("off the hook!")
        record_message()
    else: #falling edge
        GPIO.output(led_pin, GPIO.LOW)
        print("on the hook!")
        if not record_thread is None:
            record_thread.terminate()
    
def rx_hangup(channel):
    GPIO.output(led_pin, GPIO.LOW)

def record_message():
    folder = 'recorded'
    filename = 'msg'
    num = 0
    for file in os.walk(folder):
        if filename in file:
            num += 1
    filename = folder + '/' + filename + str(num) + '.wav'
    
    record_thread = subprocess.Popen('arecord -t wav -f cd filename')

    return record_thread
    
if __name__ == "__main__":
    setup()
    
    print("hook_pin: " + str(hook_pin))
    print("led_pin: " + str(led_pin))
    GPIO.add_event_detect(hook_pin, GPIO.BOTH, callback=rx_pickup, bouncetime=300)
    try:
        while True:
            pass
    except:
        GPIO.cleanup()
    GPIO.cleanup()
    
