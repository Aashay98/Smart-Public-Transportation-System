from flask import Flask, render_template, request, url_for, redirect, flash, session, jsonify
from datetime import datetime
import qrcode
from fpdf import FPDF
from cryptography.fernet import Fernet
import mysql.connector
from mysql.connector import Error
import smtplib
import math,random

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/',methods = ['GET'])
def login():
   return render_template('login.html')



@app.route('/register',methods = ['GET'])
def register():
   return render_template('register.html')




@app.route('/registerStore',methods = ['POST'])
def registerStore():
   firstName = request.form['firstName']
   lastName = request.form['lastName']
   email = request.form['email']
   password = request.form['password']
   mobileNumber = request.form['mobileNumber']
   dateOfBirth = request.form['dateOfBirth']

   myconn = mysql.connector.connect(host = "localhost", user = "root",passwd = "root",database = "stpms")  
   cur = myconn.cursor()
   
   cur.execute("select loginId from login_table where UserName = %s",(email,)) 
   result = cur.fetchall()
   print(result)

   #insert in login table first
   sqlLogin = "insert into login_table(UserName, password, Status) values (%s, %s, %s)"  
   valLogin = (email, password, 1)  
   try:  
      cur.execute(sqlLogin,valLogin)  
      myconn.commit()  
      print(cur.rowcount,"record inserted!")  
   except mysql.connector.Error as error:
      print("Failed to insert record into Laptop table {}:".format(error))

   #Get the Id of the last added field so that it can be added as foreign key in register table
   cur.execute("select loginId from login_table where UserName = %s",[(email)]) 
   result = cur.fetchone()  

   #To insert in the register table
   sqlRegister = "insert into register_table(FirstName, LastName, MobileNumber, DOB, login) values (%s, %s, %s, %s, %s)"  
   valRegister = (firstName, lastName, mobileNumber, dateOfBirth, result[0])  
   try:  
      print('inside try for INSERT')
      cur.execute(sqlRegister,valRegister)  
      myconn.commit()  
      print(cur.rowcount,"record inserted!")  
   except mysql.connector.Error as error:
      print("Failed to insert record into Laptop table {}:".format(error))

   myconn.close()

   return redirect( url_for('login'))


@app.route('/loginCheck',methods = ['POST'])
def loginCheck():
   myconn = mysql.connector.connect(host = "localhost", user = "root", passwd = "root", database = "stpms")  
   cur = myconn.cursor() 

   email = request.form['username']
   password = request.form['password']

   cur.execute("select UserName,Password from login_table where UserName = %s and Password = %s and Status = true",(email,password)) 
   result = cur.fetchall()
   session['Email'] = email

   cur.execute("select * from login_table") 
   result2 = cur.fetchall()
   print(jsonify(result2))
   myconn.close()

   if result:
      return redirect( url_for('index'))
   else:
      error = 'Check your Password or Email.'
      return render_template("login.html",error = error)



@app.route('/forgetPassword',methods = ['GET'])
def forgetPassword():
   return render_template('forgotPassword.html')


@app.route('/addUsernameFP',methods = ['POST'])
def addUsernameFP():
   email = request.form['username']

   myconn = mysql.connector.connect(host = "localhost", user = "root", passwd = "root", database = "stpms")  
   cur = myconn.cursor() 

   email = request.form['username']

   cur.execute("select UserName from login_table where UserName = %s",(email,)) 
   result = cur.fetchall()

   print(result)
   myconn.close()

   if result:
      s = smtplib.SMTP('smtp.gmail.com', 587)  
      # start TLS for security 
      s.starttls() 
      
      # Authentication 
      s.login("seproject94@gmail.com", "7778976277") 
      
      string = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
      OTP = "" 
      length = len(string) 
      for i in range(6) : 
         OTP += string[math.floor(random.random() * length)] 

      
      # message to be sent 
      message = "Hi ," + email + " your Account OTP is " + OTP
      
      # sending the mail 
      s.sendmail("seproject94@gmail.com", email, message) 
      
      # terminating the session 
      s.quit() 

      session['OTP'] = OTP
      session['Email'] = email
      return render_template("otpverify.html")

   else:
      error = 'This is not a registered Email.'
      return render_template("forgotPassword.html",error = error)


      

@app.route('/otpCheck',methods = ['POST'])
def otpCheck():  
   oldOTP = session.get('OTP')
   newOTP = request.form['otpCheck']

   if(oldOTP == newOTP):
      session.pop('OTP',None)   
      return render_template('createNewPassword.html')
   else:
      error = 'This is the wrong OTP.'
      return render_template("otpverify.html",error = error)




@app.route('/createNewPassword',methods = ['POST'])
def createNewPassword():  
   newPassword = request.form['newpassword']
   confirmPassword = request.form['confirmpassword']
   email = session.get('Email')
   if(confirmPassword == newPassword):
      myconn = mysql.connector.connect(host = "localhost", user = "root", passwd = "root", database = "stpms")  
      cur = myconn.cursor() 

      cur.execute("Update login_table set Password = %s where UserName = %s",(confirmPassword,email)) 
      myconn.commit()  

      myconn.close()
      return redirect( url_for('login'))
   else:
      error = 'The Password doesnot match.'
      return render_template('createNewPassword.html',error = error)
   


@app.route('/index',methods = ['GET'])
def index():
   return render_template('index.html')


@app.route('/busTicketGeneration',methods = ['GET'])
def busTicketGeneration():
   return render_template('busTicketGeneration.html')


@app.route('/generateTicket',methods = ['POST'])
def generateTicket():
 
   start = request.form['start']
   print('start:' + start)
   destination = request.form['destination']
   print('destination:' + destination)
   name = request.form['name']
   print('name:' + name)
   rightnow = datetime.now()#right now time
   currentTime = str(rightnow)
   # create QR code instance
   # Enter data that you want to store
   qr = qrcode.QRCode(
   version = 1,
   error_correction = qrcode.constants.ERROR_CORRECT_H,
   box_size = 5,
   border = 5
   )

   # Enter data that you want to store
   qr_data = (start + ' | ' + destination + ' | ' + name + ' | ' + currentTime).encode()

   #Fernet algorithm
   key = Fernet.generate_key()
   f = Fernet(key)
   encrypted = f.encrypt(qr_data)

   # Add data 
   qr.add_data(qr_data)
   qr.make(fit=True)
   
   img = qr.make_image(); 

   # Save the image
   image_path = name + '.png' 
   img.save(image_path)
   
   #class object FPDF() which is predefiend in side the package fpdf.
   document=FPDF(orientation='P', unit='mm', format='A3')
   document.add_page()
   #font size setting of the page
   document.set_font("Arial", size = 30)
   document.image(image_path, x = 63, y = 80, w = 100)
   #txt message will displayed on pdf page  at the center.
   txt = "Date-Time - {} \n".format(currentTime)
   location = 'From ' + start + ' | ' + 'To - ' + destination
   document.cell(200, 20, txt = 'Bus Ticket', ln = 1, align = "C")
   document.set_font("Arial", size = 15)
   document.cell(200, 10, txt = txt, ln = 6, align = "C")
   document.cell(200, 10, txt = 'Name - ' + name, ln = 9, align = "C")
   document.cell(200, 10, txt = location, ln = 12, align = "C")

   #pdf file naming.
   document.output(name + " Bus Ticket.pdf")
   #creating page format A4 Or A3 Or ...

   print("pdf has been created successfully....") 
   return render_template('busTicketGeneration.html')


@app.route('/busRecord',methods = ['GET'])
def busRecord():
   myconn = mysql.connector.connect(host = "localhost", user = "root", passwd = "root", database = "stpms")  
   cur = myconn.cursor() 

   cur.execute("select RouteNo,Passenger_Name,Start,Destination,Entry_Time,Exit_Time,travelId from travel_detail") 
   result = cur.fetchall()

   print(result)
   myconn.close()
   return render_template('busRecord.html',busRecords=result)


@app.route('/yourProfile',methods = ['GET'])
def yourProfile():
   email = session['Email']
   myconn = mysql.connector.connect(host = "localhost", user = "root", passwd = "root", database = "stpms")  
   cur = myconn.cursor() 

   cur.execute("Select loginId,UserName,Password from login_table where UserName = %s",[(email)]) 
   loginDetail = cur.fetchone()
   cur.execute("Select registerId,FirstName,LastName,MobileNumber,DOB from register_table where login = %s",[(loginDetail[0])]) 
   registerDetail = cur.fetchone()

   myconn.close()
   return render_template('manageProfile.html',registerDetail = registerDetail,loginDetail = loginDetail)

@app.route('/updateRegister',methods = ['POST'])
def updateRegister():
   firstName = request.form['firstName']
   lastName = request.form['lastName']
   email = request.form['username']
   password = request.form['password']
   mobileNumber = request.form['mobileNumber']
   dateOfBirth = request.form['dateOfBirth']
   registerId = request.form['registerId']
   loginId = request.form['loginId']

   myconn = mysql.connector.connect(host = "localhost", user = "root", passwd = "root", database = "stpms")  
   cur = myconn.cursor() 

   cur.execute("Update login_table set Password = %s, UserName = %s where loginId = %s",(password,email,loginId)) 
   myconn.commit()  

   cur.execute("Update register_table set FirstName = %s , LastName = %s , MobileNumber = %s, DOB = %s where login = %s and registerId = %s",(firstName,lastName,mobileNumber,dateOfBirth,loginId,registerId)) 
   myconn.commit()  

   myconn.close() 
   return redirect( url_for('index'))


@app.route('/logOut',methods = ['GET'])
def logOut():
   session.pop('Email',None)
   return redirect( url_for('login'))
   


if __name__ == '__main__':
   app.run(debug = True)