

import time

import board

import adafruit_dht

# Initial the dht device, with data pin connected to:
dhtDevice = adafruit_dht.DHT22(board.D22)

# you can pass DHT22 use_pulseio=False if you wouldn't like to use pulseio.
# This may be necessary on a Linux single board computer like the Raspberry Pi,
# but it will not work in CircuitPython.
# dhtDevice = adafruit_dht.DHT22(board.D18, use_pulseio=False)


EMULATED = False

def read_temperature() -> float:
    if EMULATED:
        # TODO: Check GPIO pins
        return random.uniform(15.0, 25.0)
    else:
        try:
            return dhtDevice.temperature
        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            print(error.args[0])
            time.sleep(2.0)
        except Exception as error:
            dhtDevice.exit()
            raise error

def read_humidity() -> float:
    if EMULATED:
        # TODO: Check GPIO pins
        return random.uniform(0.0, 100.0)
    else:
        try:
            return dhtDevice.humidity
        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            print(error.args[0])
            time.sleep(2.0)
        except Exception as error:
            dhtDevice.exit()
            raise error


def test_driver():
    while True:
        try:
            # Print the values to the serial port
            temperature_c = dhtDevice.temperature
            humidity = dhtDevice.humidity
            temperature_f = temperature_c * (9 / 5) + 32
            print(f"Temp: {temperature_f:.1f} F / {temperature_c:.1f} C    Humidity: {humidity}% ")
            continue
        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            print(error.args[0])
            time.sleep(2.0)
        except Exception as error:
            dhtDevice.exit()
            raise error

        time.sleep(2.0)


if __name__ == "__name__":
    test_driver()