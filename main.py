import os
import time
import sys
#import binascii
import socket
import select
import onewire
import ds18x20
import urequests

import machine
import network
from machine import deepsleep
#import esp
#esp.osdebug(None)
import ujson


rtc = machine.RTC()
r = rtc.memory()
rtc.memory(b'N')
rtcm = r.decode('ASCII')
if rtcm == 'N': #normal operation
    print("Wake up normally")
else:
    #wdt reboot
    print("Detected WDT reboot")
    machine.deepsleep(11000)

devid = 1234

ssid = 'NCC'
password = 'password'
station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)
machine.freq(80000000)
#configuration of 1-wire
dat = machine.Pin(22)
ds = ds18x20.DS18X20(onewire.OneWire(dat))
roms = [bytearray(b'(\x90\xd2\x1b\x03\x00\x00:')] #ds.scan()
print('found devices:', roms)
if roms:
    try:
        ds.convert_temp()
    except:
        print("1w-err")        


blue_led = machine.Pin(2, machine.Pin.OUT)
blue_led.value(0)
timeout = 0
while (timeout < 4000) and (station.isconnected() == False):
    timeout = timeout + 20
    time.sleep_ms(20)
print(timeout)    

wdt=machine.WDT(timeout=4000)

if station.isconnected() == True:
    blue_led.value(1)
    print('Conn')
    #print(station.ifconfig())
    reqtt = ''    
    if roms:    
        try:
            tt = ds.read_temp(roms[0])
            reqtt = "&temp="+str(tt)    
            print("Temp: " + str(tt)) 
        except:
            print("1w-err")            
    timestamp = time.time_ns()    
    try:
        my_request =  "http://192.168.88.174/data.html?comm=2&id="+str(devid)+"&time="+str(timestamp)+reqtt;
        response = urequests.get(my_request)
        print(response) 
    except:
        print("No server response")
#print(timestamp)
# put the device to sleep
machine.deepsleep(10000)


