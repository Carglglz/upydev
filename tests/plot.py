#!/usr/bin/env python3

import json
from matplotlib import pyplot as plt
import sys

file = sys.argv[1]

with open(file, 'r') as rp:
    report = json.load(rp)

data = report['benchmarks'][0]['stats']['data']
time_stamp = report['benchmarks'][0]['extra_info']['vtime']
# from absolute timestamps in ns to relative time in seconds
t_vec = [(t-time_stamp[0])/1e9 for t in time_stamp]

plt.plot(t_vec, data)
plt.ylabel("Voltage ($V$)")
plt.xlabel("Time ($s$)")
plt.show()
