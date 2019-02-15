#ISR manual test by micro:bit
#features:
#   generate clocks with test count and selected delay
#test case: OpenCR
#Usage:
#   button_a to start
#   microbit(P0) - EXTI_0( 0: Arduino PIN 2,   EXTI_0)
#LICENSE: MIT
#Author: WuLung Hsu, wuulong@gmail.com
# doc: https://paper.dropbox.com/doc/FBTUG-FarmHarvestBot-OpenCR--AXheYDmXaKg~v7I1J1WYgFB7Ag-KKIOxeWkjnEwHyJZ51GUU#:uid=924235342742563082008563&h2=%E5%AF%A6%E9%A9%97-1.1---%E7%94%A8-micro-bit-%E9%96%93%E7%B0%A1%E5%96%AE%E6%B8%AC%E8%A9%A6-Ope
from microbit import *
import utime

def pixel_debug(part,value):
    if part==1: # 1 LED at bottom-right
        value = value % 10
        display.set_pixel(4, 4, value)
    else: #4 LED
        value = value % 40
        for i in range(4):
            if value >=9:
               display.set_pixel(i, 4, 9)
            elif value<0:
                display.set_pixel(i, 4, 0)
            else:
               display.set_pixel(i, 4, value)
            value -=10


while True:
    if button_a.was_pressed():
        test_cnt = 0
        display.show("S")
        while True:
            if test_cnt == 1000:
                break
            pin0.write_digital(1)
            #sleep(1)
            pin0.write_digital(0)
            #sleep(1)
            test_cnt +=1
        display.show("E")

    #pixel_debug(0,test_cnt/10)