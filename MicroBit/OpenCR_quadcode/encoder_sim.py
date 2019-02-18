# motor encoder simulator
#features:
#   simulate 2-bit quadrature-encoded rotary encoder
#   support clockwise, counterclockwise, delay setting
#   per-clock show to LED for debug purpose
#test case: OpenCR
#Usage: button_a to start
#Default: max speed with cnt = 1000 , CW 1000 times + 1000 CCW times
#LICENSE: MIT
#Author: WuLung Hsu, wuulong@gmail.com
# doc: https://paper.dropbox.com/doc/MbitBot--AXygciMpkj~Tsk6AdFTEKGtsAg-DG5SSj5zQhBv1CoAgDtAG#:uid=925566654150854768396062&h2=Encoder-tool
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

#P0,P1
#sleep_us as us
def QuadOnePluse(clockwise,sleep_us):
    if clockwise:
        pin0.write_digital(1)
        utime.sleep_us(sleep_us)
        pin1.write_digital(1)
        utime.sleep_us(sleep_us)
        pin0.write_digital(0)
        utime.sleep_us(sleep_us)
        pin1.write_digital(0)
        utime.sleep_us(sleep_us)
    else:
        pin1.write_digital(1)
        utime.sleep_us(sleep_us)
        pin0.write_digital(1)
        utime.sleep_us(sleep_us)
        pin1.write_digital(0)
        utime.sleep_us(sleep_us)
        pin0.write_digital(0)
        utime.sleep_us(sleep_us)

def test_by_cnt_delay(target_cnt,sleep_us):
    test_cnt = 0
    while True:
        if test_cnt == target_cnt:
            break
        QuadOnePluse(True,sleep_us)
        test_cnt +=1
        #pixel_debug(0,test_cnt)
    sleep(1000)
    while True:
        if test_cnt == 0:
            break
        QuadOnePluse(False,sleep_us)
        test_cnt -=1
        #pixel_debug(0,test_cnt)

pin0.write_digital(0)
pin1.write_digital(0)
while True:
    if button_a.was_pressed():
        #display.show("S")
        #test_by_cnt_delay(100,int(100000/4))
        test_by_cnt_delay(1000,0)
        #display.show("E")

