import serial
import mysql.connector
from mysql.connector import Error
from datetime import datetime
arduino= serial.Serial('COM7',9600)

myconn = mysql.connector.connect(host = "localhost", user = "root",passwd = "root",database = "stpms")  
cur = myconn.cursor() 


while(1==1):

    if (arduino.inWaiting()>0):
        passengercount = arduino.readline()
        g = passengercount.decode('ascii')
        print('passeneger count :'+g)
        
        rightnow = datetime.now()#right now time
        currentTime = str(rightnow)
        u = g.split(',')
        print(u)
        print('split string 0: '+u[0])
        print('split string 1: '+u[1])

        details=u[0].split('|')
        print(details)
        print('split string 0 routeId: '+details[0])
        print('split string 1 Name: '+details[1])
        print('split string 1 From: '+details[2])
        print('split string 1 To: '+details[3])
        print('split string 1 In Time : '+currentTime)
        print('split string 1 Out Time: '+currentTime)
        print('split string 1 on bus or not: '+u[1])


        
        s2 = open('website/passengerList.txt','a')
        s2.write(currentTime)
        s2.write(': ')
        s2.write(u[0])
        s2.write(': pessangers -> ')
        s2.write(u[1])
        s2.write('\n')

        s = open('website/occupied.txt','w')
        s.write(u[1])
       
        eq = int(u[1])
        pa = 55-eq
        st = str(pa)
        s1 = open('website/vaccant.txt','w')
        s1.write(st)
        
        s.close()
        s1.close()
        s2.close()

        if(int(u[1])==1):
            print('inside if')
            sql = "insert into travel_detail(Route_Id, Passenger_Name, Initial_Loc, Destination_Loc, In_Time, Status) values (%s, %s, %s, %s, %s, %s)"  
  
            #The row values are provided in the form of tuple   
            val = (details[0], details[1], details[2], details[3], currentTime, 1)  
  
            try:  
                print('inside try for INSERT')
            #inserting the values into the table  
                cur.execute(sql,val)  
            #commit the transaction   
                myconn.commit()  
                print(cur.rowcount,"record inserted!")  
            except mysql.connector.Error as error:
                print("Failed to insert record into Laptop table {}:".format(error))

           
        else:
            print('inside ELSE')
            try:  
                #updating the name of the employee whose id is 110  
                cur.execute("update travel_detail Status = 0 and Out_Time = ? where Passenger_Name = ? and Destination_Loc = ?",(currentTime,details[1],details[3]))  
                myconn.commit()  
            except:  
                print('inside except-rollback for insert')
                myconn.rollback() 


        try:  
            print('inside try for read')
                #Reading the Employee data      
            cur.execute("SELECT * FROM travel_detail")  
            
                #fetching the rows from the cursor object  
              
                #printing the result  
                
            for x in cur:  
                print(x);  
        except mysql.connector.Error as error:
                print("Failed to insert record into Laptop table {}".format(error))

       
if (myconn.is_connected()):
    myconn.close()
    cur.close()
    print("MySQL connection is closed")
