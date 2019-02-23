#Microbit distance test by radio signal
#   Using receive radio signal to estimate distance between Tx/Rx
#Usage: button_a: Tx, button_b: Rx
#Output:
#   Rx LED: 10cm per led, from top to down, from left to right
#   print("(%02.2f,%i)"%(rssi_avg,cm))
#LICENSE: MIT
#Author: WuLung Hsu, wuulong@gmail.com
#Document: https://paper.dropbox.com/doc/Untitled--AYHc5bnpWd3MOFGm7~4S6Lp3Ag-DG5SSj5zQhBv1CoAgDtAG#:uid=203767515920607812540844&h2=%E7%9C%8B-radio-signal-strength-%E8%88%87%E8%B7%9D%E9%9B%A2%E7%9A%84%E9%97%9C%E4%BF%82
from microbit import *
import radio
import utime

def mymap(x, in_min, in_max, out_min, out_max):
    value = int((x-in_min) * (out_max-out_min) / (in_max-in_min) + out_min)
    if value>= out_max:
        value = out_max -1
    elif value < out_min:
        value = out_min

    return value
def pixel_debug(value):
    for j in range(5):
        for i in range(5):
            if value >=9:
               display.set_pixel(i, j, 9)
            elif value<0:
                display.set_pixel(i, j, 0)
            else:
               display.set_pixel(i, j, value)
            value -=10


#calibrate by match any record in the range table
def calibrate_by_offset(cm_m, rssi_m):
    global range_ref
    diff = 0
    for i in range(len(range_ref)):
        [cm,rssi] = range_ref[i]
        if cm_m == cm:
            diff = rssi_m - rssi
            break
    for i in range(len(range_ref)):
        range_ref[i][1] = range_ref[i][1] + diff


def estimate_distance(rssi_m,range_ref):
    max_i = 0
    min_i = 0
    if rssi_m>=range_ref[0][1]:
       return 0
    if rssi_m <= range_ref[len(range_ref)-1][1]:
        return range_ref[-1][0]
    for i in range(len(range_ref)):
        [cm,rssi] = range_ref[i]
        if rssi_m >= rssi:
            max_i = i
            break
        else:
            min_i = i
    return mymap(rssi_m,range_ref[min_i][1],range_ref[max_i][1],range_ref[min_i][0],range_ref[max_i][0])



def test_estimate():
    while True:
        for i in range(-65,-94,-1):
            value = estimate_distance(i,range_ref)
            print("%f->%i"%(i,value))
        sleep(10000)


cal_cm=50
cal_rssi=-76.0

range_ref = [
    [ 0   , -65.2 ],
    [ 10  , -66.0 ],
    [ 20  , -69.1 ],
    [ 30  , -71.0 ],
    [ 40  , -73.0 ],
    [ 50  , -76.0 ],
    [ 75  , -77.0 ],
    [ 100 , -79.0 ],
    [ 125 , -82.0 ],
    [ 150 , -84.6 ],
    [ 200 , -87.6 ],
    [ 250 , -90.0 ],
    [ 300 , -93.7 ]]

radio.on()
radio.config(queue=6,address=0x75626973,channel=5,data_rate=radio.RATE_1MBIT,power=0)

sleep(100)

calibrate_by_offset(cal_cm,cal_rssi)

mode = 0
avg_cnt = 100 #100
while True:
    if button_a.was_pressed():
        display.show("T")
        mode = 1
        break
    if button_b.was_pressed():
        display.show("R")
        mode = 2
        break
#measurement
while True:
    if mode ==1: #Tx
        radio.send("1")
        sleep(100)
    else: #Rx
        values = []
        while True:
            details = radio.receive_full()
            if details:
                [msg, rssi, timestamp] = details
                values.append(rssi)
            if len(values)>=avg_cnt:
                break

        rssi_avg = sum(values)/avg_cnt
        cm = estimate_distance(rssi_avg,range_ref)
        pixel_debug(cm)
        print("(%02.2f,%i)"%(rssi_avg,cm))