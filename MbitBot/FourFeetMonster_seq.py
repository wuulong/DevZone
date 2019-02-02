#MbitBot Four Feet Monster sequencer example
#Features:
#   using non-block ( no sleep ) mode to drive servo
#Functions:
#   correction, move_forward
#hardware setup:
#   follow these instruction
#       https://www.makerlab.tw/blog/microbitqleggedrobot
#       https://www.makerlab.tw/blog/microbitxmbitbotqleggedrobottwo
#LICENSE: MIT
#Author: WuLung Hsu, wuulong@gmail.com
#product information: https://www.icshop.com.tw/product_info.php/products_id/26934
#document: https://paper.dropbox.com/doc/MbitBot--AWrnCMJxYCI1Po2IXs6ndVYiAg-DG5SSj5zQhBv1CoAgDtAG

from microbit import *
import utime
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
        self.s_cur = [0,180,90,90,90,90,0,180]
        self.seqs = []
        self.reset_seq = [[1,0],[2,180],[3,90],[4,90],[5,90],[6,90],[7,0],[8,180],[0,100000]]
        self.time_s = utime.ticks_us()
        self.cur_sleep = 0

    def myservo(self,pin,angle):
            if angle<0:
                angle=0
            if angle>180:
                angle=180
            self.s_cur[pin-1] = angle
            servo(pin,angle)
    #command sequence definition
    #[servo_id (1-8), value]
    #[0, wait_us ]
    def seq_proc(self):
        time_now = utime.ticks_us()
        time_use = utime.ticks_diff(time_now,self.time_s)
        if self.cur_sleep - time_use <0:
            self.cur_sleep = 0
            if len(self.seqs)>0:
                cur_cmd = self.seqs[0]
                #print(cur_cmd)
                if cur_cmd[0]==0: # sleep cmd
                    self.cur_sleep = cur_cmd[1]
                    self.time_s = time_now
                else:
                    self.myservo(cur_cmd[0],cur_cmd[1])
                del self.seqs[0]
    def correction(self):
        display.show("C")
        self.seqs.extend(self.reset_seq)

    def move_forward(self):
        wait_unit = 1000000
        self.seqs.extend([[5,136],[8,120],[0,wait_unit],[6,46],[0,wait_unit],[8,180]]) #1
        self.seqs.extend([[7,60],[0,wait_unit],[5,60],[0,wait_unit],[7,0]]) #2
        self.seqs.extend([[3,120],[4,46],[5,90],[6,90],[0,wait_unit]]) #3
        self.seqs.extend([[1,60],[0,wait_unit],[3,136],[0,wait_unit],[1,0],[0,wait_unit]]) #4
        self.seqs.extend([[2,120],[0,wait_unit],[4,120],[0,wait_unit],[2,180],[0,wait_unit]]) #5
        self.seqs.extend([[3,90],[4,90],[5,136],[6,120],[0,wait_unit]]) #6

ffm = FourFeetMonster()
display.show("C")
ffm.correction()
cur_start = 0
cmd_break = False
while True:
    if button_a.was_pressed():
        ffm.seqs = []
        ffm.correction()
        cmd_break = True
    ffm.seq_proc()
    if len(ffm.seqs)==0:
        if cmd_break:
            break
        ffm.move_forward()
        if 0:
            #range_test
            v = cur_start/2
            ffm.seqs.extend([[1,v],[7,v],[2,180-v],[8,180-v],[0,10000]])
            if cur_start %2 ==0:
                v = cur_start/4
                ffm.seqs.extend([[3,135-v],[4,45+v],[5,135-v],[6,45+v],[0,10000]])
            cur_start = cur_start +1
            if cur_start >=361:
                cur_start = 0