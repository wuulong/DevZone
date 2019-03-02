import radio as ro
import utime as ut
ro.config(queue=6,address=0x75626972,channel=4,data_rate=ro.RATE_1MBIT)
ro.on()
ut.sleep_ms(100)

while True:
    rns = ro.receive_full()
    if rns:
        msg, rssi, ts = rns
        line = str(msg, 'UTF-8')
        line = line.strip()
        print("msg=%s,R=%s-rssi %i"%(msg,line[3:],rssi))