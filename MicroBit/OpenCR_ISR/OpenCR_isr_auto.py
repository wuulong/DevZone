#ISR performance binary search auto tester by micro:bit
#features:
#   use user-defined waveform to test controller ISR performance
#   report max speed ISR can handle(depends on ISR signal reported)
#   microbit use binary search to test OpenCR ISR
#   fake mode to test argorithm without OpenCR
#test case: OpenCR
#Usage:
#   button_a pressed to start 1 search test
#   FS - microbit(P0) - EXTI_0( 0: Arduino PIN 2,   EXTI_0)
#   PASS - microbit(P1) - EXTI_1( 0: Arduino PIN 3,   EXTI_1)
#   INT - microbit(P2) - EXTI_2( 0: Arduino PIN 4,   EXTI_2)
#Default:
#   search_max_speed(0,5000,10,False)
#   100Hz to max speed, step is 20us
#
#LICENSE: MIT
#Author: WuLung Hsu, wuulong@gmail.com
# doc: https://paper.dropbox.com/doc/FBTUG-FarmHarvestBot-OpenCR--AXheYDmXaKg~v7I1J1WYgFB7Ag-KKIOxeWkjnEwHyJZ51GUU#:uid=329885975022421369607500&h2=%E5%AF%A6%E9%A9%97-1.4---%E6%B8%AC%E8%A9%A6-Max-ISR-rate
from microbit import *
import utime
import random

def_cnt =1000
#sleep_us: (0) max speed, (>0) sleep delay us
def outclock_bycnt_delay(target_cnt,sleep_us):
    test_cnt = 0
    if sleep_us>0:
        while True:
            if test_cnt == target_cnt:
                break
            pin2.write_digital(1)
            utime.sleep_us(sleep_us)
            pin2.write_digital(0)
            utime.sleep_us(sleep_us)
            test_cnt +=1
    else:
        while True:
            if test_cnt == target_cnt:
                break
            pin2.write_digital(1)
            pin2.write_digital(0)
            test_cnt +=1

#min_us: minimal sleep delay, unit us, 0 mean max speed
#max_us: max sleep delay , unit us
#step: search minimal step
#fake: (0)- not fake, normal (1)-fake mode
#return: [PASS/Fail,selected delay(us),speed(Hz)]
#usage: both min_us,max_us % step == 0 , delay parameters used in sleep between signal change, 1 clock need 2 sleep
#ex: search_max_speed(0,5000,100,0)
def search_max_speed(min_us,max_us,step,fake):
    global def_cnt
    if (min_us) % step or (max_us % step):
        return [False,0,0]
    range_cur = [min_us,0,max_us]
    if fake:
        tested = [0,-1, 1]#[0,-1, 1]
    else:
        tested = [ -1,-1,-1 ] # 0 : fail, 1: pass, -1: not test yet
    rate = [0,0,0]
    speed = 0
    rate_cur = -1
    while True:#[0,0,1], [0,1,0]
        middle = int((range_cur[0] + range_cur[2] )/2)
        middle = int(middle/step)*step
        print("middle=%i"%(middle))
        range_cur[1] = middle
        tested[1] = -1
        if tested[0]>=0 and tested[2]>=0:
            if middle == range_cur[0] or middle == range_cur[2]: #not need more test
                return [True,range_cur[2],rate[2]]


        for i in range(3): #[1,-1,-1], [0,1,-1], [0,0,1],[0,0,0]
            if tested[i] == -1:
                time_start = utime.ticks_us()
                pin0.write_digital(1)
                outclock_bycnt_delay(def_cnt,range_cur[i])
                if pin1.read_digital()==1: # no response
                    display.show("X")
                    return [False,0,0]

                pin0.write_digital(0)
                time_end = utime.ticks_us()
                print("(%i)"%(range_cur[i]))
                time_used = time_end - time_start
                rate[i] = def_cnt* (1000000/time_used)
                sleep(10)
                result1 = pin1.read_digital()
                if fake:
                    result1 = random.randint(0, 2) % 2 # random 1/2
                print("result1=%i"%(result1))
                if result1==1:
                    tested[i] = 1
                    display.show("1")
                    rate_cur = range_cur[i]
                    break
                else:
                    tested[i] = 0
                    display.show("0")

        #prepare next
        if tested[0]==1: #min_us pass
            return [True, range_cur[0],rate[0] ]
        if tested[2] == 0: # min_us fail
            return [False, range_cur[2],rate[2] ]

        if tested[1]==1:
            range_cur[2] = range_cur[1]
            rate[2] = rate[1]
            tested[2] = 1
        else:
            range_cur[0] = range_cur[1]
            tested[0] = 0
            rate[0] = rate[1]




pin0.write_digital(0)
while True:
    if button_a.was_pressed():
        display.show("S")
        ok,delay,speed = search_max_speed(0,5000,10,False)
        print("ok=%i,delay=%i,speed=%f"%(ok,delay,speed))
        display.show("E")


