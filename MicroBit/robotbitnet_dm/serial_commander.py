#SerialCommander
#Features:
#    simple tool to tx/rx uart in thread
#Usage:
#    115200,N81
#    hardcode uart device name
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
#Serial process thread
class MonitorThread(threading.Thread):
    def __init__(self, wait=0.01):
        threading.Thread.__init__(self)
        self.event = threading.Event()
        self.wait = wait
        self.exit = False
        self.ser = Serial(ser_name, 115200, timeout=1) #FIXME, change device id to your system device

    def set_ts(self, ts):
        self.wait = ts

    def do_function(self):
        #print("thread running...")
        line = self.ser.readline()
        if len(line)>0:
            #print(line)
            #msg = line.decode("UTF-8") 
            #print(type(line))
            msg = line.strip()
            sys.stdout.write(msg)
    
    def run(self):
        while 1:
            if self.exit:
                break
                # Wait for a connection
            self.do_function()
            self.event.wait(self.wait)

    def serial_send(self,send_str):
        sys.stdout.write("[%s]\n" % send_str)
        self.ser.write(send_str + "\r\n")

def main():
    
    th = MonitorThread()
    th.start()
        
    while 1:
        try:
            #th.serial_send("F83")
            time.sleep(1)
        except:
            th.exit = True
            break

if __name__ == "__main__":
    main()