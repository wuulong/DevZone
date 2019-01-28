#Microbit Radio TxRx communication Test
#Test Cases:
#   NoAck - one direction
#   AckWithReTx - Re-transmittion
#
#LICENSE: MIT
#Author: WuLung Hsu, wuulong@gmail.com
#Document: https://paper.dropbox.com/doc/MbitBot--AWWwIfCnEicRuc7gSfO_tmcJAg-DG5SSj5zQhBv1CoAgDtAG

from microbit import *
import radio
import utime

#radio channel test with noack method: measure transfer rate and correction.
#installation: the same firmware can be used in both board
#usage: press button_a become transmitter, button_b become receiver(active without sequence), measurement result show on display and print
#output format: rate/s, correct_rate %
def test_pingpong_withoutack():
    radio.config(queue=6,address=0x75626970,channel=6,data_rate=radio.RATE_2MBIT)
    radio.on()

    cur_num_rx = 0
    cur_num_tx = 0

    while True:
        if button_a.was_pressed():
            display.show("T")
            mode=0
            break
        if button_b.was_pressed():
            mode=1
            break


    # Event loop.
    if mode == 0: #master, Tx
        while True:
            cur_num_tx = cur_num_tx+1
            radio.send(str(cur_num_tx))  # a-ha
            #sleep(1000)
            # Read any incoming messages.

            if button_b.was_pressed():
                break
    else: #slave, Rx
        while True:
            num_total = 0
            num_cor = 0
            first=1
            test_period = 1 #s
            test_tick = int(test_period * 1000000)

            time_s = utime.ticks_us()
            display.show("R")
            while True: # start current measurement
                time_now = utime.ticks_us()
                time_use = utime.ticks_diff(time_now,time_s)
                if test_tick - time_use <0: # 10s
                    break

                incoming = radio.receive()
                if incoming:
                    num_total+=1
                    rx_num = int(incoming)
                    if first == 1 or (rx_num == cur_num_rx+1):
                        num_cor +=1
                        first = 0
                    cur_num_rx = rx_num

            if num_total > 0 :
                rate = float(num_total)/test_period
                cor_rate = float(num_cor)/num_total*100
                #display.scroll("%i / %i / %.1f / %03.2f" %(num_cor, num_total, rate, cor_rate))
                str_output = "%.1f / %03.2f" %(rate, cor_rate)
                str_print = "(%.1f , %03.2f)" %(rate, cor_rate)
            else:
                str_output = "%i / %i " %(num_cor, num_total)
                str_print = "(%i , %i)" %(num_cor, num_total)
            print(str_print)
            if test_period>=3:
                display.scroll(str_output)



pixel_value = 0
#display value by LEDs in the bottom
#part=1: one bottom-right LED
#part=0: 4 LEDs in at the bottom
def pixel_debug(part,value):
    if part==1: # 1 LED at bottom-right
        value = value % 10
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


time_wait_cur = 10000 # 10ms
def re_tx(value):
    global time_wait_cur
    global pixel_value
    tx_cnt = 0

    while True:
        correct = 0
        radio.send(str(value))
        tx_cnt += 1
        pixel_debug(1,tx_cnt)
        time_s = utime.ticks_us()
        while True:
            time_now = utime.ticks_us()
            time_use = utime.ticks_diff(time_now,time_s)
            if time_wait_cur - time_use < 0: # 100ms
                break
            incoming = radio.receive()
            if incoming:
                rx_num = int(incoming)
                #print("rx:%i" %(rx_num))
                if rx_num == value:
                    pixel_value +=1
                    pixel_debug(0,pixel_value)
                    correct=1
                    break
        if tx_cnt <= 2: # first correct
            time_wait_cur = int(time_wait_cur * 0.99)
        else:
            time_wait_cur = int(time_wait_cur * 2)
            if time_wait_cur>=1000000:
                time_wait_cur = 1000000
        if correct==1:
            break


#radio channel test with ack method: measure transfer rate and overhead_rate.
#installation: the same firmware can be used in both board
#usage: press button_a become transmitter, button_b become receiver(active without sequence), measurement result show on display and print
#output format: rate/s, overhead_rate %
def test_pingpong_ack():
    radio.config(queue=6,address=0x75626971,channel=4,data_rate=radio.RATE_1MBIT)
    radio.on()
    sleep(100)

    cur_num_rx = 0
    cur_num_tx = 0
    global pixel_value



    while True:
        if button_a.was_pressed():
            display.show("T")
            mode=0
            break
        if button_b.was_pressed():
            display.show("r")
            mode=1
            break


    # Event loop.
    if mode == 0: #master, Tx
        num_total = 0
        num_cor = 0
        first=1
        test_period = 1 #s
        test_tick = int(test_period * 1000000)

        while True:

            cur_num_tx = cur_num_tx+1
            re_tx(cur_num_tx)
            if cur_num_tx % 100 == 0:
                str_print = "(%.1f)" %(time_wait_cur) #wait time debug
                print(str_print)

            if button_a.was_pressed():
                display.show("E")
                break
    else: #slave, Rx
        test_cnt = 0
        while True:
            num_total = 0
            num_cor = 0
            first=1
            test_period = 3 #s
            test_tick = int(test_period * 1000000)
            test_cnt +=1
            time_s = utime.ticks_us()
            display.show("R")
            pixel_debug(1,test_cnt)
            while True: # start current measurement
                time_now = utime.ticks_us()
                time_use = utime.ticks_diff(time_now,time_s)
                if test_tick - time_use <0: # 10s
                    #display.show("W")
                    break

                incoming = radio.receive()
                if incoming:
                    num_total+=1

                    rx_num = int(incoming)
                    if first == 1 or (rx_num == cur_num_rx+1):
                        num_cor +=1
                        first = 0
                    radio.send(str(rx_num))
                    cur_num_rx = rx_num
                    pixel_value +=1
                    pixel_debug(0,pixel_value)

            if num_cor > 0 :
                rate = float(num_cor)/test_period
                overhead_rate = float(num_total)/num_cor*100
                #display.scroll("%i / %i / %.1f / %03.2f" %(num_cor, num_total, rate, overhead_rate))
                str_output = "%.1f / %03.2f" %(rate, overhead_rate)
                str_print = "(%.1f , %03.2f)" %(rate, overhead_rate)


            else:
                str_output = "%i / %i " %(num_cor, num_total)
                str_print = "(%i , %i)" %(num_cor, num_total)
            print(str_print)
            if test_period>=5:
                display.scroll(str_output)

def test_10s():
    time_s = 0
    while True:
        if button_a.was_pressed():
            time_s = utime.ticks_us()
        time_now = utime.ticks_us()
        if time_s !=0 and utime.ticks_diff(time_now,time_s)>10000000:
            display.show(Image.HAPPY)
            break

#test_pingpong_withoutack()
test_pingpong_ack()