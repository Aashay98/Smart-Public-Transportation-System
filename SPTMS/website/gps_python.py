import serial
import json
from datetime import datetime
arduino1= serial.Serial('/dev/cu.usbmodem14201',9600)
while(1==1):
    if (arduino1.inWaiting()>0):
        gpsC = arduino1.readline()
        gps = gpsC.decode('UTF-8')
        print(gps)
        uq = gps.split(',')
         p = open('lat.txt','w')
        p.write(uq[0])
        p1 = open('long.txt','w')
        p1.write(uq[1])
        p.close()
        p1.close()
        data = [{'lat':float(uq[0]),'lon':float(uq[1].strip())}]
        with open("gps.json",'w')as jsonFile:
            json.dump(data,jsonFile)
            
            

