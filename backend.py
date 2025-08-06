#########################
#   Backend DATA code
#########################

import random, os, math
from datetime import datetime

def max_temperature() -> float:
    return 25.0

def min_temperature() -> float:
    return 15.0

def max_humidity() -> float:
    return 100.0

def min_humidity() -> float:
    return 0.0

def read_temperature() -> float:
    # TODO: Check GPIO pins
    return random.uniform(15.0, 25.0)

def read_humidity() -> float:
    # TODO: Check GPIO pins
    return random.uniform(0.0, 100.0)

temp_data = []
temp_last_timestamp_ms = 0
temp_rate = 1.0

humid_data = []
humid_last_timestamp_ms = 0
humid_rate = 1.0

def add_temp(temp_value):
    global temp_data
    global temp_last_timestamp_ms

    # this implementation is awful because the caller has to ensure
    # that they call add_temp continously with the same delay.
    now = int(datetime.now().timestamp() * 1000)
    delta = now - temp_last_timestamp_ms
    if delta < 1000:
        # called too soon
        temp_data.append(temp_value)
        temp_last_timestamp_ms = now
    else:
        temp_data.append(temp_value)
        temp_last_timestamp_ms = now

def add_humid(humid_value):
    global humid_data
    global humid_last_timestamp_ms

    # this implementation is awful because the caller has to ensure
    # that they call add_temp continously with the same delay.
    now = int(datetime.now().timestamp() * 1000)
    delta = now - humid_last_timestamp_ms
    if delta < 1000:
        # called too soon
        humid_data.append(humid_value)
        humid_last_timestamp_ms = now
    else:
        humid_data.append(humid_value)
        humid_last_timestamp_ms = now

# retrieve slice of data points
# offset_seconds is reversed where 0 means last point is included
# 1 means last point is skipped, 2 means the two last points are skipped (assumming rate is 1 second per point)
def slice_temperature_points(offset_seconds, time_span_seconds, rate_seconds):
    global temp_rate
    global temp_data

    num_out_points = math.ceil((time_span_seconds+0.5) / rate_seconds)
    out_points = [ 0 ] * num_out_points

    src_head = math.ceil(len(temp_data)-1 + offset_seconds / temp_rate)
    dst_head = num_out_points-1
    while dst_head >= 0:
        def clamp(ind):
            global temp_rate
            global temp_data
            return math.floor(max(0, min(ind, len(temp_data)-1)))

        val0 = temp_data[clamp(src_head-1)]
        val1 = temp_data[clamp(src_head)]
        val = (val0+val1)/2
        ind = dst_head * rate_seconds
        # print(dst_head, len(out_points))
        out_points[dst_head] = (ind, val)
        dst_head -= 1
        src_head -= temp_rate

    # print(out_points)
    return out_points

def slice_humidity_points(offset_seconds, time_span_seconds, rate_seconds):
    global humid_rate
    global humid_data

    num_out_points = math.ceil((time_span_seconds+0.5) / rate_seconds)
    out_points = [ 0 ] * num_out_points

    src_head = math.ceil(len(humid_data)-1 + offset_seconds / humid_rate)
    dst_head = num_out_points-1
    while dst_head >= 0:
        def clamp(ind):
            global humid_rate
            global humid_data
            return math.floor(max(0, min(ind, len(humid_data)-1)))

        val0 = humid_data[clamp(src_head-1)]
        val1 = humid_data[clamp(src_head)]
        val = (val0+val1)/2
        ind = dst_head * rate_seconds
        # print(dst_head, len(out_points))
        out_points[dst_head] = (ind, val)
        dst_head -= 1
        src_head -= humid_rate

    # print(out_points)
    return out_points

def save_data():
    # TODO: add version
    global temp_data
    global temp_last_timestamp_ms
    global temp_rate
    global humid_data
    global humid_last_timestamp_ms
    global humid_rate

    path = "data/temp.txt"

    print(f"Saving {path}") # TODO: Log to a file

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w") as f:
        # TODO: Binary format
        f.write("# temperature timestamp of last data point (milliseconds since epoch)\n")
        f.write(f"{temp_last_timestamp_ms}\n")
        f.write("# temperature rate (seconds per data point)\n")
        f.write(f"{temp_rate}\n")
        f.write(f"# temperature data points\n")
        f.write(f"{len(temp_data)}\n")
        for i, v in enumerate(temp_data):
            f.write(f"{v}\n")
        f.write(f"# humidity data points\n")
        f.write(f"{len(humid_data)}\n")
        for i, v in enumerate(humid_data):
            f.write(f"{v}\n")

    return True

def load_data():
    # TODO: add version
    global temp_last_timestamp_ms
    global temp_data
    global temp_rate
    global humid_last_timestamp_ms
    global humid_data
    global humid_rate

    path = "data/temp.txt"
    if not os.path.exists(path):
        # no data
        return False
    
    # TODO: Binary format
    with open(path, "r") as f:
        text = f.read()

    lines = [ s for s in text.split("\n") if len(s) > 0 and s[0] != "#" ]
    
    temp_last_timestamp_ms = int(lines[0])
    humid_last_timestamp_ms = temp_last_timestamp_ms
    temp_rate = float(lines[1])
    humid_rate = temp_rate
    temp_count = int(lines[2])
    temp_data = [ float(line) for line in lines[3:3+temp_count] ]
    humid_count = int(lines[3+temp_count])
    humid_data = [ float(line) for line in lines[3+temp_count + 1:] ]
    return True

class Config():
    def __init__(self):
        self.ymin = 0
        self.ymax = 40
        self.warn_period = 30 # min
        self.warn_level = 30
        self.rate = 1 # second

config = Config()

def save_config():
    global config
    path = "data/config.txt"
    with open(path, "w") as f:
        f.write(f"# y-min\n")
        f.write(f"{math.floor(config.ymin)}\n")
        f.write(f"# y-max\n")
        f.write(f"{math.floor(config.ymax)}\n")
        f.write(f"# warn period\n")
        f.write(f"{math.floor(config.warn_period)}\n")
        f.write(f"# warn level\n")
        f.write(f"{math.floor(config.warn_level)}\n")
        f.write(f"# read rate\n")
        f.write(f"{config.rate}\n")
    return True

def load_config():
    global config
    path = "data/config.txt"
    if not os.path.exists(path):
        return False
    
    with open(path, "r") as f:
        text = f.read()
        
    lines = [line for line in text.split("\n") if len(line) > 0 and line[0] != "#" ]
    
    config.ymin = int(lines[0])
    config.ymin = int(lines[1])
    config.warn_period = int(lines[2])
    config.warn_level = int(lines[3])
    config.rate = float(lines[4])

    return True

def get_config():
    return config