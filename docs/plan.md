A program which shows display for temperature and humidity.

The program works on raspberry PI and reads GPIO pins for values.

There are two pages. Swipe left and right to switch.

# Front page - Graphs
There is one diagram with two graphs with colored temperature and humidity.

There is also a number for temp and humid showing latest readings.

Zooming in and out to one hour span, 1 minute span to see details
- Reset zoom to default (7 days)

# Second page 
It's a touch display with one digram with two colored graphcs for temperature and humidity.

You can swipe to the right for settings:
- Change diagram value range temp and humid (15 C - 25 C, 0 - 10 humidity) (0-100% is range of relative humidity)
- Toggle for sleep mode which turns off screen to save power and screens lifetime when no user input for 10 minutes.
- Option to choose delay until sleep mode.
- Change reading rate. Also need to reformat data since data points assumes a reading rate.


# Internal functionality
Data is written to a file every minute. If raspberry PI shutsdown then data is kept. very nice.

Settings on second page are written to file upon change.

Data is a sequence of float numbers per reading. Each reading has a measure rate which specifies time per data point.
When changing read rate we need to reformat it. We could always use 1 second for each data point and then fill it out data if
we only read data from sensor every minute. But what's the point of changing rate if it's fixed when we store it. Might as well
read every second then. So yes we should reformat.

If we get more than 7d 1h worth of data points we trim it to 7 days.


# Extra
Do we need to validity check the readings within expected ranges and ignore values outside?
If we read invalid value we reuse previous value. We can also keep a counter of read invalid values for each sensor. We errors on the second page.

If you press ESC (when a keyboard is connected) the program shutsdown (we may want to show a prompt, "are you sure"). If using Raspberry PI OS Lite then you'll see a terminal. Run the program to start it again.


UI must be obvious. There should not be a need for a help screen.

Maybe a screen to the left for CPU temp and uptime or something.
