import mysql.connector                          #Andre Barnett - 22025153
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from passlib.hash import sha256_crypt
import hashlib
import gc
from functools import wraps
from datetime import date
import calendar


app = Flask(__name__) #CONTROL + C TO STOP
app.secret_key = "andrekey360" #secret key for sessions


#establishes database connection.
def get_connection():                       
    conn = mysql.connector.connect(host='localhost',
                              port='3306',                              
                              user='root',
                              password='fwdakiddre04',
                              database='horizontravels')
    return conn


@app.route('/')
@app.route('/index/')
def homepage():
    if 'UserType' in session and 'UserEmail' in session:
        print(session['UserType'])
        return render_template('homepagev2.html', usertype = session['UserType'],  UserEmail = session['UserEmail'])
    else:
        session['UserType'] = 'none'
        session['UserEmail'] = 'Account'
        print(session['UserType'])
        return render_template('homepagev2.html', usertype = session['UserType'], UserEmail = session['UserEmail'])


#RENDERS PRIVACY PAGE
@app.route("/privacy/")
def privacy():
    return render_template("privacy.html", usertype = session['UserType'])

#RENDERS SIGN UP PAGE AND INPUTS DATA INTO THE SQL DATABASE IF CORRECT INFORMATION IS ENTERED,
#ALSO HASHES THE PASSWORD

@app.route('/register/', methods=['POST', 'GET'])
def register():
    error = ''
    sucess= ''
    print('Register start')
    try:
        if request.method == "POST":         
            UserFname = request.form['UserFname']
            UserLname = request.form['UserLname']
            UserEmail = request.form['UserEmail']      
            UserPassword = request.form['UserPassword']                
            if UserFname != None and UserLname != None and UserPassword != None and UserEmail != None:           
                conn = get_connection()
                if conn != None:            
                    if conn.is_connected(): #Checking if connection is established
                        UserPassword = sha256_crypt.hash((str(UserPassword))) 
                        print('MySQL Connection is established')                          
                        dbcursor = conn.cursor()    #Creating cursor object                                                                     
                        VerifyEmail = "SELECT * FROM user WHERE UserEmail = %s;" #check if email already exists 
                        dbcursor.execute(VerifyEmail,(UserEmail,))
                        rows = dbcursor.fetchall()           
                        if dbcursor.rowcount > 0:   #this means there is a user with same Email
                            error = "There is Already an Account Which Uses This Email Address, Use Another One or Log In."
                            return render_template("register.html", error=error, usertype = session['UserType'])    
                        else:   #this means we can add new user             
                            dbcursor.execute("INSERT INTO user (UserFname, UserLname,\
                                              UserPassword, UserEmail) VALUES (%s, %s, %s, %s)", (UserFname, UserLname, UserPassword, UserEmail))

                            getUserID = "SELECT UserID FROM user WHERE UserEmail = %s;"
                            dbcursor.execute(getUserID, (UserEmail,))
                            UserID = dbcursor.fetchone()
                            UserID = UserID[0]
                            session['UserID'] = UserID

                            conn.commit()  #save db             
                            dbcursor.close()    #close db
                            conn.close()    #close conn
                            gc.collect()
                            session['logged_in'] = True     #session variables
                            session['UserEmail'] = UserEmail
                            session['UserType'] = 'standard'   #default all users are standard

                            

                            
                            return redirect(url_for("homepage"))                       

                    else:                        
                        print("Connection error")
                        return "DB Connection Error"
                else:                    
                    print("Connection error")
                    return "DB Connection Error"
            else:                
                print("empty parameters")
                return render_template("register.html", error=error, usertype = session['UserType'])
        else:            
            return render_template("register.html", error=error, usertype = session['UserType']) 
    except Exception as e:                
        return render_template("register.html", error=e, usertype = session['UserType'] )    
    

#RENDERS THE LOGIN PAGE AND WILL LOG THE USER IN IF THE CORRECT DETAILS ARE SUBMITTED
@app.route('/login/', methods=["GET","POST"])
def login():
    form={}
    error = ''
    try:	
        if request.method == "POST":            
            UserEmail = request.form['UserEmail']
            UserPassword = request.form['UserPassword']            
            form = request.form
            print('login start')
            
            if UserEmail != None and UserPassword != None:  #check if un or pw is none          
                conn = get_connection()
                if conn != None:                       
                    if conn.is_connected(): #Checking if connection is established                        
                        print('MySQL Connection is established')                          
                        dbcursor = conn.cursor()    #Creating cursor object                                                 
                        dbcursor.execute("SELECT UserPassword, UserType \
                            FROM user WHERE UserEmail = %s;", (UserEmail,))                                               
                        data = dbcursor.fetchone()
                        #print(data[0])
                        if dbcursor.rowcount < 1: #this mean no user exists                        
                            error = "Email Address or Password is Incorrect."
                            return render_template("login.html", error=error, usertype = session['UserType'], UserEmail = session['UserEmail'])
                        else:                            
                            #data = dbcursor.fetchone()[0] #extracting password   
                            # verify passowrd hash and password received from user                                                             
                            if sha256_crypt.verify(request.form['UserPassword'], str(data[0])):                                
                                session['loggedin'] = True     #set session variables
                                session['UserEmail'] = request.form['UserEmail']
                                session['UserType'] = str(data[1])                          
                                print("You are now logged in")     

                                getUserID = "SELECT UserID FROM user WHERE UserEmail = %s;"
                                dbcursor.execute(getUserID, (UserEmail,))
                                UserID = dbcursor.fetchone()
                                UserID = UserID[0]
                                session['UserID'] = UserID

                                return redirect(url_for("homepage",UserType = session['UserType'] )) 
                            else:
                                error = "Invalid credentials username/password, try again."                               
                    gc.collect()
                    print('login start 1.10')
                    return render_template("login.html", form=form, error=error, usertype = session['UserType'])
    except Exception as e:                
        error = str(e) + " <br/> Invalid credentials, try again."
        return render_template("login.html", form=form, error = error, usertype = session['UserType'])   
    
    return render_template("login.html", form=form, error = error, usertype = session['UserType'])

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:            
            print("You need to login first")
            #return redirect(url_for('login', error='You need to login first'))
            return render_template('login.html', usertype = session['UserType'],UserEmail = session['UserEmail'], error='You need to login first')    
    return wrap

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if (session['UserType'] == 'admin'):
            return f(*args, **kwargs)
        else:            
            print("You need to login first as admin user")
            #return redirect(url_for('login', error='You need to login first as admin user'))
            return render_template('login.html', error='You need to login first as admin user')    
    return wrap





#LOG OUT
@app.route("/logout/")

def logout():    
    session.clear()    #clears session variables
    gc.collect() 
    return redirect(url_for('homepage'))


@app.route('/booking/' , methods=["GET","POST"])
def booking():
            
            global SeatAmount

            if request.method == "POST":
                #print("we are posting")
                session ['DepartureCity'] = request.form['DepartureCity']
                session ['ArrivalCity'] = request.form['ArrivalCity']
                session ['LeaveDate'] = request.form['LeaveDate']      
                session ['ReturnDate'] = request.form['ReturnDate'] 
                session ['SeatAmount'] = int(request.form['SeatAmount'])

                conn = get_connection()
                if conn != None:
                    if conn.is_connected():
                        dbcursor = conn.cursor()
                        getJourneyID = "SELECT JourneyID FROM journey WHERE DepartureCity = %s AND ArrivalCity = %s"
                        dbcursor.execute(getJourneyID,(session['DepartureCity'], session['ArrivalCity']))
                        JourneyID = dbcursor.fetchone()   #fetch the journey ID
                        session['JourneyID'] = (JourneyID)

                return render_template("bookingpart2.html", SeatAmount= session['SeatAmount'], usertype = session['UserType'], UserEmail = session['UserEmail'])


            else:
                conn = get_connection()
                if conn != None:    #Checking if connection is None         
                    print('MySQL Connection is established')                          
                    dbcursor = conn.cursor()    #Creating cursor object            
                    dbcursor.execute('SELECT DISTINCT DepartureCity FROM journey;')   
                    #print('SELECT statement executed successfully.')             
                    rows = dbcursor.fetchall()                                    
                    dbcursor.close()              
                    conn.close() #Close Connection
                    cities = []
                    for city in rows:
                        city = str(city).strip("(")
                        city = str(city).strip(")")
                        city = str(city).strip(",")
                        city = str(city).strip("'")
                        cities.append(city)
                    return render_template('booking2.html', DepartureCity=cities, usertype = session['UserType'], UserEmail = session['UserEmail'])
                else:
                    print('DB connection Error')
                    return 'DB Connection Error'


@app.route ('/returncity/', methods = ['POST', 'GET'])
def ajax_returncity():   
	print('/returncity') 

	if request.method == 'GET':
		DepartureCity = request.args.get('q')
		conn = get_connection()
		if conn != None:        
			print('MySQL Connection is established')                          
			dbcursor = conn.cursor()          
			dbcursor.execute('SELECT DISTINCT ArrivalCity FROM journey WHERE DepartureCity = %s;', (DepartureCity,))               
			rows = dbcursor.fetchall()
			total = dbcursor.rowcount                                    
			dbcursor.close()              
			conn.close() #Close Connection	
			return jsonify(returncities=rows, size=total)
		else:
			print('DB connection Error')
			return jsonify(returncities='DB Connection Error')
                
@app.route('/bookingpart2/', methods = ["GET","Post"] )

def bookingpart2():
    
    if request.method == "POST":
        session['SeatID'] = list(request.form.values())     #list of all the seats containing multiple IDS
        print("we are here")
        return render_template("paypage.html", usertype = session['UserType'], UserEmail = session['UserEmail'])
        
    else:
        return render_template("bookingpart2.html", SeatAmount= session['SeatAmount'], usertype = session['UserType'], UserEmail = session['UserEmail'])


@app.route('/payment/', methods = ["GET", "POST"])
def payment():
       
    if request.method == "POST":

        Today = date.today()
        JourneyDate = session['LeaveDate']
        UserID = session['UserID']
        JourneyID = session['JourneyID']
        JourneyID = JourneyID[0]

    
        for seat in session['SeatID']:
            conn = get_connection()
            if conn != None:
                print("MySQL Connection is established")
                dbcursor = conn.cursor()
                SeatVerify = "SELECT * FROM booking WHERE SeatID =%s AND JourneyID = %s AND JourneyDate = %s;"
                dbcursor.execute(SeatVerify, ((seat), (JourneyID), (JourneyDate)))
                rows = dbcursor.fetchall()
                if dbcursor.rowcount > 0: #means there is already a booking wfor the seat
                    error = "Seat " + (seat) + " Not Available"
                    return render_template("bookingpart2.html",error = error , SeatAmount= session['SeatAmount'], usertype = session['UserType'], UserEmail = session['UserEmail'])
                else:   #We can register the booking
                    dbcursor.execute("INSERT INTO booking (JourneyID, PurchaseDate, JourneyDate, SeatID, UserID)\
                                    VALUES (%s, %s, %s, %s, %s)", (JourneyID ,  Today, JourneyDate, seat, UserID ))
                    conn.commit()   #save db
                    dbcursor.close()    #close db
                    conn.close()    #close connection
                    gc.collect()

            else:
                return render_template("paypage.html", usertype = session['UserType'], UserEmail = session['UserEmail'])
    
    return redirect(url_for("receipt",SeatAmount = session['SeatAmount'] ,  usertype = session['UserType'], UserEmail = session['UserEmail']))


@app.route('/receipt/')

def receipt():
     
     TotalPrice = 0


     conn = get_connection()
     if conn != None:
         print("MySQL Connection is established")
         dbcursor = conn.cursor()
         getPrice = "SELECT PRICE FROM journey WHERE JourneyID = %s"    # Gets the price from the SQL DB and saves it to variable Price
         dbcursor.execute(getPrice, (session['JourneyID']))
         Price = dbcursor.fetchone()
         Price = Price[0]



     for seat in session['SeatID']:
         

         # if seat is >= 80 its standard, so standard price applys, else its 2x the price

        if int(seat) <= 80:
             TotalPrice = TotalPrice + Price
             
        else:
            TotalPrice = TotalPrice + (Price * 2)
             
     
     return render_template("receipt.html",SeatList = session['SeatID'] ,\
                              usertype = session['UserType'], UserEmail = session['UserEmail'],\
                                Arrival = session['ArrivalCity'], Departure = session['DepartureCity'],\
                                    LeaveDate = session['LeaveDate'], ReturnDate = session['ReturnDate'], Price = TotalPrice)


                


@app.route('/admin/', methods = ["GET", "POST"])
@admin_required

def adminpage():

    message = ""

    conn = get_connection()
    num = date.today().month
    if conn != None:
        if conn.is_connected():
            dbcursor = conn.cursor()
            dbcursor.execute("SELECT * FROM booking WHERE monthname(PurchaseDate) = %s;",(calendar.month_name[num],))
            MonthlySales = dbcursor.fetchall()
            SalesAmount = len(MonthlySales)

            salesmessage = "There were " + str(SalesAmount) + " sales this month."
            
        else:
            salesmessage = ""         



    if request.method == "POST":
        try:
            DepartureCity = request.form['DepartureCity']
            ArrivalCity = request.form['ArrivalCity']
            DepartureTime = request.form['DepartureTime']
            ArrivalTime = request.form['ArrivalTime']

            if DepartureCity != None and ArrivalCity != None:
                conn = get_connection()
                print("Attempting to add journey")
                if conn != None:                       
                    if conn.is_connected():
                        dbcursor = conn.cursor()
                        dbcursor.execute("INSERT INTO journey (DepartureCity, ArrivalCity, DepartureTime, ArrivalTime)\
                                        VALUES (%s, %s, %s, %s)", (DepartureCity, ArrivalCity, DepartureTime, ArrivalTime))
                            
                        conn.commit()
                        dbcursor.close()
                        conn.close()

                        message = "Journey Successfully Added"

                        return render_template("adminpage.html", usertype = session['UserType'], UserEmail = session['UserType'], message = message, salesmessage = salesmessage)
                        
                    else:
                        message = " Failed, Database not connected "
                        return render_template("adminpage.html", usertype = session['UserType'], UserEmail = session['UserType'], message = message, salesmessage = salesmessage)
                else:
                    message = " Failed, Database not connected "
                    return render_template("adminpage.html", usertype = session['UserType'], UserEmail = session['UserType'], message = message, salesmessage = salesmessage)
            
                    
        except:
            try:
                JourneyID = int(request.form['JourneyID'])
                

                if JourneyID != None:
                    conn = get_connection()
                    print("Attempting to delete journey")
                    if conn != None:                      
                        if conn.is_connected():
                            print("connection success") 
                            dbcursor = conn.cursor()
                            dbcursor.execute("DELETE FROM journey WHERE JourneyID = %s",(JourneyID,))
                                
                            conn.commit()
                            dbcursor.close()
                            conn.close()

                            message = "Journey Successfully Removed"

                            return render_template("adminpage.html", usertype = session['UserType'], UserEmail = session['UserType'], message = message, salesmessage = salesmessage)
        
            except:
                
                try:
                    UserEmail = request.form['UserEmail']

                    if UserEmail != None:
                        conn = get_connection()
                        print("attempting to delete account")
                        if conn != None:                       
                            if conn.is_connected():
                                dbcursor = conn.cursor()
                                print("connection")
                                dbcursor.execute("DELETE FROM user  WHERE UserEmail = %s",(UserEmail,))
                                    
                                conn.commit()
                                dbcursor.close()
                                conn.close()

                                message = "Account Successfully Removed"

                                return render_template("adminpage.html", usertype = session['UserType'], UserEmail = session['UserType'], message = message, salesmessage = salesmessage)
                except:
                    message = ""
                    return render_template("adminpage.html", usertype = session['UserType'], UserEmail = session['UserType'], message = message, salesmessage = salesmessage)
    else:
        return render_template("adminpage.html", usertype = session['UserType'], UserEmail = session['UserType'], message = message, salesmessage = salesmessage)
        
                
        
@app.route('/account/', methods = ["GET", "POST"])


def account():

    JourneyList = ["0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0",]
    DepartureCityList = ["0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0",]
    ArrivalCityList = ["0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0",]
    DateList = ["0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0",]
    TimeList = ["0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0",]
    SeatList = ["0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0",]

    conn = get_connection()
    if conn != None:
        if conn.is_connected():
            dbcursor = conn.cursor()
            dbcursor.execute("SELECT BookingID FROM booking WHERE UserID = %s", (session['UserID'],))
            bookings = dbcursor.fetchall()
            bookings = [value for sublist in bookings for value in sublist] #formats the data from a double list to a single list


            for id in bookings:

                int(id)

                dbcursor.execute("SELECT JourneyID FROM booking WHERE BookingID =%s", (id,))
                JourneyID = dbcursor.fetchone()
                JourneyID = str(JourneyID[0])
                JourneyList.insert(id, JourneyID)

                dbcursor.execute("SELECT SeatID FROM booking WHERE BookingID =%s", (id,))
                SeatID = dbcursor.fetchone()
                SeatID = (SeatID[0])
                SeatList.insert(id, SeatID)

                dbcursor.execute("SELECT DepartureCity FROM journey WHERE JourneyID =%s", (JourneyID,))
                DepartureCity = dbcursor.fetchone()
                DepartureCity = DepartureCity[0]
                DepartureCityList.insert(id, DepartureCity)

                dbcursor.execute("SELECT ArrivalCity FROM journey WHERE JourneyID =%s", (JourneyID,))
                ArrivalCity = dbcursor.fetchone()
                ArrivalCity = ArrivalCity[0]
                ArrivalCityList.insert(id, ArrivalCity)
                
                dbcursor.execute("SELECT JourneyDate FROM booking WHERE BookingID =%s", (id,))
                JourneyDate = dbcursor.fetchone()
                JourneyDate = str(JourneyDate[0])
                DateList.insert(id, JourneyDate)

                dbcursor.execute("SELECT DepartureTime FROM journey WHERE JourneyID =%s", (JourneyID,))
                DepartureTime = dbcursor.fetchone()
                DepartureTime = str(DepartureTime[0])
                TimeList.insert(id, DepartureTime)

            dbcursor.close()
            conn.close()
            message = ""

            if request.method == "POST":
                seatid = request.form['cancelid']
                UserID = session['UserID']

                if seatid != None:
                   conn = get_connection()
                   if conn != None:
                       if conn.is_connected():
                           dbcursor = conn.cursor()
                           verify = "SELECT BookingID FROM booking WHERE UserID = %s AND SeatID = %s;"
                           dbcursor.execute(verify, ((UserID),(seatid)))
                           rows = dbcursor.fetchall()
                           if dbcursor.rowcount == 0:   #The user did not book this SeatID
                               message = "User did not book this seat"
                               return render_template ("myaccount.html", usertype = session['UserType'], UserEmail = session['UserType'],bookings = bookings\
                                    , JourneyList = JourneyList, DepartureCityList = DepartureCityList, ArrivalCityList = ArrivalCityList\
                                        , DateList = DateList, TimeList = TimeList, SeatList = SeatList, message = message )
                           else:
                               dbcursor.execute("DELETE FROM booking WHERE SeatID = %s",(seatid,))
                               conn.commit()
                               dbcursor.close()
                               conn.close()

                               message = "The booking for SeatID: " + (seatid) + " has been cancelled. Your bank account will be refunded"

                               return render_template ("myaccount.html", usertype = session['UserType'], UserEmail = session['UserType'],bookings = bookings\
                                    , JourneyList = JourneyList, DepartureCityList = DepartureCityList, ArrivalCityList = ArrivalCityList\
                                        , DateList = DateList, TimeList = TimeList, SeatList = SeatList, message = message )

            

            return render_template ("myaccount.html", usertype = session['UserType'], UserEmail = session['UserType'],bookings = bookings\
                                    , JourneyList = JourneyList, DepartureCityList = DepartureCityList, ArrivalCityList = ArrivalCityList\
                                        , DateList = DateList, TimeList = TimeList, SeatList = SeatList, message = message )




    return render_template ("myaccount.html", usertype = session['UserType'], UserEmail = session['UserType'])



if __name__ == "__main__":
    app.run (debug=True ,host = "127.0.0.1", port = 5050)