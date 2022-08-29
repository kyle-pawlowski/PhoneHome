# -*- coding: utf-8 -*-
"""
Created on Sat Apr 16 17:23:01 2022

@author: Pawlowski
"""


import subprocess
import os
import signal
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

    # set up GPIO pins
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(hook_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(led_pin, GPIO.OUT)
    GPIO.output(led_pin, GPIO.LOW)

def rx_pickup(channel):
    global record_thread
    if GPIO.input(hook_pin): # rising edge
        GPIO.output(led_pin, GPIO.LOW)
        print("on the hook!")
        if not record_thread is None:
            #record_thread.stdin.close()
            print(record_thread.pid)
            record_thread.send_signal(signal.SIGINT)
            record_thread.terminate()
            record_thread.terminate()
            record_thread.wait(timeout=5)
    else: #falling edge
        GPIO.output(led_pin, GPIO.HIGH)
        print("off the hook!")
        record_message()
    
def rx_hangup(channel):
    GPIO.output(led_pin, GPIO.LOW)

def record_message():
    global record_thread
    folder = 'recorded'
    filename = 'msg'
    num = 0
    for _,_,files in os.walk(folder):
        for file in files:
            if filename in file:
                num += 1
    filename = folder + '/' + filename + str(num) + '.wav'
    
    record_thread = subprocess.Popen('arecord -t wav -f cd '+filename, stdin=subprocess.PIPE, shell=True)
    print(record_thread.pid)
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
    
