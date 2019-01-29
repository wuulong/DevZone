#MbitBot python example
#Features:
#   support MbitBot extension board: motor,servo
#   support RGB-led, stepper
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

#not work
def light_sensor():
    display.off()
    sleep(100)
    value = pin10.read_analog()
    pin10.write_digital(1)
    display.on()
    return value

#Mbot related
def me_ultrasonic_sensor(Jpin):

    pin = pin2
    if Jpin==1:
        pin = pin14
    if Jpin==2:
        pin = pin16
    if Jpin==3:
        pin = pin2
    if Jpin==4:
        pin = pin4
        display.off() #microbit default in display mode

    cnt1=0
    cnt0=0
    exit_type=0

    #send pulse
    pin.write_digital(0)
    utime.sleep_us(2)
    pin.write_digital(1)
    utime.sleep_us(10)
    pin.write_digital(0)

    #pin.set_pull(pin.PULL_DOWN) #pin.PULL_DOWN, NO_PULL

    time_s = utime.ticks_us()

    while True:
        time_now = utime.ticks_us()
        pvalue = pin.read_digital()
        time_use = utime.ticks_diff(time_now,time_s)

        if pvalue ==1:
            cnt1+=1
        else:
            cnt0+=1
            if cnt1>0 and cnt0>1 :
                exit_type=2
                break

        if 100000 - time_use <0: # 10s
            #display.show("W")
            exit_type=1 #timeout
            break

    if time_use>=30000:
        distance = 0 #400.0 #cm, timeout when real distance = 0
    else:
        distance =  time_use * 5/3/58/2 # d * 5 / 3 / 58 cm, don't know why need last /2

    #d = pins.pulseIn(pin, PulseValue.High, 23000);  // 8 / 340 =
    #return  d #d * 5 / 3 / 58

    #print("(%i,%i,%i,%i,%2.2f)"%(cnt1,cnt0,exit_type,time_use,distance))
    #print("(%2.2f)"%(distance))


#unit test
def test_light():
    print("(%i)" % display.read_light_level())
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
    test_stepper()

def test_stepper():
    #sequence start from M3 , connection: red(A+),blue(A-),green(B+),black(B-)
    control_pins = [10,12,9,11] #drive sequence A+/B+/A-/B-, pwm9,pwm11,pwm10,pwm12,

    halfstep_seq = [
        [1,0,0,0],
        [1,1,0,0],
        [0,1,0,0],
        [0,1,1,0],
        [0,0,1,0],
        [0,0,1,1],
        [0,0,0,1],
        [1,0,0,1]
    ]
    step = 200/4
    for i in range(step):
        for halfstep in range(8): #4 step
            for pin in range(4):
                motor(control_pins[pin],halfstep_seq[halfstep][pin]*4095)
            sleep(10)
        sleep(100)

# utility
def test_plot():
    while True:
        sleep(20)
        print(str(accelerometer.get_values()))

def test_ultrasonic():
    while True:
        print("(%s)" % str(me_ultrasonic_sensor(1)))
        sleep(100)



#while True:
#    test_light()
test_plot()
#sample usage
#i2c_init()
#test_all()