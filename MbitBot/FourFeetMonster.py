#MbitBot Four Feet Monster move forward example
#Features:
#   move forward
#Functions:
#   correction, range_test, posture,move_forward_bysteps
#hardware setup:
#   follow these instruction
#       https://www.makerlab.tw/blog/microbitqleggedrobot
#       https://www.makerlab.tw/blog/microbitxmbitbotqleggedrobottwo
#Usage:
#   Button-A: stop
#LICENSE: MIT
#Author: WuLung Hsu, wuulong@gmail.com
#product information: https://www.icshop.com.tw/product_info.php/products_id/26934
#document: https://paper.dropbox.com/doc/MbitBot--AWrnCMJxYCI1Po2IXs6ndVYiAg-DG5SSj5zQhBv1CoAgDtAG
from microbit import *

#library
def mymap(x, in_min, in_max, out_min, out_max):
    value = int((x-in_min) * (out_max-out_min) / (in_max-in_min) + out_min)
    if value>= out_max:
        value = out_max -1
    elif value < out_min:
        value = out_min

    return value

#board related
def i2c_init():
    import struct

    buf1=struct.pack('>H', 16)
    buf2=struct.pack('>H', 254 * 256 + 123)
    buf3=struct.pack('>H', 0)
    i2c.write(64, buf1)
    i2c.write(64, buf2)
    i2c.write(64, buf3)
    pass

#ex: servo(1,90)
def servo(Spin, Sangle):
    import struct
    K = 4096 / 20
    StartBit = 0.5 * K
    FullScaleBit = 1.94 * K
    TS1 = int((Sangle / 180 * FullScaleBit + StartBit) % 256)
    TS2 = int((Sangle / 180 * FullScaleBit + StartBit) / 256)
    CH = (Spin - 1) * 4 + 8
    CH1 = int((CH <<8) + TS1)
    CH2 = int(((CH + 1) <<8) + TS2)
    buf1=struct.pack('>H', CH1)
    buf2=struct.pack('>H', CH2)
    i2c.write(64, buf1)
    i2c.write(64, buf2)
    print("%i,%i" %(Spin,Sangle))

#micro:bit related
#ex: set_color((10,0,0),(0,0,0),(0,0,10),(10,10,10))
def set_color(cled1,cled2,cled3,cled4):
    import neopixel
    np = neopixel.NeoPixel(pin12, 4)
    np[0] = cled1
    np[1] = cled2
    np[2] = cled3
    np[3] = cled4
    np.show()

class FourFeetMonster():
    def __init__(self):
        i2c_init()
        set_color((0,0,0),(0,0,0),(0,0,0),(0,0,0))
        self.t_start = [45,135,45,135]
        self.t_dir = [ 1,-1,1,-1 ]
        self.t_dir2 = [1,1,-1,-1]
        self.b_id = [1,2,7,8]
        self.b_start = [0,180,0,180]
        self.b_dir = [1,-1,1,-1]
        self.px_cur = 2
        self.py_cur = 2


    def correction(self):
        display.show("C")
        servo(1,0)
        servo(2,180)
        servo(3,90)
        servo(4,90)
        servo(5,90)
        servo(6,90)
        servo(7,0)
        servo(8,180)
    def range_test(self):
        step = 10

        for i in range(0,181,10):
            servo(1,i)
            servo(7,i)
            servo(2,180-i)
            servo(8,180-i)
            sleep(1000)
        for i in range(0,91,10):
            servo(3,135-i)
            servo(4,45+i)
            servo(5,135-i)
            servo(6,45+i)
            sleep(1000)
    # top: 1: all y 2: all_x 3: 90 degree
    # bottom: 4: stand 11: 5 degree 6: flat
    def posture(self,pos_id):
        if pos_id == 1:
            for i in range(4):
                servo(3+i, self.t_start[i])
        if pos_id == 2:
            for i in range(4):
                value = self.t_start[i] + 90 * self.t_dir[i]
                servo(3+i, value)
        if pos_id == 3:
            for i in range(4):
                value = self.t_start[i] + 45 * self.t_dir[i]
                servo(3+i, value)
        if pos_id == 4:
            for i in range(4):
                value = self.b_start[i]
                servo(self.b_id[i], value)
        if pos_id == 5:
            for i in range(4):
                value = self.b_start[i] + 45 * self.b_dir[i]
                servo(self.b_id[i], value)
        if pos_id == 6:
            for i in range(4):
                value = self.b_start[i] + 90 * self.b_dir[i]
                servo(self.b_id[i], value)
    def feed_step(self,bid):
        servo(self.b_id[bid],self.b_start[bid]+20*self.b_dir[bid])
        sleep(100)
        value = 90 + 22* self.t_dir2[bid]
        servo(3+bid,value)
        sleep(100)
        servo(self.b_id[bid],self.b_start[bid])
        sleep(100)
        value = 90 - 22* self.t_dir2[bid]
        servo(3+bid,value)
        sleep(100)



    def move_forward_bysteps(self,step_id):
        display.show(str(step_id))
        if step_id==1:
            servo(5,135)
            servo(8,120)
            sleep(100)
            servo(6,45)
            sleep(100)
            servo(8,180)
        if step_id==2:
            servo(7,60)
            sleep(100)
            servo(5,60)
            sleep(100)
            servo(7,0)
        if step_id==3:
            servo(3,120)
            servo(4,45)
            servo(5,90)
            servo(6,90)
            sleep(100)
        if step_id==4:
            servo(1,60)
            sleep(100)
            servo(3,135)
            sleep(100)
            servo(1,0)
            sleep(100)
        if step_id==5:
            servo(2,120)
            sleep(100)
            servo(4,120)
            sleep(100)
            servo(2,180)
            sleep(100)
        if step_id==6:
            servo(3,90)
            servo(4,90)
            servo(5,135)
            servo(6,120)
            sleep(100)


ffm = FourFeetMonster()
ffm.correction()
sleep(1000)
step = 0

while True:
    if button_a.was_pressed():
        ffm.correction()

    for j in range(6):
        display.show(str(j+1))
        ffm.move_forward_bysteps(j+1)