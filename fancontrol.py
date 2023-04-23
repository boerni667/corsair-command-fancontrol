#!/usr/bin/env python3

import json
from time import sleep
from liquidctl import find_liquidctl_devices

class Fanspeed:
    def __init__(self, dev):
        self._set_attempts = 0
        self.oldspeed = -1
        self.dev = dev
        self.rpm = 0
        self.init_status = self.dev.initialize()
        self.water_temp = 0
        self.get_temp()
        self.set_speed_all(100)
        while self.rpm < 2000:
            self.get_rpm()
            sleep(1)

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
        self.get_rpm()
        print("Water has {}°C, set Fans to {}%".format(self.water_temp,speed))
        self.oldspeed = speed
        self._set_attempts = 0

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
            sleep(60)

    def temp_to_pwm(self):
        pwm = int((self.water_temp-30)*5)
        if pwm < 10:
            return 0
        elif pwm > 100:
            return 100
        else:
            return pwm


def run():
    devices = find_liquidctl_devices()
    for dev in devices:
        if 'Corsair Commander' in dev.description:
            with dev.connect():
                Fanspeed(dev).monitor()


if __name__ == '__main__':
    run()
