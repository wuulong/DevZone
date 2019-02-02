#MbitBot Four Feet Monster balance example
#Features:
#   standup, show current accelerometer information to LEDs, try balance
#   left/right, forward/backward balance
#Functions:
#   acc_to_led, acc_to_feet
#hardware setup:
#   follow these instruction
#       https://www.makerlab.tw/blog/microbitqleggedrobot
#       https://www.makerlab.tw/blog/microbitxmbitbotqleggedrobottwo
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
    #print("%i,%i" %(Spin,Sangle))

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
        self.s_cur = [0,180,90,90,90,90,0,180]
        self.avg_x = 0.0
        self.avg_y = 1000.0
        self.dyn_cnt = 10
        self.flat_cnt = 0

    def myservo(self,pin,angle):
            if angle<0:
                angle=0
            if angle>180:
                angle=180
            self.s_cur[pin-1] = angle
            servo(pin,angle)
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

    def acc_to_led(self):

        [x,y,z ] = accelerometer.get_values()
        px = mymap(x,-400,400,0,5)
        py = mymap(z,-400,400,0,5)

        if self.px_cur != px or self.py_cur != py:
            display.set_pixel(self.px_cur, self.py_cur, 0)
        display.set_pixel(px, py, 9)
        self.px_cur = px
        self.py_cur = py
    def acc_to_feet(self):
        [x,y,z ] = accelerometer.get_values()

        self.avg_x = (self.avg_x * (self.dyn_cnt-1) + x)/self.dyn_cnt
        self.avg_y = (self.avg_y * (self.dyn_cnt-1) + y)/self.dyn_cnt
        print("(%i,%i,%i,%i)"%(x,y,self.avg_x,self.avg_y))
        x = self.avg_x
        y = self.avg_y
        if x>100 or x<-100 or y>1020 or y<980:
            self.flat_cnt=0
            if x>100 :
                self.myservo(7,self.s_cur[7-1]+1)
                self.myservo(8,self.s_cur[8-1]-1)
                self.myservo(1,0)
                self.myservo(2,180)
            elif x< -100:
                self.myservo(1,self.s_cur[1-1]+1)
                self.myservo(2,self.s_cur[2-1]-1)
                self.myservo(7,0)
                self.myservo(8,180)
            elif y > 1000+20:
                self.myservo(1,self.s_cur[1-1]+1)
                self.myservo(8,self.s_cur[8-1]-1)
                self.myservo(7,0)
                self.myservo(2,180)

            elif y < 1000-20:
                self.myservo(7,self.s_cur[7-1]+1)
                self.myservo(2,self.s_cur[2-1]-1)
                self.myservo(1,0)
                self.myservo(8,180)
        else:
            self.flat_cnt+=1

        sleep(10)


ffm = FourFeetMonster()
ffm.correction()
sleep(1000)
display.clear()
while True:
    ffm.acc_to_led()
    ffm.acc_to_feet()
