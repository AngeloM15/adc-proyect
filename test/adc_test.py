import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.ads1x15 import Mode
from adafruit_ads1x15.analog_in import AnalogIn

# Data collection setup
RATE = 3300
SAMPLES = 1000

# Create the I2C bus with a fast frequency
# NOTE: Your device may not respect the frequency setting
#       Raspberry Pis must change this in /boot/config.txt

i2c = busio.I2C(board.SCL, board.SDA, frequency=1000000)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)

# Create single-ended input on channel 0
chan0 = AnalogIn(ads, ADS.P0)

# ADC Configuration
ads.mode = Mode.CONTINUOUS
ads.data_rate = RATE

while True:
    print(chan0.value, chan0.voltage)
    time.sleep(1)