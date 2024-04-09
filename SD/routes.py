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

# Wrappers

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to be logged in to access this page", "danger")
            return render_template('login.html', title="Login")
    return wrap 

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'authLevel' in session:
            if session['authLevel'] == 'admin':
                return f(*args, **kwargs)
            else:
                flash("You need to be logged in as an admin to access this page", "danger")
                return redirect(url_for('home'))
        else:
            flash("You need to be logged in to access this page", "danger")
            return render_template('login.html', title="Login")
    return wrap



# Routes

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
                    flash("User does not exist", "danger")
                    return render_template("login.html", error=error, title="Login")
                else:
                    print("Query successful")                          

                    # verify passowrd hash and password received from user                                                           
                    print("Logged in")     
                    currentUser.setLoginDetails(code) 
                    authLevel = currentUser.getAuthorisation()   

                            
                    #set session variable
                    session['logged_in'] = True
                    session['authLevel'] = authLevel
                    session['code'] = code    
                                        
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


@app.route("/home.html/")
@login_required
def home():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    return render_template('home.html', title="Home", logged_in=logged_in, authLevel=authLevel)

@app.route('/createUser/', methods=['POST', 'GET'])
@login_required
@admin_required
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
                            flash("Invalid username syntax", "danger")
                            return render_template('createUser.html', error=error, title="Create User", logged_in=logged_in, authLevel=authLevel, restaurants=restaurants)
                    else:
                        flash("Invalid password syntax", "danger")
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

@app.route("/deleteUser/", methods=['GET', 'POST'])
@login_required
@admin_required
def deleteUser():
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    currentUser = User()
    currentUser.setLoginDetails(session['code'])

    employeeCode = []
    tempEmployeeCode = currentUser.getEmployeeCodes()
    employeeCode = strip.it(tempEmployeeCode)


    baseRestaurant = []
    tempBaseRestaurant = currentUser.getBaseRestaurants()
    baseRestaurant = strip.it(tempBaseRestaurant)

    authorisationLevel = []
    tempAuthorisationLevel = currentUser.getAuthorisationLevels()
    authorisationLevel = strip.it(tempAuthorisationLevel)

    return render_template('deleteUser.html', title = "Delete User", logged_in=logged_in, authLevel=authLevel, baseRestaurant=baseRestaurant, authorisationLevel=authorisationLevel, employeeCode=employeeCode, codeLen=len(employeeCode))

@app.route("/deleteUser2/", methods=['GET', 'POST'])
@login_required
def deleteUser2():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    currentUser = User()

    try:
        if request.method == "POST":
            # Code that you wanna delete
            code = request.form['code']

            # Users code. DON'T DELETE
            usercode = session['code']

            if code != usercode:
                if currentUser.deleteUser(code):
                    flash(f"You have successfully deleted the user {code}", 'info')
                    return redirect(url_for('userOptions'))
                else:
                    flash(f"Account \"{code}\" does not exist", 'danger')
                    return redirect(url_for('deleteUser'))
            else:
                flash("You cannot delete your own user", "danger")
                return redirect(url_for('deleteUser'))
    except Exception as e:  
        return render_template('userOptions.html', error=e, title="User Options", logged_in=logged_in, authLevel=authLevel)

@app.route("/updateUser/", methods=['GET', 'POST'])
@login_required
def updateUser():
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    currentUser = User()
    currentUser.setLoginDetails(session['code'])

    employeeCode = []
    tempEmployeeCode = currentUser.getEmployeeCodes()
    employeeCode = strip.it(tempEmployeeCode)


    baseRestaurant = []
    tempBaseRestaurant = currentUser.getBaseRestaurants()
    baseRestaurant = strip.it(tempBaseRestaurant)

    authorisationLevel = []
    tempAuthorisationLevel = currentUser.getAuthorisationLevels()
    authorisationLevel = strip.it(tempAuthorisationLevel)

    return render_template('updateUser.html', title = "Update User", logged_in=logged_in, authLevel=authLevel, baseRestaurant=baseRestaurant, authorisationLevel=authorisationLevel, employeeCode=employeeCode, codeLen=len(employeeCode))
    
@app.route("/updateUser2/", methods=['GET', 'POST'])
@login_required
@admin_required
def updateUser2():
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    currentUser = User()
    restaurant = Restaurant()
    restaurants = []
    tempRestaurants = restaurant.getAllRestaurants()

    restaurants = strip.it(tempRestaurants)


    if request.method == "POST":
        code = request.form['code']

        session['code'] = code

        AL = currentUser.getSpecificAuthorisationLevel(code)
        AL = strip.it(AL)[0]

        BR = currentUser.getSpecificBaseRestaurant(code)
        # BR comes back as a string so make sure to make it an int before using
        BR = strip.it(BR)[0]

        print(BR)
        print(AL)


        return render_template("updateUser2.html", title = "Update User", logged_in=logged_in, authLevel=authLevel, AL=AL, BR=BR, code=code, restaurants=restaurants, restaurantLen=len(restaurants))
    
    return render_template("updateUser2.html", title = "Update User", logged_in=logged_in, authLevel=authLevel, restaurants=restaurants)


@app.route("/updateUser3/", methods=['GET', 'POST'])
@login_required
@admin_required
def updateUser3():
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    currentUser = User()
    restaurant = Restaurant()
    restaurants = []
    tempRestaurants = restaurant.getAllRestaurants()

    restaurants = strip.it(tempRestaurants)

    

    try:
        if request.method == "POST":
            
            code = request.form['code']
            base = restaurant.getRestaurantIDFromName(request.form['base'])
            auth = request.form['auth']
            print(base)



            if code != None and base != None and auth != None:
    
                if currentUser.validateCodeSyntax(code) == 1:
        
                    if currentUser.validateAuthorisationSyntax(auth) == 1:
            
                        if currentUser.validateBaseRestaurantSyntax(base) == 1:
                

                            previousCode = session['code']
                            
                            currentUser.updateBaseRestaurant(previousCode, base)
                            currentUser.updateAuthorisation(previousCode, auth)
                            print(code)
                            print(previousCode)
                            if code != previousCode:
                                currentUser.updateCode(previousCode, code)

                            flash(f"You have successfully updated the user {code}", 'info')
                            return redirect(url_for('userOptions'))
                        else:
                            flash("There's something wrong", "error")
                            return render_template('updateUser2.html', error="", title = "Update User", logged_in=logged_in, authLevel=authLevel, restaurants=restaurants)
                    else:
                        return render_template('updateUser2.html', error="", title = "Update User", logged_in=logged_in, authLevel=authLevel, restaurants=restaurants)
                else:
                    return render_template('updateUser2.html', error="", title = "Update User", logged_in=logged_in, authLevel=authLevel, restaurants=restaurants)
            else:                
                flash("Please don't leave any field empty", "danger")
                return render_template('updateUser2.html', error="", title = "Update User", logged_in=logged_in, authLevel=authLevel, restaurants=restaurants)
    except Exception as e:                
        return render_template('updateUser2.html', error=e, title = "Update User", logged_in=logged_in, authLevel=authLevel, restaurants=restaurants)
        
if __name__ == "__main__":
    app.run( debug=True ,host="127.0.0.1", port=5050)