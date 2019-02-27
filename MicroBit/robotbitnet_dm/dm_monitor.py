#RobotBitNet domain monitor
#Features:
#    log RobotBitNet network
#    support dm send raw command through radio tx
#    dm prototype with nodes(all init information from uart rx)
#Default:
#    ask end point report number by sequence
#    115200,N81
#    hardcode uart device name
#Architecture:
#    device uart tx all rx/tx content
#    domain monitor log to file
#Verification:
#    Mac OK
#LICENSE: MIT
#Author: WuLung Hsu, wuulong@gmail.com
#Document: https://paper.dropbox.com/doc/MbitBot--AWWwIfCnEicRuc7gSfO_tmcJAg-DG5SSj5zQhBv1CoAgDtAG

import threading
from serial import *
import time
import sys

ser_name = '/dev/cu.usbmodem1412'

class Node():
    def __init__(self,id):
        self.id = id
        self.last_rx = 0
    def rx_update(self):
        self.last_rx = time.time()
        pass
# DM function
class DM():
    def __init__(self):
        self.dmid=0 # also sid,no need = 1
        self.sid=1
        self.nodes = {} #id as index, not include self
        self.uids = []
        pass
    def get_nodes_cnt(self):
        return len(self.uids) + 1
    #l1 T/R=
    #l2 sid:did:1,type,pertype
    #l3 1,20,num
    def proc_record(self,rec):
        with open('dm.log', 'a') as log_file:
            log_file.write(rec)
        l1 = rec.split("=")
        if len(l1)==2:
            tr , l2_str = l1 
            l2 = l2_str.split(":")
            if len(l2)==3:
                sid,did,ap_str = l2
                sid = int(sid)
                did = int(did)
                l3 = ap_str.split(",")  
                if tr == "T" and self.dmid == 0:          
                    self.dmid = sid
                    self.sid = sid 
                if tr == "T" and did==0: # maintain  
                    time_now = time.time()  
                    for id in self.nodes.keys():
                        if time_now - self.nodes[id].last_rx > 5:
                            del self.nodes[id]
                            pos = self.uids.index(id)
                            if pos>=0:
                                del self.uids[pos]
                if tr == "R":
                    if not sid in self.uids:
                        self.uids.append(sid)
                        self.nodes[sid] = Node(sid)
                        self.nodes[sid].rx_update()                        
                    else:
                        if sid in self.nodes:
                            self.nodes[sid].rx_update()
                        
#Serial process thread
class MonitorThread(threading.Thread):
    def __init__(self, dm, wait=0.01):
        threading.Thread.__init__(self)
        self.event = threading.Event()
        self.wait = wait
        self.exit = False
        self.ser = Serial(ser_name, 115200, timeout=1) #FIXME, change device id to your system device
        self.dm = dm
    def set_ts(self, ts):
        self.wait = ts

    def do_function(self):
        line = self.ser.readline()
        if line:
            if len(line)>0:
                msg = line.strip()
                msg_line =msg+"\n" 
                sys.stdout.write(msg_line)
                self.dm.proc_record(msg_line)

    
    def run(self):
        while 1:
            if self.exit:
                break
                # Wait for a connection
            self.do_function()
            self.event.wait(self.wait)

    def serial_send(self,send_str):
        sys.stdout.write("[%s]\n" % send_str)
        self.ser.write("%s\n" % send_str)

def main():
    dm = DM()
    th = MonitorThread(dm)
    th.start()
    show_num = 1
    seq = 0    

    while dm.dmid==0:
        time.sleep(0.1)
    while 1:
        try:
            sid = dm.sid
            # send command here
            for did in dm.nodes.keys():
                th.serial_send("%i:%i:1,20,%i="%(sid,did,show_num)) 
                show_num+=1
                time.sleep(1)
            
            time.sleep(1)
        except:
            th.exit = True
            break

if __name__ == "__main__":
    main()
