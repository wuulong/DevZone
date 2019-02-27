#RobotBitNet domain monitor
#Features:
#    log RobotBitNet network
#    support dm send raw command through radio tx
#Usage:
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

# DM function
class DM():
    def __init__(self):
        pass
    def proc_record(self,rec):
        with open('dm.log', 'a') as log_file:
            log_file.write(rec)        
    

#Serial process thread
class MonitorThread(threading.Thread):
    def __init__(self, wait=0.01):
        threading.Thread.__init__(self)
        self.event = threading.Event()
        self.wait = wait
        self.exit = False
        self.ser = Serial(ser_name, 115200, timeout=1) #FIXME, change device id to your system device
        self.dm = DM()
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
    
    th = MonitorThread()
    th.start()
    show_num = 1    
    while 1:
        try:
            # send command here
            th.serial_send("2:1:1,20,%i="%(show_num)) #comment out for silence monitoring
            show_num+=1
            time.sleep(1)
        except:
            th.exit = True
            break

if __name__ == "__main__":
    main()