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
from Model.discountModel import *

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

    try:
        if request.method == "POST": 
            #getting data from form        
            code = request.form['code']
            BR = request.form['base']
            print(str(BR)) 
            AL = request.form['auth']
            password = request.form['password']
            confirmPassword = request.form['confirmPassword']                    
            if code != None and BR != None and password != None and confirmPassword != None and confirmPassword == password:
                if currentUser.validateUserpasswordSyntax(password) == 1:
                    if currentUser.validateCodeSyntax(code) == 1:
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
                    flash("Invalid username syntax", "danger")
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

@app.route("/adminOptions/")
@login_required
def adminOptions():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    return render_template('adminOptions.html', title="Admin Options", logged_in=logged_in, authLevel=authLevel)


@app.route("/menu/")
@login_required
def menu():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    return render_template('menu.html', title="Menu", logged_in=logged_in, authLevel=authLevel)

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
@admin_required
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
                    return redirect(url_for('adminOptions'))
                else:
                    flash(f"Account \"{code}\" does not exist", 'danger')
                    return redirect(url_for('deleteUser'))
            else:
                flash("You cannot delete your own user", "danger")
                return redirect(url_for('deleteUser'))
    except Exception as e:  
        return render_template('adminOptions.html', error=e, title="User Options", logged_in=logged_in, authLevel=authLevel)

@app.route("/updateUser/", methods=['GET', 'POST'])
@login_required
@admin_required
def updateUser():
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    currentUser = User()
    currentUser.setLoginDetails(session['code'])

    BR = currentUser.getBaseRestaurant()
    AL = currentUser.getAuthorisation()

    employeeCode = []
    tempEmployeeCode = currentUser.getEmployeeCodes()
    employeeCode = strip.it(tempEmployeeCode)
    print(employeeCode)
    employeeCode.append(session['code'])


    baseRestaurant = []
    tempBaseRestaurant = currentUser.getBaseRestaurants()
    baseRestaurant = strip.it(tempBaseRestaurant)
    baseRestaurant.append(BR)
    print(baseRestaurant)

    authorisationLevel = []
    tempAuthorisationLevel = currentUser.getAuthorisationLevels()
    authorisationLevel = strip.it(tempAuthorisationLevel)
    authorisationLevel.append(AL)
    print(authorisationLevel)
    print(AL)

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
        session['previousCode'] = code
        currentUser.setLoginDetails(session['previousCode'])

        AL = currentUser.getAuthorisation()

        BR = currentUser.getBaseRestaurant()

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
            base = request.form['base']
            auth = request.form['auth']
            print(base)



            if code != None and base != None and auth != None:
    
                if currentUser.validateCodeSyntax(code) == 1:
        
                    if currentUser.validateAuthorisationSyntax(auth) == 1:
            
                        if currentUser.validateBaseRestaurantSyntax(base) == 1:
                

                            previousCode = session['previousCode']
                            
                            currentUser.updateBaseRestaurant(previousCode, base)
                            currentUser.updateAuthorisation(previousCode, auth)
                            print(code)
                            print(previousCode)
                            if code != previousCode:
                                currentUser.updateCode(previousCode, code)
                                if previousCode == session['code']:
                                    session['code'] = code

                            flash(f"You have successfully updated the user {code}", 'info')
                            return redirect(url_for('adminOptions'))
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
    
#Beggining of restaurant crud

@app.route("/restaurantOptions/")
@login_required
def restaurantOptions():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    return render_template('restaurantOptions.html', title="Restaurant Options", logged_in=logged_in, authLevel=authLevel)

@app.route('/createRestaurant/', methods=['POST', 'GET'])
@login_required
@admin_required
def createRestaurant():
    restaurant = Restaurant()
    restaurants = []
    tempRestaurants = restaurant.getAllRestaurants()

    restaurants = strip.it(tempRestaurants)

    logged_in = session['logged_in']
    authLevel = session['authLevel']


    error = ''

    try:
        if request.method == "POST": 
            #getting data from form        
            restaurantName = request.form['restaurantName']
            numberOfTables = request.form['numberOfTables']
            print(str(numberOfTables))                   
            if restaurantName != None and numberOfTables != None:
                if restaurant.checkRestaurantName(restaurantName) != 1:
                    if restaurant.validateRestaurantSyntax(restaurantName) == 1:
                        if restaurant.validateTableNumberSyntax(numberOfTables) == 1:
                            print(str(numberOfTables))
                            if restaurant.createRestaurant(restaurantName, numberOfTables) == 1:                      
                                flash("Restaurant is now registered", "success")
                                return redirect(url_for('home'))
                            else:
                                flash("Invalid restaurant syntax", "danger")
                                return render_template('createRestaurant.html', error=error, title="Create Restaurant", logged_in=logged_in, authLevel=authLevel, restaurants=restaurants)
                        else:
                            flash("Invalid table number", "danger")
                            return render_template('createRestaurant.html', error=error, title="Create Restaurant", logged_in=logged_in, authLevel=authLevel, restaurants=restaurants)
                    else:
                        flash("Invalid resaurant syntax", "danger")
                        return render_template('createRestaurant.html', error=error, title="Create Restaurant", logged_in=logged_in, authLevel=authLevel, restaurants=restaurants)
                else:
                    flash("Restaurant name already exists", "danger")
                    print("Restaurant name exists")
                    return render_template('createRestaurant.html', error=error, title="Create Restaurant", logged_in=logged_in, authLevel=authLevel, restaurants=restaurants)
            else:                
                flash("Fields cannot be empty", "danger")
                print("Passwords don't match")
                return render_template('createRestaurant.html', error=error, title="Create Restaurant", logged_in=logged_in, authLevel=authLevel, restaurants=restaurants)
        else:            
            return render_template('createRestaurant.html', error=error, title="Create Restaurant", logged_in=logged_in, authLevel=authLevel, restaurants=restaurants)        
    except Exception as e:                
        return render_template('createRestaurant.html', error=e, title="Create Restaurant", logged_in=logged_in, authLevel=authLevel, restaurants=restaurants)


@app.route("/deleteRestaurant/", methods=['GET', 'POST'])
@login_required
@admin_required
def deleteRestaurant():
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    restaurant = Restaurant()
    
    restaurantName = []
    tempRestaurantName = restaurant.getAllRestaurants()
    restaurantName = strip.it(tempRestaurantName)

    numberOfTables = []
    tempNumberOfTables= [tables[1] for tables in restaurant.get_restaurants()]
    numberOfTables = strip.it(tempNumberOfTables)

    return render_template('deleteRestaurant.html', title = "Delete Restaurant", logged_in=logged_in, authLevel = authLevel, restaurantName=restaurantName, numberOfTables=numberOfTables, restaurantNameLen=len(restaurantName))


@app.route("/deleteRestaurant2/", methods=['GET', 'POST'])
@login_required
@admin_required
def deleteRestaurant2():
    print("in this function")
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    currentUser = User()
    restaurant = Restaurant()
    
    try:
        if request.method == "POST":
            # Restaurant name that you wanna delete
            restaurantName = request.form['restaurantName']

            # Users code. DON'T DELETE
            #restaurantName = session['code']
            currentUserRestaurant = currentUser.getBaseRestaurant()
            print(restaurantName)
            print(currentUserRestaurant)
            if restaurantName != currentUserRestaurant:
                if restaurant.deleteRestaurant(restaurantName):
                    flash(f"You have successfully deleted the restaurant {restaurantName}", 'info')
                    return redirect(url_for('adminOptions'))
                else:
                    flash(f"Restaurant \"{restaurantName}\" does not exist", 'danger')
                    return redirect(url_for('deleteRestaurant'))
            else:
                flash("You cannot delete your own restaurant", "danger")
                return redirect(url_for('deleteRestaurant'))
    except Exception as e:  
        return render_template('adminOptions.html', error=e, title="Restaurant Options", logged_in=logged_in, authLevel=authLevel)

@app.route("/updateRestaurant/", methods=['GET', 'POST'])
@login_required
@admin_required
def updateRestaurant():
    
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    restaurant = Restaurant()
    
    restaurantName = []
    tempRestaurantName = restaurant.getAllRestaurants()
    restaurantName = strip.it(tempRestaurantName)

    numberOfTables = []
    tempNumberOfTables= [tables[1] for tables in restaurant.get_restaurants()]
    numberOfTables = strip.it(tempNumberOfTables)

    
    return render_template('updateRestaurant.html', title = "Update Restaurant", logged_in=logged_in, authLevel = authLevel, restaurantName=restaurantName, numberOfTables=numberOfTables, restaurantNameLen=len(restaurantName))

@app.route("/updateRestaurant2/", methods=['GET', 'POST'])
@login_required
@admin_required
def updateRestaurant2():
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    restaurant = Restaurant()

    if request.method == "POST":
        
        restaurantName = request.form['restaurantName']
        
        session['previousRestaurantName'] = restaurantName
        
        restaurant.setRestaurantDetails(session['previousRestaurantName'])
        
        numberOfTables = int(restaurant.getNumberOfTables())
        
        return render_template("updateRestaurant2.html", title = "Update Restaurant", logged_in=logged_in, authLevel=authLevel,restaurantName=restaurantName, numberOfTables=numberOfTables, restaurantNameLen=len(restaurantName))
    
    return render_template("updateRestaurant2.html", title = "Update Restaurant", logged_in=logged_in, authLevel=authLevel)

@app.route("/updateRestaurant3/", methods=['GET', 'POST'])
@login_required
@admin_required
def updateRestaurant3():
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    restaurant = Restaurant()

    try:
        if request.method == "POST":
            
            restaurantName = request.form['restaurantName']
            numberOfTables = request.form['numberOfTables']

            if restaurantName != None and numberOfTables != None:
                if session["previousRestaurantName"] == restaurantName:
                    if restaurant.updateNumberOfTables(restaurantName, numberOfTables):
                        flash(f"You have successfully updated the restaurant {restaurantName}", 'info')
                        return redirect(url_for('adminOptions'))
                    else:
                        flash("Invalid table number syntax", "danger")
                        return render_template('updateRestaurant2.html', error="", title = "Update Restaurant", logged_in=logged_in, authLevel=authLevel)
                    
                    
                if restaurant.updateRestaurantName(session['previousRestaurantName'], restaurantName):
                    
                    if restaurant.updateNumberOfTables(restaurantName, numberOfTables):
                        pass
                    else:
                        flash("Invalid table number syntax", "danger")
                        return render_template('updateRestaurant2.html', error="", title = "Update Restaurant", logged_in=logged_in, authLevel=authLevel)
                    
                else:
                    if restaurant.checkRestaurantName(restaurantName) == 1: #0 means it doesnt exist 1 means it does
                        flash("Restaurant already exists", "danger")
                        return render_template('updateRestaurant2.html', error="", title = "Update Restaurant", logged_in=logged_in, authLevel=authLevel)
                    elif restaurant.validateRestaurantSyntax(restaurantName) == 0:
                        flash("Invalid restaurant syntax", "danger")
                        return render_template('updateRestaurant2.html', error="", title = "Update Restaurant", logged_in=logged_in, authLevel=authLevel)
                    
                flash(f"You have successfully updated the restaurant {restaurantName}", 'info')
                return redirect(url_for('adminOptions'))

            else:                
                flash("Please don't leave any field empty", "danger")
                return render_template('updateRestaurant2.html', error="", title = "Update Restaurant", logged_in=logged_in, authLevel=authLevel)
    except Exception as e:                
        return render_template('updateRestaurant2.html', error=e, title = "Update Restaurant", logged_in=logged_in, authLevel=authLevel)


#Beggining of discount crud

@app.route("/discountOptions/")
@login_required
def discountOptions():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    return render_template('discountOptions.html', title="Restaurant Options", logged_in=logged_in, authLevel=authLevel)

@app.route('/createDiscount/', methods=['POST', 'GET'])
@login_required
def createDiscount():
    discount = Discount()

    logged_in = session['logged_in']
    authLevel = session['authLevel']


    error = ''

    try:
        if request.method == "POST": 
            #getting data from form        
            discountID = request.form['discountID']
            discountValue = request.form['discountValue']

                 
            if discountID != None and discountValue != None:
                if discount.checkDiscountValue(discountValue) != 1:
                    if discount.validateDiscountIDSyntax(discountID) == 1:
                        if discount.validateDiscountValueSyntax(discountValue) == 1:
        

                            if discount.createDiscount(discountID, discountValue) == 1:                      
                                flash("Discount is now registered", "success")
                                return redirect(url_for('discountOptions'))
                            else:
                                flash("Unexpected Error occured", "danger")
                                return render_template('discountOptions.html', error=error, title="Discount Options", logged_in=logged_in, authLevel=authLevel)
                        else:
                            flash("Invalid discount value", "danger")
                            return render_template('createDiscount.html', error=error, title="Create Discount", logged_in=logged_in, authLevel=authLevel)
                    else:
                        flash("Invalid Discount ID syntax", "danger")
                        return render_template('createDiscount.html', error=error, title="Create Discount", logged_in=logged_in, authLevel=authLevel)
                else:
                    flash("Discount already exists", "danger")
                    print("Discount exists")
                    return render_template('createDiscount.html', error=error, title="Create Discount", logged_in=logged_in, authLevel=authLevel)
            else:                
                flash("Fields cannot be empty", "danger")
                return render_template('createDiscount.html', error=error, title="Create Discount", logged_in=logged_in, authLevel=authLevel)
        else:            
            return render_template('createDiscount.html', error=error, title="Create Discount", logged_in=logged_in, authLevel=authLevel)        
    except Exception as e:                
        return render_template('createDiscount.html', error=e, title="Create Discount", logged_in=logged_in, authLevel=authLevel)


@app.route("/deleteDiscount/", methods=['GET', 'POST'])
@login_required
def deleteDiscount():
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    discount = Discount()
    

    return render_template('deleteDiscount.html', title = "Delete Discount", logged_in=logged_in, authLevel = authLevel)#, restaurantName=restaurantName, numberOfTables=numberOfTables, restaurantNameLen=len(restaurantName))



@app.route("/updateDiscount/", methods=['GET', 'POST'])
@login_required
def updateDiscount():
    
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    discount = Discount()


  
    return render_template('updateDiscount.html', title = "Update Discount", logged_in=logged_in, authLevel = authLevel)#, restaurantName=restaurantName, numberOfTables=numberOfTables, restaurantNameLen=len(restaurantName))


if __name__ == "__main__":
    app.run( debug=True ,host="127.0.0.1", port=5050)