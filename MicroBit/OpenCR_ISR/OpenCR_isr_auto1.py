#ISR performance auto tester by micro:bit
#features:
#   use user-defined waveform to test controller ISR performance
#   user select target_cnt and delay parameters
#test case: OpenCR
#Usage:
#   button_a pressed to start test, test pass show "1", fail show "0"
#   FS - microbit(P0) - EXTI_0( 0: Arduino PIN 2,   EXTI_0)
#   PASS - microbit(P1) - EXTI_1( 0: Arduino PIN 3,   EXTI_1)
#   INT - microbit(P2) - EXTI_2( 0: Arduino PIN 4,   EXTI_2)
#LICENSE: MIT
#Author: WuLung Hsu, wuulong@gmail.com
# doc: https://paper.dropbox.com/doc/FBTUG-FarmHarvestBot-OpenCR--AXheYDmXaKg~v7I1J1WYgFB7Ag-KKIOxeWkjnEwHyJZ51GUU#:uid=044033165837223902265584&h2=%E5%AF%A6%E9%A9%97-1.2---%E8%87%AA%E5%8B%95%E6%B8%AC%E8%A9%A6-Interrupt-1000-%E6%AC%A1
from microbit import *
import utime

#sleep_ms: (0) max speed, (>0) sleep delay ms
def outclock_bycnt_speed(target_cnt,sleep_ms):
    test_cnt = 0
    if sleep_ms>0:
        while True:
            if test_cnt == target_cnt:
                break
            pin2.write_digital(1)
            sleep(sleep_ms)
            pin2.write_digital(0)
            sleep(sleep_ms)
            test_cnt +=1
    else:
        while True:
            if test_cnt == target_cnt:
                break
            pin2.write_digital(1)
            pin2.write_digital(0)
            test_cnt +=1


pin0.write_digital(0)
while True:
    if button_a.was_pressed():
        display.show("S")
        pin0.write_digital(1)
        outclock_bycnt_speed(1000,0)
        pin0.write_digital(0)
        display.show("E")
        sleep(10)
        if pin1.read_digital()==1:
            display.show("1")
        else:
            display.show("0")
