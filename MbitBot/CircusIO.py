#MbitBot circus IO example
#Tested:
#OK list(LED, pixel RGB,Analog VR )
#KO list(Vibration)
#Definition:
#conn_id:
#   C1: i2c far M1  C2: i2c near M1 C3: p15 C4: p13 C5: p9 C6: p5 C7: p1 C8: p3
# circus_type:
#   1:Analog VR 2: LED 3:Pixel RGB 4:Serial RGB 5:Vibration 6:Encoder 7:Temperature/Humidity
#LICENSE: MIT
#Author: WuLung Hsu, wuulong@gmail.com
from microbit import *

class CircusIO():
    def __init__(self):
        self.pin_led = pin15
        self.pin_pixel_rgb = pin15
        self.pin_vibration = pin15
        self.pin_analog_vr = pin15
        pass
    #conn_id:
    #   C1: i2c far M1  C2: i2c near M1 C3: p15 C4: p13 C5: p9 C6: p5 C7: p1 C8: p3
    # circus_type:
    #   1:Analog VR 2: LED 3:Pixel RGB 4:Serial RGB 5:Vibration 6:Encoder 7:Temperature/Humidity

    def set_pin(self, circus_type , conn_id):
        if conn_id == 3:
            pin = pin15
        elif conn_id == 4:
            pin = pin13
        elif conn_id == 5:
            pin = pin9
            display.off()
        elif conn_id == 6:
            pin = pin5
            #button mode, can't use
        elif conn_id == 7:
            pin = pin1
        elif conn_id == 8:
            pin = pin3

        if circus_type == 1: #Analog VR
            self.pin_analog_vr = pin
        if circus_type == 2: #LED
            self.pin_led = pin
        if circus_type == 3: #Pixel RGB
            self.pin_pixel_rgb = pin
        if circus_type == 5: #Vibration
            self.pin_vibration = pin
    def get_vr(self):
        return self.pin_analog_vr.read_analog()
    def set_led(self,value):
        self.pin_led.write_digital(value)

    def set_color(self,cled1,cled2,cled3,cled4):
        import neopixel
        np = neopixel.NeoPixel(self.pin_pixel_rgb, 4)
        np[0] = cled1
        np[1] = cled2
        np[2] = cled3
        np[3] = cled4
        np.show()
    def set_vibration(self,value):
        self.pin_vibration.write_digital(value)

    # test result: OK list(LED, pixel RGB,Analog VR ), KO list(Vibration)
    #1:Analog VR 2: LED 3:Pixel RGB 4:Serial RGB 5:Vibration 6:Encoder 7:Temperature/Humidity
    def test(self,test_id):
        if test_id == 1: #Analog VR
            self.set_pin(1,7)
            while True:
                print("(%i)"%(self.get_vr()))
                sleep(100)
        if test_id == 2:# LED
            self.set_pin(2,3)
            self.set_led(1)
        if test_id==3: #Pixel RGB
            self.set_pin(3,3)
            self.set_color((10,0,0),(0,10,10),(0,10,0),(10,10,0))
        if test_id == 5: #Vibration
            cio.set_pin(5,3)
            cio.set_vibration(1)

cio = CircusIO()
cio.test(1)
#while True:
#    print("(%i,%i)"%(pin1.read_analog(),pin2.read_analog()))
#    sleep(10)
#pin15.write_digital(1)


#while True:
#    pin15.write_digital(1)
#    sleep(20)
#    pin15.write_digital(0)
#    sleep(480)

#if 0:
#    while True:
#        if button_a.was_pressed():
#            cio.test(2)
#            sleep(1000)