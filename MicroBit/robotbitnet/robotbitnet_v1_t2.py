# RobotBitNet
# Licence: MIT
# Limited memory coding style, doc in the same folder
#from microbit import *
import radio as ro
import utime as ut
import random as rn
from microbit import display as di
from microbit import button_a,button_b

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
    ro.config(queue=6,address=0x75626972,channel=4,data_rate=ro.RATE_1MBIT)
    ro.on()
    ut.sleep_ms(100)


def tx(did,v):
    global txc
    txc += 1
    txt = "%i:%i:%s" %(lid,did,str(v))
    ro.send(txt)
    leds(1,txc)
def txp(did,ty,v):
    if ty==1:
        txt = "1,1,%i,%i" %(ms,cs)

    if ty==20:
        txt = "1,20,%s" %(v)
    tx(did,txt)

def gnid(used_ids):#get_new_id
    for id in range(1,20):
        if not id in used_ids:
            break
    return id

def wait_start():
    global uids,lid
    while True:
        if button_a.was_pressed():
            di.show("F")
            uids = find_used_ids()
            lid = gnid(uids)
            break
def show_id():
    di.clear()

    for id in uids:
        if id>0:
            uid = id - 1
            di.set_pixel(uid%5,int(uid/5),2)

    uid = lid - 1
    di.set_pixel(uid%5,int(uid/5),7)

    id = mid
    if id>0:
        uid = id-1
        di.set_pixel(uid%5,int(uid/5),9)


def find_used_ids():
    used_ids=[]
    t_s = ut.ticks_us()

    while True: # start current measurement
        t_now = ut.ticks_us()
        t_use = ut.ticks_diff(t_now,t_s)
        if 1500000 - t_use <0: # 1.5s
            #di.show("W")
            break
        incoming = ro.receive()
        if incoming:
            items = incoming.split(":")
            if len(items)==3:
                sid = int(items[0])
                if not (sid in used_ids):
                    used_ids.append(sid)
    return used_ids

def leds(part,va):#pixel_debug
    if part==1: # tx
        va = va *3 % 10
        di.set_pixel(4, 4, va)
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

def bi_tran():
    global lid,txc,rxc,uids,uidsn,ackd,ms,cs,mid

    cur_num_tx = 0
    wait_start()
    while True:
        rxc = 0
        txc = 0
        tp = 1 #test_period s
        t_tick = int(tp * 1000000)

        t_s = ut.ticks_us()
        t_l = t_s

        #broadcast device exist every test period
        txp(0,1,"")
        show_id()
        leds_br()


        # rate target hz
        rate_target = rn.randint(1, 100)
        send_tick = int(t_tick/rate_target)


        while True: # start current measurement
            t_now = ut.ticks_us()
            t_use = ut.ticks_diff(t_now,t_s)
            if t_tick - t_use <0: # 10s
                uids = uidsn
                #show_id()
                uidsn = []
                break

            t_last = ut.ticks_diff(t_now,t_l)
            if send_tick - t_last <0: # should send
                t_l = t_now
                if ackd:
                    cur_num_tx = cur_num_tx+1
                ackd = False
                if len(uids)>0:
                    index = rn.randint(0, len(uids)-1)
                    did = uids[index]
                    txp(did,20,cur_num_tx)


            incoming = ro.receive()
            if incoming:
                rxc+=1
                items = incoming.split(":")
                if len(items)==3:

                    sid,did,value = items
                    sid = int(sid)
                    did = int(did)
                    if not sid in uids:
                        uids.append(sid)

                    if not sid in uidsn:
                        uidsn.append(sid)

                    if sid == lid: # sid collision
                        lid = gnid(uids)


                    if did == lid:
                        if value == ack:
                            ackd = True
                        else:
                            tx(sid,ack)
                    pvs = value.split(",")
                    if pvs[0]=="1":
                        if pvs[1]=="1" or pvs[1]=="2":
                            if pvs[2]=="1":
                                mid = sid
                            if mid == sid and pvs[2]=="0":
                                mid = 0
                    del pvs
                    del items

                leds(0,rxc)
            if button_b.was_pressed():
                ms^=1
                if ms == 1:
                    mid=lid
                else:
                    mid=0

        print("%i,%i" %(lid,mid))

init()
bi_tran()