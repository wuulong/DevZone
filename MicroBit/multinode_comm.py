#Microbit Radio multi-node bi-direction communication test
#Features:
#   multi-nodes communication with re-transmition
#   current ids show on LEDs (sid: brighter,did: darker)
#   random tx rate test
#   auto select non-used sid
#   sid collision avoidence
#Usage:
#   Button-A: start, Button-B: change sid
#   plot format: (tx_rate,rx_rate,ack_loss rate)
#   rate unit: Hz/s, throughput can estimated by * 32
#   limitation: max nodes = 20, due to reserved 20 LEDs to show device id
#LICENSE: MIT
#Author: WuLung Hsu, wuulong@gmail.com
#Document: https://paper.dropbox.com/doc/MbitBot--AWWwIfCnEicRuc7gSfO_tmcJAg-DG5SSj5zQhBv1CoAgDtAG

from microbit import *
import radio
import utime
import random
#protocol:
#   (1,20) random select ID as device ID
#   device id 0 used for broadcast
#   data format: TID:RID:value
#   ACK format: value as ~
#   broadcast msg "sid:0:0" every second
#   power-up receive 1.5 second to select new device id
#   auto invalid leaving node
#   LED index (x*5+y) as sid-1
#   if sid collision, need to change new sid
class Comm():
    def __init__(self):
        self.sid = 0
        self.ack = "~"
        self.tx_cnt = 0
        self.rx_cnt = 0
        self.tx_new_cnt = 0
        self.rx_new_cnt = 0
        self.ack_cnt = 0
        self.used_ids = []
        self.used_ids_next = []
        self.ack_received = False
        radio.config(queue=6,address=0x75626972,channel=4,data_rate=radio.RATE_1MBIT)
        radio.on()
        sleep(100)
        pass
    def tx(self,did,value):
        self.tx_cnt += 1
        tx_txt = "%i:%i:%s" %(self.sid,did,str(value))
        radio.send(tx_txt)
        self.pixel_debug(1,self.tx_cnt)
    def get_new_id(self,used_ids):
        while True:
            id = random.randint(1, 20)
            if not id in used_ids:
                break
        return id

    def wait_start(self):
        while True:
            if button_a.was_pressed():
                display.show("F")
                self.used_ids = self.find_used_ids()
                self.sid = self.get_new_id(self.used_ids)
                self.show_id()
                break
    def show_id(self):
        display.clear()
        sid = self.sid - 1
        display.set_pixel(sid%5,int(sid/5),9)
        for id in self.used_ids:
            if id>0:
                uid = id - 1
                display.set_pixel(uid%5,int(uid/5),5)
    def find_used_ids(self):
        used_ids=[]
        time_s = utime.ticks_us()

        while True: # start current measurement
            time_now = utime.ticks_us()
            time_use = utime.ticks_diff(time_now,time_s)
            if 1500000 - time_use <0: # 1.5s
                #display.show("W")
                break
            incoming = radio.receive()
            if incoming:
                items = incoming.split(":")
                if len(items)==3:
                    did = int(items[1])
                    if not (did in used_ids):
                        used_ids.append(did)
        return used_ids


    #display value by LEDs in the bottom
    #part=1: one bottom-right LED
    #part=0: 4 LEDs in at the bottom
    def pixel_debug(self,part,value):
        if part==1: # 1 LED at bottom-right
            value = value *3 % 10
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

    def bi_transfer(self):
        cur_num_tx = 0
        self.wait_start()

        test_cnt = 0

        while True:
            self.rx_cnt = 0
            self.rx_new_cnt = 0
            self.tx_cnt = 0
            self.tx_new_cnt = 0
            self.ack_cnt = 0
            test_period = 1 #s
            test_tick = int(test_period * 1000000)
            test_cnt +=1
            time_s = utime.ticks_us()
            time_l = time_s

            #broadcast device exist every test period
            self.tx(0,str(0))
            # rate target hz
            rate_target = random.randint(1, 100)
            send_tick = int(test_tick/rate_target)


            while True: # start current measurement
                time_now = utime.ticks_us()
                time_use = utime.ticks_diff(time_now,time_s)
                if test_tick - time_use <0: # 10s
                    self.used_ids = self.used_ids_next
                    self.show_id()
                    self.used_ids_next = []
                    break

                time_last = utime.ticks_diff(time_now,time_l)
                if send_tick - time_last <0: # should send
                    time_l = time_now
                    if self.ack_received:
                        cur_num_tx = cur_num_tx+1
                    self.ack_received = False
                    if len(self.used_ids)>0:
                        index = random.randint(0, len(self.used_ids)-1)
                        did = self.used_ids[index]
                        self.tx(did,cur_num_tx)
                        self.tx_new_cnt += 1


                incoming = radio.receive()
                if incoming:
                    self.rx_cnt+=1
                    items = incoming.split(":")
                    if len(items)==3:

                        sid,did,value = items
                        sid = int(sid)
                        did = int(did)
                        if not sid in self.used_ids:
                            self.used_ids.append(sid)
                            self.show_id()

                        if not sid in self.used_ids_next:
                            self.used_ids_next.append(sid)

                        if sid == self.sid: # sid collision
                            self.sid = self.get_new_id(self.used_ids)
                            self.show_id()

                        if did == self.sid:
                            if value == self.ack:
                                self.ack_received = True
                                self.ack_cnt += 1
                            else:
                                self.rx_new_cnt += 1
                                self.tx(sid,self.ack)
                            #radio.send ("%i:%i:%s"%(self.sid,sid,self.ack))

                    self.pixel_debug(0,self.rx_cnt)
                if button_b.was_pressed(): # test sid collision
                    if len(self.used_ids)>0:
                        self.sid = self.used_ids[0]
                    else:
                        self.sid = random.randint(1, 20)
                    break
            tx_rate = float(self.tx_new_cnt)/test_period
            rx_rate = float(self.rx_new_cnt)/test_period
            str_output = "(%.1f,%.1f,%i)" %(tx_rate, rx_rate, self.tx_new_cnt - self.ack_cnt)

            print(str_output)

comm = Comm()
comm.bi_transfer()