# -*- coding: utf-8 -*-
"""
Created on Sat Apr 16 17:23:01 2022

@author: Pawlowski
"""


import subprocess
from multiprocessing import Process, Event
import os
import signal
import pyaudio
import wave
import warnings
from threading import Thread
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
    if GPIO.input(hook_pin): # rising edge
        GPIO.output(led_pin, GPIO.LOW)
        print("on the hook!")
        try:
            if rx_pickup.thread_handle.is_alive():
                rx_pickup.stop_event.set()
                rx_pickup.thread_handle.join() # waits for thread to finish
                rx_pickup.stop_event.clear()
        except AttributeError:
            pass 
    else: #falling edge
        GPIO.output(led_pin, GPIO.HIGH)
        print("off the hook!")
        rx_pickup.stop_event = Event()
        rx_pickup.stop_event.clear()
        rx_pickup.thread_handle = record_thread(rx_pickup.stop_event) # starts thread
    
def rx_hangup(channel):
    GPIO.output(led_pin, GPIO.LOW)

''' this function starts recording audio and saves
to the next available filename after a Ctrl+C signal
is received'''
def record_message(stop_event):
    play_file('test_answer.wav')
    print('finished playing audio!')
    folder = 'recorded'
    filename = 'msg'

    #find available file name
    num = 0
    for _,_,files in os.walk(folder):
        for file in files:
            if filename in file:
                num += 1
    filename = folder + '/' + filename + str(num) + '.wav'

    frames = [] #create list for audio data

    #pyaudio settings
    sample_format = pyaudio.paInt16
    chunk_size = 1024
    nchannels = 1
    fs = 44100

    # open pyaudio interface
    p = pyaudio.PyAudio()
    stream = p.open(format=sample_format,
                    channels= nchannels, 
                    rate= fs, 
                    frames_per_buffer=chunk_size, 
                    input=True)
    
    while not stop_event.is_set():
        data = stream.read(chunk_size)
        frames.append(data)
    
    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(nchannels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

def play_file(filename):
    # Set chunk size of 1024 samples per data frame
    chunk = 65572  

    # Open the sound file 
    wf = wave.open(filename, 'rb')

    # Create an interface to PortAudio
    p = pyaudio.PyAudio()

    # Open a .Stream object to write the WAV file to
    # 'output = True' indicates that the sound will be played rather than recorded
    stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = 44100,
                    frames_per_buffer = chunk,
                    output = True)

    # Read data in chunks
    data = wf.readframes(chunk)

    # Play the sound by writing the audio data to the stream
    while len(data) > 0 and data != '':
        stream.write(data)
        data = wf.readframes(chunk)

    # Close and terminate the stream
    stream.close()
    p.terminate()


def record_thread(stop_event):
    thread_handle = Process(target=record_message, args=(stop_event,))
    thread_handle.start()
    return thread_handle

    
if __name__ == "__main__":
    setup()

    rx_pickup.thread_handle = None
    GPIO.add_event_detect(hook_pin, GPIO.BOTH, callback=rx_pickup, bouncetime=300)
    try:
        while True:
            pass
    except:
        GPIO.cleanup()
    GPIO.cleanup()
    
