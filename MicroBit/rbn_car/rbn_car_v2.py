# RobotBitNet Car
# Licence: MIT
# Limited memory coding style, doc in the same folder
import radio as ro
import utime as ut
import random as rn
from microbit import display as di
from microbit import button_a,button_b, i2c, compass, uart,accelerometer,microphone,sleep
from microbit import pin_logo

import struct


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

def motor(Spin, Speed):
    TM1 = int(Speed % 256)
    TM2 = int(Speed / 256)
    CH = (Spin - 1) * 4 + 8
    CH1 = int((CH <<8) + TM1)
    CH2 = int(((CH + 1) <<8) + TM2)
    i2c.write(64, struct.pack('>H', CH1))
    i2c.write(64, struct.pack('>H', CH2))

def move_motor_port(MPort, usevalue):
    if(usevalue>100):
        usevalue = 100
    if(usevalue<-100):
        usevalue = -100
    dir=0
    #MP2 may have bug
    mpid = 13
    if MPort==2:
        usevalue=-usevalue
        mpid = 15

    if usevalue<0:
        usevalue = -usevalue
        dir=1

    usevalue = mymap(usevalue, 0, 100, 0, 4095)

    if dir==0:
        motor(mpid, usevalue)
        motor(mpid+1, 0)
    else:
        motor(mpid, 0)
        motor(mpid+1, usevalue)

#communication 

lid = 0
ack = "~"
txc = 0#tx_cnt
rxc = 0#rx_cnt
uids = [] #used_ids
uidsn = [] #used_ids_next
ackd = False#ack_received
ms = 0#master_status
cs = 0#cmd_status
mid = 0#master id

def init():

    ro.config(queue=6,address=0x75626972,channel=4,data_rate=ro.RATE_1MBIT,length=64)
    ro.on()
    ut.sleep_ms(100)



def tx(did,v):
    global txc
    txc += 1
    txt = "%i:%i:%s" %(lid,did,str(v))
    ro.send(txt)
    print("T=%s" %(txt))
    leds(1,txc)

def txp(did,ty,v):
    if ty==1:
        txt = "1,1,%i,%i" %(ms,cs)
    elif ty==2:
        txt = "1,2,%i,%i,%s" %(ms,cs,v)
    elif ty==3:
        #sensing_str = "%i,%i,%i,%i,%i,%i" % (int(pin_logo.is_touched()),display.read_light_level(),a_x,a_y,a_z,compass.heading())
        a_x,a_y,a_z = accelerometer.get_values()
        sensing_str = "%i,%i,%i,%i,%i,%i" % (int(pin_logo.is_touched()),di.read_light_level(),microphone.sound_level(),a_x,a_y,a_z)
        txt = "1,3,%i,%i,%i,%s" %(ms,cs,v, sensing_str)

    elif ty==20:
        txt = "1,20,%s" %(v)
    elif ty==22:
        txt = "1,22,%i,%i" %(v[0],v[1])

    else:
        txt = "1,%i,%s" %(ty,v)
    tx(did,txt)

def gnid(used_ids):#get_new_id
    global ms,mid,lid
    for id in range(1,20):
        if not id in used_ids:
            break
    if id==1:
        lid=1
        ms=1
        mid=1
    else:
        lid=id

def mt():
    global uids,mid
    if not mid in uids:
        mid=0

def find_used_ids():
    used_ids=[]
    t_s = ut.ticks_us()

    while True: # start current measurement
        t_now = ut.ticks_us()
        t_use = ut.ticks_diff(t_now,t_s)
        if 1500000 - t_use <0: # 1.5s
            break
        incoming = ro.receive()
        if incoming:
            items = incoming.split(":")
            if len(items)==3:
                sid = int(items[0])
                if not (sid in used_ids):
                    used_ids.append(sid)
    return used_ids

def wait_start():
    global uids,lid,joystick
    go=0
    while True:
        if button_b.was_pressed():
                joystick=1
                di.show("J")
                go=1                 
        if button_a.was_pressed():
            go=1
            di.show("F")
            i2c_init()
            move_motor_port(1,0)
            move_motor_port(2,0)
            
        if go==1:
            sleep(500)
            di.clear()
            uids = find_used_ids()
            gnid(uids)
            break


def show_id():
    di.clear()

    for id in uids:
        if id>0:
            uid = id - 1
            di.set_pixel(uid%5,int(uid/5),2)

    uid = lid - 1
    di.set_pixel(uid%5,int(uid/5),5)

    id = mid
    if id>0:
        uid = id-1
        di.set_pixel(uid%5,int(uid/5),9)

def leds(part,va):#pixel_debug
    va = va % 10
    if part==1: # tx
        va = va *3 % 10
        di.set_pixel(4, 4, va)
    elif part==0:# rxc
        di.set_pixel(0, 4, va)
    elif part==2:#master
        di.set_pixel(3, 4, va)
    else: #3 Rx
        va = va % 30
        for i in range(3):
            if va >=9:
                di.set_pixel(i, 4, 9)
            elif va<0:
                di.set_pixel(i, 4, 0)
            else:
                di.set_pixel(i, 4, va)
            va -=10
def leds_br():
    if ms==1:
        leds(2,9)
    elif mid>0:
        leds(2,5)
    else:
        leds(2,0)

def rccar_tx(did):
    global px_cur,py_cur
    [x,y,z] = accelerometer.get_values()
    px = mymap(x,-1000,1000,0,5)
    py = mymap(y,-1000,1000,0,5)
    #print("(%i,%i,%i,%i,%i)"%(x,y,z,px,py))

    if px_cur != px or py_cur != py:
        di.set_pixel(px_cur, py_cur, 0)
    di.set_pixel(px, py, 9)
    px_cur = px
    py_cur = py

    px_cmd = mymap(x,-1000,1000,0,100)
    py_cmd = mymap(y,-1000,1000,0,100)



    cmd = px_cmd *100 + py_cmd
    txp(did,23,str(cmd))
    #radio.send(str(cmd))
    #trx_cnt +=1
    #pixel_debug(trx_cnt)
    
def rccar_rx(cmd):
    global px_cur,py_cur
    px_cmd = int(cmd/100)
    py_cmd = cmd % 100

    px = mymap(px_cmd,0,100,0,5)
    py = mymap(py_cmd,0,100,0,5)
    if px_cur != px or py_cur != py:
        di.set_pixel(px_cur, py_cur, 0)
    di.set_pixel(px, py, 9)

    px_cur = px
    py_cur = py

    go_value = -(py_cmd-50)*2
    percent = (px_cmd-50)

    value1 = go_value-percent
    value2 = go_value+percent

    move_motor_port(1,value1)
    move_motor_port(2,value2)



#car related
joystick=0 # if used for joystick, will be at broker. press_b to enable
ver = 2.0

init()
cur_num_tx = 0
ur=""
wait_start()
tp = 1 #
t_tick = int(tp * 1000000) #broadcast


rt=5
send_tick = int(t_tick/rt) #send cmd
t_l = ut.ticks_us()
cidx=0
lc = 1

rssi=0
rid=0
rrssi=0
csid=1

tidx=0

#car
px_cur = 0
py_cur = 0
trx_cnt = 0

while True:
    #di.show("R")
    rxc = 0
    txc = 0
    t_s = ut.ticks_us()
    lu = len(uids)
    #broadcast device exist every test period
    txp(0,3,lu)
    mt()
    #show_id()
    #leds_br()
    

    while True: # start current measurement
        t_now = ut.ticks_us()
        t_use = ut.ticks_diff(t_now,t_s)
        if t_tick - t_use <0: # broadcast
            if lc % 5==0:
                uids = uidsn
                uidsn = []
            break

        t_last = ut.ticks_diff(t_now,t_l)
        if send_tick - t_last <0: # should send
            t_l = t_now
            if ackd:
                cur_num_tx = cur_num_tx+1
            ackd = False
            if lu>0:
                cidx %= lu
                did = uids[cidx]
                if joystick==1:
                    rccar_tx(did)
                cidx +=1
                
                    

        rns = ro.receive_full()
        if rns:
            rxc+=1
            msg= rns[0]
            rssi = rns[1]
            line = str(msg, 'UTF-8')[3:]
            items = line.split(":")
            if len(items)==3:

                sid,did,value = items
                sid = int(sid)
                did = int(did)
                if not sid in uids:
                    uids.append(sid)

                if not sid in uidsn:
                    uidsn.append(sid)

                if sid == lid: # sid collision
                    gnid(uids)
                    break


                if did == lid:
                    if value == ack:
                        ackd = True
                    else:
                        tx(sid,ack)
                print("R=%s" %(line))
                pvs = value.split(",")

                if did==0:
                    if pvs[0]=="1":
                        if pvs[1]=="1" or pvs[1]=="2" or pvs[1]=="3":
                            if pvs[2]=="1":
                                mid = sid
                            if mid == sid and pvs[2]=="0":
                                mid = 0


                if did==lid:
                    if pvs[0]=="1":
                        if pvs[1]=="20": #action
                            di.show(pvs[2])
                        if pvs[1]=="10":
                            csid = sid
                            rid = int(pvs[2])
                        if pvs[1]=="23": #rccar_rx
                            rccar_rx(int(pvs[2]))
                        if pvs[1]=="22":
                            di.show("G")
                            px_cmd = int(pvs[2])
                            py_cmd = int(pvs[3])

                            go_value = -(py_cmd-50)*2
                            percent = (px_cmd-50)

                            value1 = go_value-percent
                            value2 = go_value+percent

                            move_motor_port(1,value1)
                            move_motor_port(2,value2)
                
                if sid==rid:
                    if pvs[0]=="1":
                        rrssi = rssi
                        txp(csid,11,"%i,%i" % (rid,rssi))
                        rid=0

                del pvs
                del items

            leds(0,rxc)


    lc +=1
    #print("%i,%i" %(lid,mid))
    #di.show("R")
