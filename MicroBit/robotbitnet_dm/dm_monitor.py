#RobotBitNet domain monitor
#Features:
#    log RobotBitNet network
#    support dm send raw command through radio tx
#    dm prototype with nodes(all init information from uart rx)
#    CLI support
#    pertype info, monitor id, maxnodes test
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
import cmd


ser_name = '/dev/cu.usbmodem1412'
VERSION = "0.3"

dm = None
cli = None
th = None

class Node():
    def __init__(self,id):
        self.id = id
        self.last_rx = 0
        self.ms = False
        self.cs = False
        self.tinfo = {} #pertype infor, type as id, content [], ex: 20->[number]
    #l3: [] for l3 information, ex [1,20,number]
    def rx_update(self,l3):
        self.last_rx = time.time()
        #print("rx_update=%s"%(str(l3)))
        if len(l3)>=2:
            tid = int(l3[1])
            self.tinfo[tid] = l3[2:]
            if tid== 1 or tid==2:
                self.ms = int(l3[2])
                self.cs = int(l3[3])

    def desc(self):
        t_now = time.time()
        txt = "node ID=%2i, last_rx=%2.3f s,ms=%i,cs=%i" %(self.id,self.last_rx - t_now,self.ms,self.cs)
        for id in self.tinfo.keys():
            txt +="\n\ttype[%i]=%s" %(id,self.tinfo[id])
        return txt
# DM function
class DM():
    def __init__(self):
        self.dmid=0 # also sid,no need = 1
        self.sid=1
        self.nodes = {} #id as index, not include self
        self.uids = []
        self.ready = False
        
    def reset(self):
        self.__init__()
    
    def get_nodes_cnt(self):
        if self.ready:
            return len(self.uids) + 1
        else:
            return 0
    def get_max_id(self):
        max_id=self.sid
        for i in range(len(self.uids)):
            if self.uids[i]>max_id:
                max_id = self.uids[i]
        return max_id
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
                    self.ready = True
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
                        self.nodes[sid].rx_update(l3)                        
                    else:
                        if sid in self.nodes:
                            self.nodes[sid].rx_update(l3)
                        

class DmCli(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = 'Dm>'
        self.user_quit = False
        pass
    def do_quit(self, line):
        """quit"""
        self.user_quit = True
        return True
    def do_reset(self,line):
        """reset DM"""
        dm.reset()
    def do_dminfo(self,line):
        """Show DM information"""
        if dm.ready:
            str = "Domain nodes count=%i\nDM ID=%i\nDM broker ID=%i" %(dm.get_nodes_cnt(),dm.dmid,dm.sid)
            print(str)
            for id in dm.nodes.keys():
                node = dm.nodes[id]
                print(node.desc())
        else:
            print("DM not ready!")
        

    def wait_dm_ready(self):
        while dm.dmid==0:
            time.sleep(0.1)
    def do_version(self,line):
        """Report software version"""
        out = "DmMonitor V%s" %(VERSION)
        print(out)
    def do_mon_ids(self,line):
        """Monitor ID/main status"""
        #ss-12345678901234567890
        #01-.DL.
        txt = "SS-"
        max_id = dm.get_max_id() 
        for i in range(1, max_id+1):
            txt += "%s" % (i%10)
        #txt += "\n"
        print(txt)

        for t in range(10): 
            txt = "%2i-" %(t)    
            for i in range(1, max_id+1):
                if i == dm.dmid:
                    sym = "d"
                else:                
                    if i  in dm.nodes:
                        node = dm.nodes[i]
    
                        if node.ms:
                            sym = "l"
                        else:
                            sym = "."
                        if node.cs:
                            sym = sym.upper()
                    else:
                        sym = " "
                txt += sym
                
            print(txt)
            time.sleep(1)
    def do_demo1(self,line):
        """Demo EP show number by sequence"""
        self.wait_dm_ready()
        show_num = 1
        seq = 0          
        while 1:
            sid = dm.sid
            # send command here
            for did in dm.nodes.keys():
                th.serial_send("%i:%i:1,20,%i="%(sid,did,show_num)) 
                show_num+=1
                time.sleep(1)
            
            time.sleep(1)
    def do_maxnodes_test(self,line):
        """Test Max nodes
            maxnodes_test [max_nodes_cnt]
        """
        self.wait_dm_ready()
        show_num = 2
        test_did=0
        
        max_nodes_cnt = 20
        if not line =="":
            max_nodes_cnt = int(line)

        sid = dm.sid
        # send command here
        for did in dm.nodes.keys():
            if test_did==0:
                test_did = did
            print("testing id=%i, max counts=%i" %(did,show_num))
            th.serial_send("%i:%i:1,20,%i="%(sid,did,show_num)) 
            show_num+=1
            time.sleep(1)
        for id in range(1,max_nodes_cnt):
            if not(id == dm.sid or (id in dm.uids) ):
                print("testing id=%i, max counts=%i" %(id,show_num))
                th.serial_send("%i:%i:1,20,%i="%(id,1,show_num)) 
                time.sleep(0.01)
                #th.serial_send("%i:%i:1,20,%i="%(sid,test_did,show_num))
                #time.sleep(0.01)
                
                show_num+=1
        self.do_dminfo("")
        #time.sleep(3)
        #for i in range(10):
        #    th.serial_send("%i:%i:1,20,%i="%(sid,test_did,show_num-1))
        #    time.sleep(1)
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
                #sys.stdout.write(msg_line)
                self.dm.proc_record(msg)

    
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
    global dm,cli,th
    dm = DM()
    cli = DmCli()
    th = MonitorThread(dm)
    th.start()
       
    while 1:
        if 1:
        #try:
            cli.cmdloop()
            if cli.user_quit:
                th.exit = True
                break
        #except:
        #    th.exit = True
        #    print("Exception!")
        #    break

if __name__ == "__main__":
    main()
    
    
