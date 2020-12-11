from microbit import *
cnt=0
while True:
    x = cnt %5
    y = int(cnt / 5) % 5
    v = int(cnt/ 25) % 2

    rl= uart.readline()
    if rl:
        print("I")
    display.set_pixel(x, y, 5-v*5)
    cnt+=1
    sleep(1000)