#!/usr/bin/env python3

import json
import os
import sys
from time import sleep
from liquidctl import find_liquidctl_devices


def eprint(*args, **kwargs):
    '''
    print to stderr
    '''
    print(*args, file=sys.stderr, **kwargs)

class Fanspeed:
    def __init__(self, dev):
        self._set_attempts = 0
        self.oldspeed = -1
        self.dev = dev
        self.rpm = 0
        self.dc = self.find_dc_device("it86")
        self.init_device()
        self.water_temp = 0
        self.get_temp()
        self.set_speed_all(100)
        self.set_dc_speed("pwm1",255)
        self.set_dc_speed("pwm2",255)
        self.set_dc_speed("pwm1",200)

    def init_device(self):
        init = False
        while init is not True:
            try:
                self.init_status = self.dev.initialize()
                init = True
            except:
                pass

    def set_speed_all(self, speed):
        if speed == self.oldspeed:
            return
        for i in range(1,4):
            fan_set = False
            while fan_set is not True:
                try:
                    self.dev.set_fixed_speed("fan{}".format(i),speed)
                    fan_set = True
                except:
                    pass
        self.set_dc_speed("pwm2",self.temp_to_dc_pwm())
        self.get_rpm()
        eprint("Water has {}°C, set Fans to {}%".format(self.water_temp,speed))
        self.oldspeed = speed
        self._set_attempts = 0

    def set_dc_speed(self,name,value):
        with open(self.dc+name+"_enable","wt") as outp:
            outp.write("0")
        with open(self.dc+name,"wt") as outp:
            outp.write(str(value))

    def get_rpm(self):
        rpm = -1
        while rpm < 0:
            try:
                rpm = self.dev.get_status()[1][1]
            except:
                pass
        self.rpm = rpm

    def get_temp(self):
        water_temp = -1
        while water_temp < 0:
            try:
                water_temp = self.dev.get_status()[-1][1]
            except:
                pass
        self.water_temp = water_temp

    def monitor(self):
        while True:
            self.get_temp()
            self.set_speed_all(self.temp_to_pwm())
            self.watch_pump("fan1_input")
            sleep(60)

    def temp_to_dc_pwm(self):
        pwm = 100+self.temp_to_pwm()*1.55
        if pwm < 100:
            return 0
        elif pwm > 255:
            return 255
        else:
            return int(pwm)

    def temp_to_pwm(self):
        pwm = int((self.water_temp-30)*5)
        if self.water_temp<25:
            return 0
        elif pwm < 10:
            return 10
        elif pwm > 100:
            return 100
        else:
            return pwm

    def find_dc_device(self, name):
        basepath = "/sys/class/hwmon/"
        for f in os.listdir(basepath):
            with open(basepath+f+"/name","rt") as inp:
                if name in inp.read():
                    return basepath+f+"/"

    def watch_pump(self, name):
        with open(self.dc+name,"rt") as inp:
            rpm = int(inp.read())
            if rpm == 0:
                eprint("PUMP NOT RUNNING! Setting Voltage Control to 12V!")
                self.set_dc_speed("pwm1",255)

def run():
    devices = find_liquidctl_devices()
    for dev in devices:
        if 'Corsair Commander' in dev.description:
            with dev.connect():
                Fanspeed(dev).monitor()


if __name__ == '__main__':
    run()
