# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time

import board

import adafruit_dht

# Initial the dht device, with data pin connected to:
devs = [ adafruit_dht.DHT22(board.D17), 
adafruit_dht.DHT22(board.D22),
adafruit_dht.DHT22(board.D27),
]

# you can pass DHT22 use_pulseio=False if you wouldn't like to use pulseio.
# This may be necessary on a Linux single board computer like the Raspberry Pi,
# but it will not work in CircuitPython.
# dhtDevice = adafruit_dht.DHT22(board.D18, use_pulseio=False)

while True:
    temp = ["?","?","?"]
    hum  = ["?","?","?"]
    for i, d in enumerate(devs):
        try:
            temp[i] = d.temperature
            hum[i] = d.temperature

            # Print the values to the serial port
            #temperature_c = d.temperature
            #humidity = dhtDevice.humidity

        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            # print(error.args[0])
            # time.sleep(2.0)
            continue
        except Exception as error:
            # dhtDevice.exit()
            # dhtDevice1.exit()
            # dhtDevice2.exit()
            raise error
    print(f"PIN D17 Temp: {temp[0]} C    Humidity: {hum[0]}% ")
    print(f"PIN D22       {temp[1]} C              {hum[1]}% ")
    print(f"PIN D27       {temp[2]} C              {hum[2]}% ")

    time.sleep(2.0)

# import gpiod 
# import time 
# LED_PIN = 17 
# chip = gpiod.Chip('/dev/gpiochip4') 
# led_line = chip.get_line(LED_PIN) 
# led_line.request(consumer="LED",type=gpiod.LINE_REQ_DIR_OUT)
# 
# try: 
#   while True: 
#     led_line.set_value(1) 
#     time.sleep(1) 
#     led_line.set_value(0) 
#     time.sleep(1)
# 
# finally: 
#     led_line.release()


#import RPi.GPIO as GPIO
#
#GPIO.setmode(GPIO.BOARD)
#
#GPIO.setup(4, GPIO.IN)
#
## Switch on
##GPIO.output(26, GPIO.HIGH)
#
## To read the state
#while True:
#    state = GPIO.input(4)
#    if state:
#        print('on')
#    else:
#        print('off')