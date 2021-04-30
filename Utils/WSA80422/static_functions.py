# encoding: UTF-8

"""
Version: 0.2
Updated: 30/04/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON IMPORTS
import math


# TRASFORMA vanes_volt_angle_dict DA dict[str, float] a dict[float, float]
def adjust(configs):
    vanes_volt_angle_dict_v1 = configs["vanes_volt_angle_dict"]
    vanes_volt_angle_dict_v2 = {}
    for key, value in vanes_volt_angle_dict_v1.items():
        vanes_volt_angle_dict_v2[float(key)] = value
    configs["vanes_volt_angle_dict"] = vanes_volt_angle_dict_v2
    return configs


# VOLTAGE DIVIDER
def voltage_divider(r1, r2, v_in):
    v_out = (v_in * r1) / (r1 + r2)
    return round(v_out, 3)


# GET AVERAGE OF ANGLES
def average(angles):
    sin_sum = 0
    cos_sum = 0

    for angle in angles:
        r = math.radians(angle)
        sin_sum += math.sin(r)
        cos_sum += math.cos(r)

    flen = float(len(angles))
    s = sin_sum / flen
    c = cos_sum / flen
    arc = math.degrees(math.atan(s / c))
    avg = 0.0

    if s > 0 and c > 0:
        avg = arc
    elif c < 0:
        avg = arc + 180
    elif s < 0 and c > 0:
        avg = arc + 360

    return 0.0 if avg == 360 else avg
