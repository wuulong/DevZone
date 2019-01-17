#MbitBot python example
#Features:
#   support MbitBot extension board: motor,servo
#   support RGB-led
#LICENSE: MIT
#Author: WuLung Hsu, wuulong@gmail.com
from microbit import *

#library
def mymap(x, in_min, in_max, out_min, out_max):
    return int((x-in_min) * (out_max-out_min) / (in_max-in_min) + out_min)

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

def motor(Spin, Speed):
    import struct
    TM1 = int(Speed % 256)
    TM2 = int(Speed / 256)
    CH = (Spin - 1) * 4 + 8
    CH1 = int((CH <<8) + TM1)
    CH2 = int(((CH + 1) <<8) + TM2)
    buf1=struct.pack('>H', CH1)
    buf2=struct.pack('>H', CH2)
    i2c.write(64, buf1)
    i2c.write(64, buf2)

#ex: move_motor_port(1,100)
def move_motor_port(MPort, usevalue):
    if(usevalue>100):
        usevalue = 100
    if(usevalue<-100):
        usevalue = -100
    dir=0
    #MP2 may have bug
    if MPort==2:
        usevalue=-usevalue

    if usevalue<0:
        usevalue = -usevalue
        dir=1

    usevalue = mymap(usevalue, 0, 100, 0, 4095)		
	
    port_start = [13,15,11,9]
    if dir==0:
        motor(port_start[MPort-1], usevalue)
        motor(port_start[MPort-1]+1, 0)
    else:
        motor(port_start[MPort-1], 0)
        motor(port_start[MPort-1]+1, usevalue)

#ex: set_color((10,0,0),(0,0,0),(0,0,10),(10,10,10))
def set_color(cled1,cled2,cled3,cled4):
    import neopixel
    np = neopixel.NeoPixel(pin12, 4)
    np[0] = cled1
    np[1] = cled2
    np[2] = cled3
    np[3] = cled4
    np.show()

#not work
def light_sensor():
    display.off()
    sleep(100)
    value = pin10.read_analog()
    pin10.write_digital(1)
    display.on()
    return value
#unit test

def test_music():
    import music
    music.play(music.NYAN)

def test_pixel():
    set_color((10,0,0),(0,0,0),(0,0,0),(10,10,10))

def test_i2c():
    i2c.init(freq=100000, sda=pin20, scl=pin19)
    i2c.scan()

def test_motor():
    move_motor_port(1,30)
    move_motor_port(2,30)

def test_servo():
    servo(1,180)

def test_all():
    test_pixel()
    test_motor()
    test_servo()
    test_music()

#sample usage
test_all()