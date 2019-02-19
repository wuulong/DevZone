# motor decoder
#features:
#   decode 2-bit quadrature-encoded rotary encoder
#test case: OpenCR
#Usage: power-on start
#Default: debug print current position
#LICENSE: MIT
#Author: WuLung Hsu, wuulong@gmail.com
# doc: https://paper.dropbox.com/doc/MbitBot--AXygciMpkj~Tsk6AdFTEKGtsAg-DG5SSj5zQhBv1CoAgDtAG#:uid=546258796330450544968800&h2=decoder-routing
from microbit import *
import utime

def rotation_decode():

    pinA = pin1 #pin15
    pinB = pin0 #pin16
    pA = 0
    pB = 0
    pos =0
    while True:

        while True:


            # read both of the switches
            A = pinA.read_digital()
            B = pinB.read_digital()
            bP = False
            if A != pA:
                bP = True
                if A == 1:
                    if B == 0:
                        pos+=1
                    else:
                        pos-=1
                else:
                    if B==1:
                        pos+=1
                    else:
                        pos-=1
                pA = A

            if B!=pB:
                bP = True
                if B==1:
                    if A==1:
                        pos+=1
                    else:
                        pos-=1
                else:
                    if A==0:
                        pos+=1
                    else:
                        pos-=1
                pB = B

            if bP:# and (pos==0 or pos==-400 or pos==400): # comment out in normal case
                print("(%i)"%(pos))

rotation_decode()