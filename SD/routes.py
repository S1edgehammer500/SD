from flask import Flask, render_template, request, flash, session, jsonify
from passlib.hash import sha256_crypt
import hashlib
import gc
from functools import wraps
from datetime import datetime, timedelta, date
import calendar
from Model.Database import *
from flask import redirect, url_for
from Model.userModel import *
from Model.restaurantModel import *

# User defined
import strip

app = Flask(__name__)
app.secret_key = 'SK'

@app.route("/")
@app.route('/login/', methods=["GET","POST"])
def login():
    session.clear()
    gc.collect()
    if "logged_in" in session and "authLevel" in session:
        logged_in = session['logged_in']
        authLevel = session['authLevel']
    else:
        logged_in = False
        authLevel = 'staff'

    form={}
    error = ''

    try:	
        if request.method == "POST":            
            code = request.form['code']
            password = request.form['password']            
            form = request.form
            currentUser = User()
            print(str(code))
            print(str(password))
            
            if code != None and password != None:         
                if currentUser.checkCodePassword(code, password) == 0:
                    #no record of this user exists                         
                    error = "User / password does not exist or password is incorrect, login again"
                    return render_template("login.html", error=error, title="Login")
                else:
                    print("Query successful")                          

                    # verify passowrd hash and password received from user                                                           
                    print("Logged in")     
                    currentUser.setLoginDetails(code, password) 
                    authLevel = currentUser.getAuthorisation()                  
                          
                    #set session variable
                    session['logged_in'] = True
                    session['authLevel'] = authLevel                        
                    flash("You are now logged in", "success")                               
                    return redirect(url_for('home'))                            
            else:
                flash("You have entered no details", "danger")
                error = "No details entered"
                return render_template("login.html", form=form, error=error, title="Login", logged_in=logged_in, authLevel=authLevel)
    except Exception as e:                
        error = str(e) + " <br/> Invalid credentials, try again."
        return render_template("login.html", form=form, error=error, title="Login", logged_in=logged_in, authLevel=authLevel)   
    
    return render_template("login.html", form=form, error=error, title="Login", logged_in=logged_in, authLevel=authLevel)


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to be logged in to access this page", "danger")
            return render_template('login.html', title="Login")
    return wrap 

@app.route("/home.html/")
@login_required
def home():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    return render_template('home.html', title="Home", logged_in=logged_in, authLevel=authLevel)

@app.route('/createUser/', methods=['POST', 'GET'])
@login_required
def createUser():
    currentUser = User()
    restaurant = Restaurant()
    restaurants = []
    tempRestaurants = restaurant.getAllRestaurants()

    restaurants = strip.it(tempRestaurants)

    logged_in = session['logged_in']
    authLevel = session['authLevel']


    error = ''
    currentUser = User()
    if session['authLevel'] != 'admin':
        flash("You need to be an admin to access this page", "danger")
        return redirect(url_for('home'))
    else:
        try:
            if request.method == "POST": 
                #getting data from form        
                code = request.form['code']
                tempBR = request.form['base']
                print(str(tempBR)) 
                AL = request.form['auth']
                password = request.form['password']
                confirmPassword = request.form['confirmPassword']                    
                if code != None and tempBR != None and password != None and confirmPassword != None and confirmPassword == password:
                    if currentUser.validateUserpasswordSyntax(password) == 1:
                        if currentUser.validateCodeSyntax(code) == 1:
                            print(str(tempBR))
                            BR = restaurant.getRestaurantIDFromName(tempBR)
                            print(str(tempBR))
                            print(str(BR))
                            if currentUser.saveUserDetails(code, password, AL, BR) == 1:                      
                                flash("Account is now registered", "success")
                                return redirect(url_for('home'))
                            else:
                                return render_template('createUser.html', error=error, title="Create User", logged_in=logged_in, authLevel=authLevel, restaurants=restaurants)
                        else:
                            return render_template('createUser.html', error=error, title="Create User", logged_in=logged_in, authLevel=authLevel, restaurants=restaurants)
                    else:
                        return render_template('createUser.html', error=error, title="Create User", logged_in=logged_in, authLevel=authLevel, restaurants=restaurants)
                else:                
                    flash("Password and Confirm Password fields need to match", "danger")
                    print("Passwords don't match")
                    return render_template('createUser.html', error=error, title="Create User", logged_in=logged_in, authLevel=authLevel, restaurants=restaurants)
            else:            
                return render_template('createUser.html', error=error, title="Create User", logged_in=logged_in, authLevel=authLevel, restaurants=restaurants)        
        except Exception as e:                
            return render_template('createUser.html', error=e, title="Create User", logged_in=logged_in, authLevel=authLevel, restaurants=restaurants)
    
@app.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("You have been logged out", "success")
    gc.collect()
    return render_template('login.html', title='Login')

@app.route("/userOptions/")
@login_required
def userOptions():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    return render_template('userOptions.html', title="User Options", logged_in=logged_in, authLevel=authLevel)

@app.route("/updateUser/", methods=['GET', 'POST'])
@login_required
def updateUser():
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    currentUser = User()
    if session['authLevel'] != 'admin':
        flash("You need to be an admin to access this page", "danger")
        return redirect(url_for('home'))
    else:
        baseRestaurant = []
        tempBaseRestaurant = currentUser.getBaseRestaurants()
        baseRestaurant = strip.it(tempBaseRestaurant)

        authorisationLevel = []
        tempAuthorisationLevel = currentUser.getAuthorisationLevels()
        authorisationLevel = strip.it(tempAuthorisationLevel)

        employeeCode = []
        tempEmployeeCode = currentUser.getEmployeeCodes()
        employeeCode = strip.it(tempEmployeeCode)

    return render_template('updateUser.html', title = "Update User", logged_in=logged_in, authLevel=authLevel, baseRestaurant=baseRestaurant, authorisationLevel=authorisationLevel, employeeCode=employeeCode, codeLen=len(employeeCode))
    
@app.route("/updateUser2/", methods=['GET', 'POST'])
@login_required
def updateUser2():
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    currentUser = User()
    if session['authLevel'] != 'admin':
        flash("You need to be an admin to access this page", "danger")
        return redirect(url_for('home'))
    else:
        if request.method == ['POST']:
            code = request.form['code']

            AL = currentUser.getSpecificAuthorisationLevel(code)
            AL = strip.it(AL)

            BR = currentUser.getSpecificBaseRestaurant(code)
            BR = strip.it(BR)

            return render_template("updateUser2.html", title = "Update User", logged_in=logged_in, authLevel=authLevel, AL=AL, BR=BR, code=code)
        
if __name__ == "__main__":
    app.run( debug=True ,host="127.0.0.1", port=5050)