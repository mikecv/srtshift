#!/usr/bin/env python3

# *******************************************
# Convert time components to fractional seconds.
# *******************************************
def conv2Secs(h, m, s, ms):
    secs = 0.0
    secs += (ms / 1000.0)
    secs += s
    secs += (m * 60.0)
    secs += (h * 3600.0)

    return secs

# *******************************************
# Convert fractional seconds to time components.
# *******************************************
def conv2time(s):
    secs = s
    h = int(secs // 3600)
    secs = secs % 3600
    m = int(secs // 60)
    secs = secs % 60
    s = int(secs // 1)
    ms = int((secs % 1) * 1000)

    return h, m, s, ms

