#RobotBitNet domain monitor
#Features:
#    log RobotBitNet network
#    support dm send raw command through radio tx
#    dm prototype with nodes(all init information from uart rx)
#    CLI support
#    pertype info, monitor id, maxnodes test
#    support networkx, monitor per-node rate
#    support rssi capacity, estimate distance
#Default:
#    ask end point report number by sequence
#    115200,N81
#    hardcode uart device name
#Architecture:
#    device uart tx all rx/tx content
#    domain monitor log to file
#Verification:
#    Mac OK
#Requirement:
#    pyserial, networkx
#LICENSE: MIT
#Author: WuLung Hsu, wuulong@gmail.com
#Document: https://paper.dropbox.com/doc/MbitBot--AWWwIfCnEicRuc7gSfO_tmcJAg-DG5SSj5zQhBv1CoAgDtAG

import threading
from serial import *
import time
import sys
import cmd


ser_name = '/dev/cu.usbmodem1412'
VERSION = "0.5.1"

dm = None
cli = None
th = None

def mymap(x, in_min, in_max, out_min, out_max):
    value = int((x-in_min) * (out_max-out_min) / (in_max-in_min) + out_min)
    if value>= out_max:
        value = out_max -1
    elif value < out_min:
        value = out_min

    return value

#calibrate by match any record in the range table
def calibrate_by_offset(cm_m, rssi_m):
    global range_ref
    diff = 0
    for i in range(len(range_ref)):
        [cm,rssi] = range_ref[i]
        if cm_m == cm:
            diff = rssi_m - rssi
            break
    for i in range(len(range_ref)):
        range_ref[i][1] = range_ref[i][1] + diff


def estimate_distance(rssi_m,range_ref):
    max_i = 0
    min_i = 0
    if rssi_m>=range_ref[0][1]:
       return 0
    if rssi_m <= range_ref[len(range_ref)-1][1]:
        return range_ref[-1][0]
    for i in range(len(range_ref)):
        [cm,rssi] = range_ref[i]
        if rssi_m >= rssi:
            max_i = i
            break
        else:
            min_i = i
    return mymap(rssi_m,range_ref[min_i][1],range_ref[max_i][1],range_ref[min_i][0],range_ref[max_i][0])



def test_estimate():
    while True:
        for i in range(-65,-94,-1):
            value = estimate_distance(i,range_ref)
            print("%f->%i"%(i,value))
        sleep(10000)


cal_cm=50
cal_rssi=-76.0

range_ref = [
    [ 0   , -65.2 ],
    [ 10  , -66.0 ],
    [ 20  , -69.1 ],
    [ 30  , -71.0 ],
    [ 40  , -73.0 ],
    [ 50  , -76.0 ],
    [ 75  , -77.0 ],
    [ 100 , -79.0 ],
    [ 125 , -82.0 ],
    [ 150 , -84.6 ],
    [ 200 , -87.6 ],
    [ 250 , -90.0 ],
    [ 300 , -93.7 ]]



class Node():
    def __init__(self,id):
        self.id = id
        self.last_rx = 0
        self.ms = False
        self.cs = False
        self.tinfo = {} #pertype infor, type as id, content [], ex: 20->[number]
        self.rssis = {} #remote node id as key, content rssi
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
            if tid==11:
                self.rssis[int(l3[2])] = int(l3[3])
            #rssi handler, type=11
        

    def desc(self):
        t_now = time.time()
        txt = "node ID=%2i, last_rx=%2.3f s,ms=%i,cs=%i" %(self.id,self.last_rx - t_now,self.ms,self.cs)
        for id in self.tinfo.keys():
            txt +="\n\ttype[%i]=%s" %(id,self.tinfo[id])
        for id in self.rssis.keys():
            rssi = self.rssis[id] 
            cm = estimate_distance(rssi,range_ref)
            txt +="\n\trssi[%i]=%i -> %i cm" %(id,rssi,cm)
        return txt
# DM function
class DM():
    def __init__(self):
        self.dmid=0 # also sid,no need = 1
        self.sid=1
        self.nodes = {} #id as index, not include self
        self.uids = []
        self.nn_cnt = {} #sid-did as key, [current_cnt, ori_cnt, rate ]
        self.ready = False
        self.t_last_mt = 0
        
    def reset(self):
        self.__init__()
    
    def get_nodes_cnt(self):
        if self.ready:
            return len(self.uids)
        else:
            return 0
    def get_max_id(self):
        max_id=self.sid
        for i in range(len(self.uids)):
            if self.uids[i]>max_id:
                max_id = self.uids[i]
        return max_id
    def get_rate_between(self,sid,did,both=True):
        
        rate = 0 
        key = "%i-%i" %(sid,did)
        if key  in self.nn_cnt:
            rate += self.nn_cnt[key][2]
        if both:
            key = "%i-%i" %(did,sid)
            if key  in self.nn_cnt:
                rate += self.nn_cnt[key][2]
        return rate
    def get_distance_between(self,sid,did):
        if not did in self.nodes:
            return 0
        node = self.nodes[did]
        if not sid in node.rssis:
            return 0
        
        rssi = node.rssis[sid]
        
        if not sid in self.nodes:
            return rssi
        node = self.nodes[sid]
        if not did in node.rssis:
            return rssi
        
        rssi += node.rssis[did]
        return int(rssi/2)
        
    def get_sym_fromid(self,id):
        if id == dm.dmid:
            sym = "d"
        else:                
            if id  in dm.nodes:
                node = dm.nodes[id]

                if node.ms:
                    sym = "l"
                else:
                    sym = "e"
                if node.cs:
                    sym = sym.upper()
            else:
                sym = " "
        return sym

    # monitor network rate
    def proc_traffic(self,sid,did):
        if did==0 or did!=0:
            key = "%i-%i" %(sid,did)
            if key in self.nn_cnt:
                self.nn_cnt[key][0]+=1
                pass
            else:
                self.nn_cnt[key] = [0,0,0]
        
    def desc(self):
        if dm.ready:
            str = "Domain nodes count=%i\nDM/broker ID=%i\n" %(dm.get_nodes_cnt(),dm.dmid)
            print(str)
            for id in dm.nodes.keys():
                node = dm.nodes[id]
                print(node.desc())
            for key in dm.nn_cnt.keys():
                nn = dm.nn_cnt[key]
                ids = key.split("-")
                print("%s->%s : %i,%i,%i" %(ids[0],ids[1],nn[0],nn[1],nn[2]))
        else:
            print("DM not ready!")
        
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
                self.proc_traffic(sid,did)
                l3 = ap_str.split(",")  
                if tr == "T" and self.dmid == 0:          
                    self.dmid = sid
                    self.sid = sid 
                    self.ready = True
                if tr == "T" and did==0: # maintain  
                    time_now = time.time()  
                    ids_need_del = []
                    for id in self.nodes.keys():
                        if time_now - self.nodes[id].last_rx > 4.9:
                            ids_need_del.append(id)
                    for id in ids_need_del: 
                        del self.nodes[id]
                        pos = self.uids.index(id)
                        if pos>=0:
                            del self.uids[pos]
                    if self.t_last_mt>0:
                        if time_now - self.t_last_mt >= 4.9:
                            for key in self.nn_cnt:
                                nn = self.nn_cnt[key]
                                nn[2] = nn[0] * 12
                                nn[1] += nn[0]
                                nn[0]=0
                            self.t_last_mt = time_now
                        else:
                            pass
                    else:
                        self.t_last_mt = time_now
                if tr == "R" or tr=="T":
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
        dm.desc()

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
                sym = dm.get_sym_fromid(i)
                txt += sym
                
            print(txt)
            time.sleep(1)
    
        
    def do_network(self,line):
        """Using networkx to plot current network with update per second
            do_network [with_update]    #with_update 0:no update, 1: update     
        """
        import matplotlib.pyplot as plt
        import matplotlib.animation as an
        import networkx as nx
        
        G = nx.Graph()
        
        
        def nx_update(num=0):
            fig.clf()
            fig.suptitle("Current network status")
            G.clear()
            
            #for did in dm.nodes.keys():
            #    rate = dm.get_rate_between(dm.dmid,did)
            #    rssi = dm.get_distance_between(dm.dmid,did)
                
            #    G.add_edge(str(dm.dmid), str(did), weight= rate+1,length=5 )
            
            for id1 in dm.nodes.keys():
                for id2 in dm.nodes.keys():
                    if id2>id1:
                        rate = dm.get_rate_between(id2,id1)
                        rssi = dm.get_distance_between(id2,id1)
                        sym2 = dm.get_sym_fromid(id2)
                        sym1 = dm.get_sym_fromid(id1)
                        n1 = "%i-%s" %(id2,sym2)
                        n2 = "%i-%s" %(id1,sym1)
                        G.add_edge(n1,n2, rate=rate,rssi=rssi)
            
            elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d['rate'] > 0]
            esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d['rate'] <= 0]
            
            pos = nx.spring_layout(G)  # positions for all nodes
            
            # nodes
            nx.draw_networkx_nodes(G, pos, node_size=700)
            
            # edges
            nx.draw_networkx_edges(G, pos, edgelist=elarge,
                                   width=6)
            nx.draw_networkx_edges(G, pos, edgelist=esmall,
                                   width=6, alpha=0.5, edge_color='b', style='dashed')
            
            # labels
            nx.draw_networkx_labels(G, pos, font_size=20, font_family='sans-serif')
            nx.draw_networkx_edge_labels(G, pos)
            plt.axis('off')
        
        fig, ax = plt.subplots() 
        
        nx_update(1)
        if line=="1":
            ani = an.FuncAnimation(fig, nx_update,init_func=nx_update, frames=6, interval=5000, repeat=False)
        plt.show()
        
    def demo1(self,show_num):
        sid = dm.sid
        
        # send command here
        for did in dm.nodes.keys():
            th.serial_send("%i:%i:1,20,%i="%(sid,did,show_num)) 
            show_num+=1
            time.sleep(1)
        
    def do_demo1(self,line):
        """Demo EP show number by sequence"""
        self.wait_dm_ready()
        show_num = 1         
        for i in range(5):
            self.demo1(show_num)            
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
                #msg = line.strip()
                msg = str(line,'UTF-8').strip()
                #print(msg)
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
        out_str = "%s\n" % send_str
        self.ser.write(out_str.encode())



def main():
    calibrate_by_offset(cal_cm,cal_rssi)
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
    
    
