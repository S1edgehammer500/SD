from flask import Flask, render_template, request, flash, session, jsonify, make_response
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
from Model.menuModel import *
from Model.foodModel import *
from Model.reportModel import *
from Model.inventoryModel import *
from Model.itemModel import *
from Model.reservationModel import *
from Model.ordersModel import *
import pdfkit
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

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

def chef_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'authLevel' in session:
            if session['authLevel'] == 'chef' or session['authLevel'] == 'admin' or session['manager']:
                return f(*args, **kwargs)
            else:
                flash("You need to be logged in as a chef or admin to access this page", "danger")
                return redirect(url_for('home'))
        else:
            flash("You need to be logged in to access this page", "danger")
            return render_template('login.html', title="Login")
    return wrap

def manager_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'authLevel' in session:
            if session['authLevel'] == 'manager' or session['authLevel'] == 'admin':
                return f(*args, **kwargs)
            else:
                flash("You need to be logged in as a manager or admin to access this page", "danger")
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

@app.route("/qrcode/")
def qrcode():
    
    return render_template('qrcode.html', title="QRcode Scanner")

@app.route("/ourMenu/")
def ourMenu():

    restaurantName = request.args.get('q')

    menu = Menu()

    todayMenu = menu.getAvailableMenuList(restaurantName)
    

    
    return render_template('ourMenu.html', title="Our Menu", menu=todayMenu, listLen=len(todayMenu[0]))



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
                            return redirect(url_for('admin'))
                        else:
                            flash("User already exists", "danger")
                            return render_template('createUser.html', error=error, title="Create User", logged_in=logged_in, authLevel=authLevel, restaurants=restaurants)
                    else:
                        flash("Invalid username syntax", "danger")
                        return render_template('createUser.html', error=error, title="Create User", logged_in=logged_in, authLevel=authLevel, restaurants=restaurants)
                else:
                    flash("Invalid passowrd syntax", "danger")
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
    if session['authLevel'] == 'admin':
        print(employeeCode)
        employeeCode.append(session['code'])


    baseRestaurant = []
    tempBaseRestaurant = currentUser.getBaseRestaurants()
    baseRestaurant = strip.it(tempBaseRestaurant)
    if session['authLevel'] == 'admin':
        baseRestaurant.append(BR)
        print(baseRestaurant)

    authorisationLevel = []
    tempAuthorisationLevel = currentUser.getAuthorisationLevels()
    authorisationLevel = strip.it(tempAuthorisationLevel)
    if session['authLevel'] == 'admin':
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
                            session['authLevel'] = auth
                            authLevel = session['authLevel']
                            
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


@app.route('/createMenu/', methods=['POST', 'GET'])
@login_required

def createMenu():

    currentUser = User()
    currentFood = Food()
    currentMenu = Menu()

    logged_in = session['logged_in']
    authLevel = session['authLevel']

    
    currentUser.setLoginDetails(session['code'])

    currentRestaurant = currentUser.getBaseRestaurant()

    error = ''


    foodList = currentFood.get_food_list()

    #gets all foods in the food database
    allfoods = [item[0] for item in foodList]

    #gets all the foods currently in the restaurants menu
    foods_in_menu = currentMenu.getfoodNames(currentRestaurant)

    #gets all the foods that are not in the restaurants menu but are in the food database
    foods = [food for food in allfoods if food not in [item[0] for item in foods_in_menu]]

    try: 
        if request.method == "POST":

            print("here3")

            foodName = request.form['foodName']
            print("The food is: " ,foodName)
            print ("The restaurant is: ", currentRestaurant)


            if currentMenu.validateRestaurantName(currentRestaurant) == 1:

                if currentMenu.validateFoodName(foodName) == 1:
                    
                    if currentMenu.checkRestaurantFood(currentRestaurant, foodName) != 1:
                        
                        if currentMenu.createMenu(currentRestaurant, foodName) == 1:
                            
                            flash("Item added to the menu", "success")
                            return redirect(url_for('menu'))

                        else:
                            flash("Failed to add item to the menu", "danger")
                            return render_template('createMenu.html', title="Create Menu", error = e, logged_in=logged_in, authLevel = authLevel, foods = foods, listLen = len(foods))                      

                    else:
                        flash("Food is already in this restaurants Menu", "danger")
                        return render_template('createMenu.html', title="Create Menu", error = e, logged_in=logged_in, authLevel = authLevel, foods = foods, listLen = len(foods))
                    
                else:
                    flash("Food name is invalid", "danger")
                    return render_template('createMenu.html', title="Create Menu", error = e, logged_in=logged_in, authLevel = authLevel, foods = foods, listLen = len(foods))               

            else:
                flash("Restaurant name is invalid", "danger")
                return render_template('createMenu.html', title="Create Menu", error = e, logged_in=logged_in, authLevel = authLevel, foods = foods, listLen = len(foods))

            

        
        else: 
            return render_template('createMenu.html', title="Create Menu", error = e, logged_in=logged_in, authLevel = authLevel, foods = foods, listLen = len(foods))
    
    except Exception as e:
        print("exception")
        return render_template('createMenu.html', title="Create Menu", error = e, logged_in=logged_in, authLevel = authLevel, foods = foods, listLen = len(foods))
    

@app.route("/updateMenu/", methods = ['GET', 'POST'])
@login_required
def updateMenu():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    

    currentUser = User()
    currentUser.setLoginDetails(session['code'])

    currentRestaurant = currentUser.getBaseRestaurant()


    currentMenu = Menu()

    
    foodList, priceList, allergyList, idList, isAvailableList = currentMenu.getMenuList(currentRestaurant)


    return render_template('updateMenu.html', title = "Update Menu" , logged_in=logged_in, authLevel=authLevel,allergyList=allergyList, isAvailableList=isAvailableList, foodList = foodList, priceList = priceList, listLen = len(foodList), idList = idList)

@app.route("/updateMenu2/", methods = ['GET', 'POST'])
@login_required
def updateMenu2():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    

    currentUser = User()
    currentUser.setLoginDetails(session['code'])

    currentRestaurant = currentUser.getBaseRestaurant()


    
    currentFood = Food()
    
    menu = Menu()

    
    

    if request.method == "POST":
        menuID = request.form['idList']
        
        menu.setMenuDetails(menuID)
        
        session['ID'] = menuID
        
        isAvailable = menu.getIsAvailable()
        

    return render_template('updateMenu2.html', title = "Update Menu" , logged_in=logged_in, authLevel=authLevel, isAvailable=isAvailable)


@app.route("/updateMenu3/", methods = ['GET', 'POST'])
@login_required
def updateMenu3():
    # check to see what navbar to display
    menuID = session['ID']

    currentMenu = Menu()

    try:
        if request.method == "POST":
            
            isAvailable = request.form['isAvailable']
            print(isAvailable)

            if isAvailable != None:
                if currentMenu.validateAvailability(isAvailable) == 1:
                    if currentMenu.updateAvailability(isAvailable, menuID) == 1:
                        
                        flash(f"You have successfully updated the item's availability", 'info')
                        return redirect(url_for('updateMenu'))
                    else:
                        flash("Sorry there was an error changing the availability", "danger")
                        return redirect(url_for('updateMenu3'))
                else:
                    flash("Availability syntax incorrect", "danger")
                    return redirect(url_for('updateMenu3'))
            else:                
                flash("Please don't leave any field empty", "danger")
                return redirect(url_for('updateMenu3'))
    except Exception as e:                
        return redirect(url_for('updateMenu3'))  



    return redirect(url_for('updateMenu3'))





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


#Beginning of discount crud

@app.route("/discountOptions/")
@login_required
@manager_required

def discountOptions():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    return render_template('discountOptions.html', title="Restaurant Options", logged_in=logged_in, authLevel=authLevel)

@app.route('/createDiscount/', methods=['POST', 'GET'])
@login_required
@manager_required

def createDiscount():
    discount = Discount()

    

    logged_in = session['logged_in']
    authLevel = session['authLevel']


    error = ''

    try:
        if request.method == "POST": 
            #getting data from form        
            discountValue = request.form['discountValue']

                 
            if discountValue != None:
                if discount.checkDiscountValue(discountValue) != 1:

                    
                    if discount.validateDiscountValueSyntax(discountValue) == 1:
                        

                        if discount.createDiscount(discountValue) == 1:  
                   

                            flash("Discount is now registered", "success")
                            return redirect(url_for('home'))
                        else:
                            flash("Unexpected Error occured", "danger")
                            return render_template('home.html', error=error, title="Discount Options", logged_in=logged_in, authLevel=authLevel)
                    else:
                        flash("Invalid discount value", "danger")
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
@manager_required

def deleteDiscount():
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    discount = Discount()
    
    dIDs, dValues = discount.get_discounts()

    return render_template('deleteDiscount.html', title = "Delete Discount", logged_in=logged_in, authLevel = authLevel, dIDs=dIDs, dValues=dValues, discountsLen = len(dIDs))

@app.route("/deleteDiscount2/", methods=['GET', 'POST'])
@login_required
@manager_required


def deleteDiscount2():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    discount = Discount()


    try:
        if request.method == "POST":
            # Code that you wanna delete
            dID = request.form['selected']

   
            if discount.deleteDiscount(dID):
                flash(f"You have successfully deleted the discount with ID {dID}", 'info')
                return redirect(url_for('adminOptions'))
            else:
                flash(f"Discount with ID \"{dID}\" does not exist", 'danger')
                return redirect(url_for('deleteUser'))
            
    except Exception as e:  
        return render_template('adminOptions.html', error=e, title="User Options", logged_in=logged_in, authLevel=authLevel)


@app.route("/updateDiscount/", methods=['GET', 'POST'])
@login_required
@manager_required

def updateDiscount():
    
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    discount = Discount()

    dIDs, dValues = discount.get_discounts()
  
    return render_template('updateDiscount.html', title = "Update Discount", logged_in=logged_in, authLevel = authLevel, dIDs=dIDs, dValues=dValues, discountsLen = len(dIDs))

@app.route("/updateDiscount2/", methods=['GET', 'POST'])
@login_required
@manager_required

def updateDiscount2():
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    currentDiscount = Discount()
    

    if request.method == "POST":
        dID = request.form['selected']
        session['previousdID'] = dID
        currentDiscount.setDiscountDetails(dID)

        dValue = currentDiscount.getDiscountValue()


        return render_template("updateDiscount2.html", title = "Update Discount", logged_in=logged_in, authLevel=authLevel, discountID=dID, discountValue=dValue)
    
    return render_template("updateDiscount2.html", title = "Update Discount", logged_in=logged_in, authLevel=authLevel)

@app.route("/updateDiscount3/", methods=['GET', 'POST'])
@login_required
@manager_required

def updateDiscount3():
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    discount = Discount()    

    try:
    
        if request.method == "POST":
        
            dValue = request.form['discountValue']

            print(f"dValue {dValue}")

            if dValue != None:
    
                if discount.validateDiscountValueSyntax(dValue) == 1:

                    previousdID = session['previousdID']
                    

                    if discount.updateDiscountValue(previousdID, dValue):


                        flash(f"You have successfully updated the discount with value {dValue}", 'info')
                        return redirect(url_for('adminOptions'))
                    else:
                        flash("Unexpected error occured")
                        return render_template('updateDiscount2.html', error="", title = "Update Discount", logged_in=logged_in, authLevel=authLevel)
                else:
                    flash("Discount value is in the wrong format")
                    return render_template('updateDiscount2.html', error="", title = "Update Discount", logged_in=logged_in, authLevel=authLevel)
            else:                
                flash("Please don't leave any field empty", "danger")
                return render_template('updateDiscount2.html', error="", title = "Update Discount", logged_in=logged_in, authLevel=authLevel)
    except Exception as e:                
        return render_template('updateDiscount2.html', error=e, title = "Update Discount", logged_in=logged_in, authLevel=authLevel)


#### Reports

@app.route("/salesReport/", methods=['GET', 'POST'])
@login_required
@manager_required
def salesReport():  
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    # Put some restaurant thing in here
    restaurant = Restaurant()
    restaurants = []
    tempRestaurants = restaurant.getAllRestaurants()

    restaurants = strip.it(tempRestaurants)
    
    return render_template('viewSalesReport.html', title = "Sales Report", logged_in=logged_in, authLevel=authLevel, restaurants=restaurants)


@app.route("/salesReport2/", methods=['GET', 'POST'])
@login_required
@manager_required
def salesReport2():  
    logged_in = session['logged_in']
    authLevel = session['authLevel']


    startDate = request.form['dateStart']
    endDate = request.form['dateEnd']

    currentUser = User()
    code = session['code']
    currentUser.setLoginDetails(code)

    
    if authLevel == "manager":
        selected_restaurant = currentUser.getBaseRestaurant()
        
        records = sales(startDate, endDate, selected_restaurant)

    if authLevel == "admin":
        selected_restaurant = request.form['res']
        
        records = sales(startDate, endDate, selected_restaurant)

    if records == []:
        flash("No information for this date range", 'danger')
        return redirect(url_for('salesReport'))
    
    return render_template('salesReport.html', title = "Sales Report", logged_in=logged_in, authLevel=authLevel, records=records, recordsLen=len(records))
    
@app.route("/averageSalesReport/", methods=['GET', 'POST'])
@login_required
@manager_required
def averageSalesReport():  
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    # Put some restaurant thing in here
    restaurant = Restaurant()
    restaurants = []
    tempRestaurants = restaurant.getAllRestaurants()

    restaurants = strip.it(tempRestaurants)
    

    return render_template('viewAverageSalesReport.html', title = "Average Sales Report", logged_in=logged_in, authLevel=authLevel, restaurants=restaurants)
    
@app.route("/averageSalesReport2/", methods=['GET', 'POST'])
@login_required
@manager_required
def averageSalesReport2():  
    logged_in = session['logged_in']
    authLevel = session['authLevel']


    startDate = request.form['dateStart']
    endDate = request.form['dateEnd']

    currentUser = User()
    code = session['code']
    currentUser.setLoginDetails(code)

    
    if authLevel == "manager":
        selected_restaurant = currentUser.getBaseRestaurant()
        
        records = averageSales(startDate, endDate, selected_restaurant)

    if authLevel == "admin":
        selected_restaurant = request.form['res']
        
        records = averageSales(startDate, endDate, selected_restaurant)

    if records == []:
        flash("No information for this date range", 'danger')
        return redirect(url_for('salesReport'))
    
    return render_template('averageSalesReport.html', title = "Average Sales Report", logged_in=logged_in, authLevel=authLevel, records=records, recordsLen=len(records))    

@app.route("/averageServingTimeReport/", methods=['GET', 'POST'])
@login_required
@manager_required
def averageServingTimeReport():  
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    # Put some restaurant thing in here
    restaurant = Restaurant()
    restaurants = []
    tempRestaurants = restaurant.getAllRestaurants()

    restaurants = strip.it(tempRestaurants)
    
    return render_template('viewAverageServingTimeReport.html', title = "Average Serving Time Report", logged_in=logged_in, authLevel=authLevel, restaurants=restaurants)

@app.route("/averageServingTimeReport2/", methods=['GET', 'POST'])
@login_required
@manager_required
def averageServingTimeReport2():  
    logged_in = session['logged_in']
    authLevel = session['authLevel']


    startDate = request.form['dateStart']
    endDate = request.form['dateEnd']

    currentUser = User()
    code = session['code']
    currentUser.setLoginDetails(code)

    
    if authLevel == "manager":
        selected_restaurant = currentUser.getBaseRestaurant()
        
        records = averageServingTime(startDate, endDate, selected_restaurant)

    if authLevel == "admin":
        selected_restaurant = request.form['res']
        
        records = averageServingTime(startDate, endDate, selected_restaurant)

    if records == []:
        flash("No information for this date range", 'danger')
        return redirect(url_for('salesReport'))
    
    return render_template('averageServingTimeReport.html', title = "Average Serving Time Report", logged_in=logged_in, authLevel=authLevel, records=records, recordsLen=len(records)) 


@app.route("/totalDiscountAmountReport/", methods=['GET', 'POST'])
@login_required
@manager_required
def totalDiscountAmountReport():  
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    # Put some restaurant thing in here
    restaurant = Restaurant()
    restaurants = []
    tempRestaurants = restaurant.getAllRestaurants()

    restaurants = strip.it(tempRestaurants)
    
    return render_template('viewTotalDiscountReport.html', title = "Total Discount Amount Report", logged_in=logged_in, authLevel=authLevel, restaurants=restaurants)

@app.route("/totalDiscountAmountReport2/", methods=['GET', 'POST'])
@login_required
@manager_required
def totalDiscountAmountReport2():  
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    startDate = request.form['dateStart']
    endDate = request.form['dateEnd']

    currentUser = User()
    code = session['code']
    currentUser.setLoginDetails(code)

    
    if authLevel == "manager":
        selected_restaurant = currentUser.getBaseRestaurant()
        
        records = totalDiscountAmount(startDate, endDate, selected_restaurant)

    if authLevel == "admin":
        selected_restaurant = request.form['res']
        
        records = totalDiscountAmount(startDate, endDate, selected_restaurant)

    if records == []:
        flash("No information for this date range", 'danger')
        return redirect(url_for('salesReport'))
    
    return render_template('totalDiscountReport.html', title = "Total Discount Amount Report", logged_in=logged_in, authLevel=authLevel, records=records, recordsLen=len(records))

@app.route("/averageDiscountAmountReport/", methods=['GET', 'POST'])
@login_required
@manager_required
def averageDiscountAmountReport():  
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    # Put some restaurant thing in here
    restaurant = Restaurant()
    restaurants = []
    tempRestaurants = restaurant.getAllRestaurants()

    restaurants = strip.it(tempRestaurants)
    

    return render_template('viewAverageDiscountReport.html', title = "Average Discount Amount Report", logged_in=logged_in, authLevel=authLevel, restaurants=restaurants)


@app.route("/averageDiscountAmountReport2/", methods=['GET', 'POST'])
@login_required
@manager_required
def averageDiscountAmountReport2():  
    logged_in = session['logged_in']
    authLevel = session['authLevel']


    startDate = request.form['dateStart']
    endDate = request.form['dateEnd']

    currentUser = User()
    code = session['code']
    currentUser.setLoginDetails(code)

    
    if authLevel == "manager":
        selected_restaurant = currentUser.getBaseRestaurant()
        
        records = averageDiscountAmount(startDate, endDate, selected_restaurant)

    if authLevel == "admin":
        selected_restaurant = request.form['res']
        
        records = averageDiscountAmount(startDate, endDate, selected_restaurant)

    if records == []:
        flash("No information for this date range", 'danger')
        return redirect(url_for('salesReport'))
    
    return render_template('averageDiscountReport.html', title = "Average Discount Amount Report", logged_in=logged_in, authLevel=authLevel, records=records, recordsLen=len(records))


#Beggining of Inventory

@app.route("/inventory/", methods = ['GET', 'POST'])
@login_required
@chef_required
def inventory():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    

    currentUser = User()
    inventory = Inventory()
    currentUser.setLoginDetails(session['code'])
    
    currentRestaurant = currentUser.getBaseRestaurant()
    
    items = []
    tempItems = inventory.getItemNames(currentRestaurant)
    items = strip.it(tempItems)
    
    quantity = []
    tempQuantity = inventory.getItemQuantity(currentRestaurant)
    quantity = strip.it(tempQuantity)
    
    stockLimit = []
    tempStockLimit = inventory.getItemStockLimit(currentRestaurant)
    stockLimit = strip.it(tempStockLimit)
    
    return render_template('inventory.html', title = "Inventory" , logged_in=logged_in, authLevel=authLevel, items = items, quantity = quantity, stockLimit=stockLimit, listLen = len(items))

@app.route("/createInventory/", methods = ['GET', 'POST'])
@login_required
@chef_required
def createInventory():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    currentUser = User()
    inventory = Inventory()
    currentItem = Item()

    currentUser.setLoginDetails(session['code'])
    
    currentRestaurant = currentUser.getBaseRestaurant()

    itemsList = currentItem.get_item_list()
    
    #gets all foods in the food database
    allItems = [item[0] for item in itemsList]

    items_in_inventory = inventory.getItemNames(currentRestaurant)

    #gets all the foods that are not in the restaurants menu but are in the food database
    items = [item for item in allItems if item not in [inventoryItem[0] for inventoryItem in items_in_inventory]]

    error = ''
    
    try:
        if request.method == "POST": 
            #getting data from form        
            currentRestaurant = currentUser.getBaseRestaurant()
            itemName = request.form['itemName']
            quantity = request.form['itemQuantity']
            stockLimit = request.form['itemSL']                   
            if itemName != None and quantity != None and stockLimit != None:
                if inventory.validateItemName(itemName) == 1:
                    if inventory.validateQuantity(quantity) == 1:
                        if inventory.validateQuantity2(quantity, stockLimit) == 1:
                            if inventory.validateStockLimit(stockLimit) == 1:
                                if inventory.checkRestaurantItem(currentRestaurant, itemName) != 1:
                                    if inventory.createInventory(currentRestaurant, itemName, quantity, stockLimit) == 1:               
                                        flash("Item has been created", "success")
                                        return redirect(url_for('inventory'))
                                    else:
                                        flash("Could not create item", "danger")
                                        return render_template('createInventory.html', error=error, title="Create Invnentory", logged_in=logged_in, authLevel=authLevel, items = items, listLen = len(items))
                                else:
                                    flash("Item already exists in the restaurant", "danger")
                                    return render_template('createInventory.html', error=error, title="Create Invnentory", logged_in=logged_in, authLevel=authLevel, items = items, listLen = len(items))
                            else:
                                flash("Invalid stock limit (1-99)", "danger")
                                return render_template('createInventory.html', error=error, title="Create Invnentory", logged_in=logged_in, authLevel=authLevel, items = items, listLen = len(items))
                        else:
                            flash("Quantity cannot be more than stock limit", "danger")
                            return render_template('createInventory.html', error=error, title="Create Inventory", logged_in=logged_in, authLevel=authLevel, items = items, listLen = len(items))
                    else:
                        flash("Invalid quantity input (1-99)", "danger")
                        return render_template('createInventory.html', error=error, title="Create Inventory", logged_in=logged_in, authLevel=authLevel, items = items, listLen = len(items))
                else:
                    flash("Item not available in the warehouse", "danger")
                    return render_template('createInventory.html', error=error, title="Create Inventory", logged_in=logged_in, authLevel=authLevel, items = items, listLen = len(items))
            else:                
                flash("Fields cannot be empty", "danger")
                return render_template('createInventory.html', error=error, title="Create Inventory", logged_in=logged_in, authLevel=authLevel, items = items, listLen = len(items))
        else:            
            return render_template('createInventory.html', error=error, title="Create Inventory", logged_in=logged_in, authLevel=authLevel, items = items, listLen = len(items))        
    except Exception as e:                
        return render_template('createInventory.html', error=e, title="Create Inventory", logged_in=logged_in, authLevel=authLevel, items = items, listLen = len(items))


@app.route("/deleteInventory/", methods=['GET', 'POST'])
@login_required
@chef_required
def deleteInventory():
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    currentUser = User()
    inventory = Inventory()
    currentUser.setLoginDetails(session['code'])
    
    currentRestaurant = currentUser.getBaseRestaurant()
    
    inventoryID = []
    tempInventoryID = inventory.getInventoryID(currentRestaurant)
    inventoryID = strip.it(tempInventoryID)
    
    itemName = []
    tempItemName = inventory.getItemNames(currentRestaurant)
    itemName = strip.it(tempItemName)
    
    itemQuantity = []
    tempItemQuantity = inventory.getItemQuantity(currentRestaurant)
    itemQuantity = strip.it(tempItemQuantity)
    
    itemSL = []
    tempItemSL = inventory.getItemStockLimit(currentRestaurant)
    itemSL = strip.it(tempItemSL)
    
    return render_template('deleteInventory.html', title = "Delete Inventory" , logged_in=logged_in, authLevel=authLevel, inventoryID = inventoryID, itemName = itemName, itemQuantity = itemQuantity, itemSL=itemSL, listLen = len(itemName))

@app.route("/deleteInventory2/", methods=['GET', 'POST'])
@login_required
@chef_required
def deleteInventory2():
    inventory = Inventory()

    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    try:
        if request.method == "POST":
            # Item name that you wanna delete
            inventoryID = request.form['inventoryID']
            inventory.setInventoryDetails(inventoryID)
            
            itemName = inventory.getItemName()
  
            if inventory.delete_inventory(inventoryID):
                flash(f"You have successfully deleted the item {itemName}", 'info')
                return redirect(url_for('inventory'))
            else:
                flash(f"Item \"{itemName}\" does not exist", 'danger')
                return redirect(url_for('deleteInventory'))
                
    except Exception as e:  
        return render_template('deleteInventory.html', error=e, title="Delete Inventory", logged_in=logged_in, authLevel=authLevel)

@app.route("/updateInventory/", methods=['GET', 'POST'])
@login_required
@chef_required
def updateInventory():
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    currentUser = User()
    inventory = Inventory()
    currentUser.setLoginDetails(session['code'])
    
    currentRestaurant = currentUser.getBaseRestaurant()
    
    inventoryID = []
    tempInventoryID = inventory.getInventoryID(currentRestaurant)
    inventoryID = strip.it(tempInventoryID)
    
    itemName = []
    tempItemName = inventory.getItemNames(currentRestaurant)
    itemName = strip.it(tempItemName)
    
    itemQuantity = []
    tempItemQuantity = inventory.getItemQuantity(currentRestaurant)
    itemQuantity = strip.it(tempItemQuantity)
    
    itemSL = []
    tempItemSL = inventory.getItemStockLimit(currentRestaurant)
    itemSL = strip.it(tempItemSL)
    
    return render_template('updateInventory.html', title = "Update Inventory" , logged_in=logged_in, authLevel=authLevel, inventoryID = inventoryID, itemName = itemName, itemQuantity = itemQuantity, itemSL=itemSL, listLen = len(itemName))

@app.route("/updateInventory2/", methods=['GET', 'POST'])
@login_required
@chef_required
def updateInventory2():
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    if request.method == "POST":
        
        inventoryID = request.form['inventoryID']
        session['inventoryID'] = inventoryID
    
    return render_template('updateInventory2.html', title = "Update Inventory" , logged_in=logged_in, authLevel=authLevel)

@app.route("/updateInventory3/", methods=['GET', 'POST'])
@login_required
@chef_required
def updateInventory3():
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    inventoryID = session['inventoryID']

    
    inventory = Inventory()
    
    inventory.setInventoryDetails(inventoryID)
    print(inventoryID)
    
    itemName = inventory.getItemName()
    try:
        if request.method == "POST":
            
            itemSL = request.form['itemSL']
            
            if itemSL != None:
                if inventory.validateStockLimit(itemSL) == 1:
                    if inventory.updateStockLimit(itemSL, inventoryID):
                        flash(f"You have successfully updated the item {itemName}", 'info')
                        return redirect(url_for('inventory'))
                    else:
                        flash("The stock Limit should be within 1-99", "danger")
                        return render_template('updateInventory2.html', title = "Update Inventory" , logged_in=logged_in, authLevel=authLevel)
                else:
                    flash("The stock Limit should be within 1-99", "danger")
                    return render_template('updateInventory2.html', title = "Update Inventory" , logged_in=logged_in, authLevel=authLevel)
            else:                
                flash("Please don't leave any field empty", "danger")
                return render_template('updateInventory2.html', title = "Update Inventory" , logged_in=logged_in, authLevel=authLevel)
    except Exception as e:                
        return render_template('updateInventory2.html', title = "Update Inventory" , logged_in=logged_in, authLevel=authLevel)


@app.route("/manualOrder/", methods=['GET', 'POST'])
@login_required
@chef_required
def manualOrder():
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    currentUser = User()
    invent = Inventory()

    currentUser.setLoginDetails(session['code'])
    
    currentRestaurant = currentUser.getBaseRestaurant()
    session['currentRestaurant'] = currentRestaurant
    
    inventoryID = []
    tempInventoryID = invent.getInventoryID(currentRestaurant)
    inventoryID = strip.it(tempInventoryID)
    
    itemName = []
    tempItemName = invent.getItemNames(currentRestaurant)
    itemName = strip.it(tempItemName)
    
    itemQuantity = []
    tempItemQuantity = invent.getItemQuantity(currentRestaurant)
    itemQuantity = strip.it(tempItemQuantity)
    
    itemSL = []
    tempItemSL = invent.getItemStockLimit(currentRestaurant)
    itemSL = strip.it(tempItemSL)

    
    
    return render_template('manualOrder.html', title = "Manual Order" , logged_in=logged_in, authLevel=authLevel, inventoryID = inventoryID, itemName = itemName, itemQuantity = itemQuantity, itemSL=itemSL, listLen = len(itemName))


@app.route("/manualOrder2/", methods=['GET', 'POST'])
@login_required
@chef_required
def manualOrder2():
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    invent = Inventory()
    
    if request.method == "POST":
        
        inventoryID = request.form['inventoryID']
        session['inventoryID'] = inventoryID

        invent.setInventoryDetails(inventoryID)

        itemQuant = invent.getQuantity()

        itemSL = invent.getStockLimit()

    
    return render_template('manualOrder2.html', title = "Manual Order" , logged_in=logged_in, authLevel=authLevel, itemQuant=itemQuant, itemSL=itemSL)


@app.route("/manualOrder3/", methods=['GET', 'POST'])
@login_required
@chef_required
def manualOrder3():
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    inventoryID = session['inventoryID']
    
    invent = Inventory()
    item = Item()
    
    invent.setInventoryDetails(inventoryID)
    item.setItemDetails(invent.getItemName())
    
    itemName = invent.getItemName()
    try:
        
        if request.method == "POST":
            
            
            quantToAdd = int(request.form['itemQuant'])
            
            
            if quantToAdd != None:
                itemSL = int(invent.getStockLimit())
                itemQuant = int(invent.getQuantity())
                

                if invent.checkItemQuantLessThanStockLimit(itemSL, itemQuant, quantToAdd) == 1:
                    
                    if item.isThereMoreItems(itemName, quantToAdd) == 1:
                    

                        invent.updateQuantity(quantToAdd + itemQuant)
                        item.takeAwayItems(quantToAdd, itemName)

                        flash(f"You have successfully updated the item {itemName}", 'info')
                        return redirect(url_for('inventory'))
                    else:
                        flash("There is not enough stock in the warehouse", "danger")
                        return render_template('manualOrder2.html', title = "Manual Order" , logged_in=logged_in, authLevel=authLevel, itemQuant=itemQuant, itemSL=itemSL)
                else:
                    flash("The quantity must be smaller than the stock limit", "danger")
                    return render_template('manualOrder2.html', title = "Manual Order" , logged_in=logged_in, authLevel=authLevel, itemQuant=itemQuant, itemSL=itemSL)
            else:                
                flash("Please don't leave any field empty", "danger")
                return render_template('manualOrder2.html', title = "Manual Order" , logged_in=logged_in, authLevel=authLevel, itemQuant=itemQuant, itemSL=itemSL)
    except Exception as e:                
        flash(e)
        return render_template('home.html', title = "Manual Order" , logged_in=logged_in, authLevel=authLevel)







@app.route("/order/")
@login_required
def order():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    user = User()
    user.setLoginDetails(session['code'])
    restaurant = user.getBaseRestaurant()

    order = Order()
    tempStatus = [status[2] for status in order.get_order(restaurant)]
    status = strip.it(tempStatus)

    tempPrice = [price[3] for price in order.get_order(restaurant)]
    price = strip.it(tempPrice)

    tempTableNumber = [tableNumber[4] for tableNumber in order.get_order(restaurant)]
    tableNumber = strip.it(tempTableNumber)

    tempStartTime = [startTime[5] for startTime in order.get_order(restaurant)]
    startTime = strip.it(tempStartTime)

    tempReadyTime = [readyTime[6] for readyTime in order.get_order(restaurant)]
    readyTime = strip.it(tempReadyTime)
    
    return render_template('order.html', title="order", logged_in=logged_in, authLevel=authLevel, status=status, price=price, tableNumber=tableNumber, startTime=startTime, readyTime=readyTime, len=len(status))

@app.route("/createTableNumber/", methods = ["GET", "POST"])
@login_required
def createTableNumber():
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    currentUser = User()
    currentUser.setLoginDetails(session['code'])

    currentRestaurant = currentUser.getBaseRestaurant()
    restaurant = Restaurant()
    restaurant.setRestaurantDetails(currentRestaurant)
    numOfTables = restaurant.getNumberOfTables()

    try:
        if request.method == "POST":
            status = "Order Created"
            order = Order()
            tableNumber = request.form['tableNumber']
            startTime = None
            readyTime = None
            if order.createOrder(currentRestaurant, status, int(tableNumber), startTime, readyTime):
                flash("Order has been created, you may now add items to it", "success")
                orderID = order.getID()
                session['orderID'] = orderID
                return redirect(url_for("createOrder"))
            else:
                flash("Table Number does not exist in your restaurant", "danger")
                return render_template('createTableNumber.html', title = "Create Order" , logged_in=logged_in, authLevel=authLevel, numOfTables=numOfTables)
    except Exception as e:                
        return render_template('createTableNumber.html', title = "Create Order" , logged_in=logged_in, authLevel=authLevel, error=e, numOfTables=numOfTables)
    return render_template('createTableNumber.html', title="Create Order", logged_in=logged_in, authLevel=authLevel, numOfTables=numOfTables)

    

@app.route("/createOrder/", methods=['GET', 'POST'])
@login_required
def createOrder():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    currentUser = User()
    currentUser.setLoginDetails(session['code'])

    currentRestaurant = currentUser.getBaseRestaurant()

    currentMenu = Menu()

    
    foodList, priceList, allergyList, idList, isAvailableList = currentMenu.getAvailableMenuList(currentRestaurant)

    try:

        if request.method == 'POST':
            foodName = request.form['foodName']
            order = Order()
            
            order.addFoodToOrder(session['orderID'], foodName)
            flash("Successfully added food to order", "success")
            return redirect(url_for('createOrder'))
        return render_template('createOrder.html', title="Create Order", logged_in=logged_in, authLevel=authLevel, foodList = foodList, priceList = priceList, allergyList = allergyList, idList = idList, listLen = len(foodList))
    except Exception as e:                
        return render_template('createOrder.html', title="Create Order", logged_in=logged_in, authLevel=authLevel, error=e, foodList = foodList, priceList = priceList, allergyList = allergyList, idList = idList, listLen = len(foodList))





@app.route("/createOrder2/", methods=['POST', 'GET'])
@login_required
def createOrder2():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    currentUser = User()
    currentUser.setLoginDetails(session['code'])
    order = Order()

    order.setOrderDetails(session['orderID'])
    foodList = order.getFoodList()
    foodList = strip.it(foodList)

    discountList = order.getDiscountValues(session['orderID'])
    discountList = str(discountList).strip("[")
    discountList = str(discountList).strip("]")

    orderPrice = order.getPrice()

    priceList = []
    
    for food in foodList:
        price = order.getFoodListPrice(food)
        price = strip.it(price)
        price = str(price).strip("[")
        price = str(price).strip("]")
        price = str(price).strip("'")
        priceList.append(price)

    
    return render_template('createOrder2.html', title="order", logged_in=logged_in, authLevel=authLevel, foodList=foodList, priceList=priceList, foodLen=len(foodList), discountList=str(discountList), orderPrice=orderPrice)


@app.route("/deleteOrder/", methods=['POST', 'GET'])
@login_required
def deleteOrder():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    user = User()
    user.setLoginDetails(session['code'])
    restaurant = user.getBaseRestaurant()

    order = Order()

    tempID = [orderID[0] for orderID in order.get_order(restaurant)]
    ID = strip.it(tempID)

    tempStatus = [status[2] for status in order.get_order(restaurant)]
    status = strip.it(tempStatus)

    tempPrice = [price[3] for price in order.get_order(restaurant)]
    price = strip.it(tempPrice)

    tempTableNumber = [tableNumber[4] for tableNumber in order.get_order(restaurant)]
    tableNumber = strip.it(tempTableNumber)

    tempStartTime = [startTime[5] for startTime in order.get_order(restaurant)]
    startTime = strip.it(tempStartTime)

    tempReadyTime = [readyTime[6] for readyTime in order.get_order(restaurant)]
    readyTime = strip.it(tempReadyTime)

    
    return render_template('deleteOrder.html', title="Delete Order", logged_in=logged_in, authLevel=authLevel, status=status, price=price, tableNumber=tableNumber, startTime=startTime, readyTime=readyTime, ID=ID, len=len(ID))

@app.route("/deleteOrder2/", methods=['GET', 'POST'])
@login_required
@chef_required
def deleteOrder2():
    order = Order()

    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    try:
        if request.method == "POST":
            # order name that you wanna delete
            ID = request.form['ID']
            if order.delete_order(ID):
                flash(f"You have successfully deleted an order", 'info')
                return redirect(url_for('order'))
            else:
                flash(f"This order does not exist", 'danger')
                return redirect(url_for('deleteOrder'))
                
    except Exception as e:  
        return render_template('deleteOrder.html', error=e, title="Delete Order", logged_in=logged_in, authLevel=authLevel)

@app.route("/updateOrder/", methods=['POST', 'GET'])
@login_required
def updateOrder():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    user = User()
    user.setLoginDetails(session['code'])
    restaurant = user.getBaseRestaurant()

    order = Order()
    tempID = [orderID[0] for orderID in order.get_order(restaurant)]
    ID = strip.it(tempID)

    tempStatus = [status[2] for status in order.get_order(restaurant)]
    status = strip.it(tempStatus)

    tempPrice = [status[3] for status in order.get_order(restaurant)]
    price = strip.it(tempPrice)

    tempTableNumber = [tableNumber[4] for tableNumber in order.get_order(restaurant)]
    tableNumber = strip.it(tempTableNumber)

    tempStartTime = [startTime[5] for startTime in order.get_order(restaurant)]
    startTime = strip.it(tempStartTime)

    tempReadyTime = [readyTime[6] for readyTime in order.get_order(restaurant)]
    readyTime = strip.it(tempReadyTime)
    
    return render_template('updateOrder.html', title="Update Order", logged_in=logged_in, authLevel=authLevel, status=status, price=price, tableNumber=tableNumber, startTime=startTime, readyTime=readyTime, len=len(ID), orderID=ID)

@app.route("/updateOrder2/", methods=['POST', 'GET'])
@login_required
def updateOrder2():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    try:
        if request.method == 'POST':
            orderID = request.form['orderID']
            session['orderID'] = orderID
            order = Order()
            order.setOrderDetails(orderID)
            status = order.getStatus()
            return render_template('updateOrder2.html', title="Update Order", logged_in=logged_in, authLevel=authLevel, error=e, status=status)

    except Exception as e:                
        return render_template('updateOrder2.html', title="Update Order", logged_in=logged_in, authLevel=authLevel, error=e, status=None)
    
    return render_template('updateOrder2.html', title="Update Order", logged_in=logged_in, authLevel=authLevel, status=None)

@app.route("/updateOrder3/", methods=['POST', 'GET'])
@login_required
def updateOrder3():
    logged_in=session['logged_in']
    authLevel=session['authLevel']
    order = Order()
    order.setOrderDetails(session['orderID'])
    status = order.getStatus()
    startTime = order.getStartTime()
    readyTime = order.getReadyTime()
    try:
        if request.method == 'POST':
            newStatus = request.form['status']
            if newStatus == 'Cooking':
                if startTime == None:
                    order.updateStatus(newStatus, session['orderID'])
                    currentDate = datetime.datetime.now()
                    currentDate = currentDate.strftime("%Y-%m-%d %H:%M:%S")
                    order.updateStartTime(currentDate, session['orderID'])
                    flash("Successfully updated order details", "success")
                    return redirect(url_for('order'))
                else:
                    flash("Start time has already been set", "danger")
                    return redirect(url_for('updateOrder2'))
            elif newStatus == 'Ready':
                if startTime != None:
                    if readyTime == None:
                        order.updateStatus(newStatus, session['orderID'])
                        currentDate = datetime.datetime.now()
                        currentDate = currentDate.strftime("%Y-%m-%d %H:%M:%S")
                        startTime = order.getStartTime()
                        if order.updateReadyTime(currentDate, session['orderID'], startTime):
                            flash("Successfully updated order details", "success")
                            return redirect(url_for('order'))
                    else:
                        flash("You have already set the ready time for this order", "danger")
                        return redirect(url_for('updateOrder2'))
                else:
                    flash("Start time should be set before Ready time", "danger")
                    return render_template('updateOrder2.html', title="Update Order", logged_in=logged_in, authLevel=authLevel, error=e, status=status)
            elif newStatus == "Cancelled":
                order.delete_order(session['orderID'])
                flash("Order has been deleted", "success")
                return redirect(url_for('order'))
            elif newStatus == 'Delivered':
                if startTime != None:
                    if readyTime != None:
                        order.updateStatus(newStatus, session['orderID'])
                        flash("Successfully updated order details", "success")
                        return redirect(url_for('order'))
                    else:
                        flash("You have not yet marked the order as ready", "danger")
                        return redirect(url_for('updateOrder2'))
                else:
                    flash("You have not yet marked the order as being started", "danger")
                    return redirect(url_for)
            else:
                flash("Successfully updated order details", "success")
                return redirect(url_for('updateOrder2'))
    except Exception as e:                
        return render_template('updateOrder2.html', title="Update Order", logged_in=logged_in, authLevel=authLevel, error=e, status=status)

@app.route("/removeFromOrder/", methods=['POST', 'GET'])
@login_required
def removeFromOrder():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    currentUser = User()
    currentUser.setLoginDetails(session['code'])
    order = Order()

    order.setOrderDetails(session['orderID'])
    foodList = order.getFoodList()
    foodList = strip.it(foodList)

    foodListID = order.getFoodListID()
    foodListID = strip.it(foodListID)

    priceList = []
    
    for food in foodList:
        price = order.getFoodListPrice(food)
        price = strip.it(price)
        price = str(price).strip("[")
        price = str(price).strip("]")
        price = str(price).strip("'")
        priceList.append(price)

        try:
            if request.method == "POST":
                chosenFood = request.form['foodListID']
                chosenName = order.getSpecificFoodList(chosenFood)
                chosenName = strip.it(chosenName)
                chosenName = str(chosenName).strip("[")
                chosenName = str(chosenName).strip("]")
                chosenName = str(chosenName).strip("'")
                print(str(session['orderID']))
                print(str(chosenName))
                print(str(chosenFood))
                if order.removeFoodFromOrder(session['orderID'],chosenName, chosenFood):
                    flash("Successfully removed food", "success")
                    return redirect(url_for('createOrder2'))
                else:
                    flash("Error removing food", "danger")
                    return redirect(url_for('removeFromOrder'))
        except Exception as e:
            return render_template('removeFromOrder.html', title="Remove From Order", logged_in=logged_in, authLevel=authLevel,foodList=foodList, priceList=priceList, foodLen=len(foodList), foodListID=foodListID, error=e)
    
    return render_template('removeFromOrder.html', title="order", logged_in=logged_in, authLevel=authLevel,foodList=foodList, priceList=priceList, foodLen=len(foodList), foodListID=foodListID)



@app.route("/applyDiscountOrder/", methods=['POST', 'GET'])
@login_required
def applyDiscountOrder():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    discount = Discount()
    order = Order()
    order.setOrderDetails(session['orderID'])

    dIDs, dValues = discount.get_discounts()

    discountListIDs, orderIDs, discountIDs = order.getDiscountList(session['orderID'])
    i = 0
    while i < len(dIDs):
        if dIDs[i] in discountIDs:
            dIDs.remove(dIDs[i])
        else:
            i += 1

    try:
        if request.method == 'POST':
            discountID = request.form['dID']
            print(str(discountID))
            if order.addDiscountToOrder(session['orderID'], discountID):
                flash("Applied discount to order", "success")
                return redirect(url_for('createOrder2'))
            else:
                flash("Error adding discount to order", "danger")
                return redirect(url_for('applyDiscountOrder'))

    except Exception as e:
         return render_template('applyDiscountOrder.html', title = "Update Discount", logged_in=logged_in, authLevel = authLevel, dIDs=dIDs, dValues=dValues, discountsLen = len(dIDs), error=e)


  
    return render_template('applyDiscountOrder.html', title = "Update Discount", logged_in=logged_in, authLevel = authLevel, dIDs=dIDs, dValues=dValues, discountsLen = len(dIDs))

@app.route("/removeDiscountOrder/", methods=['POST', 'GET'])
@login_required
def removeDiscountOrder():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    currentUser = User()
    currentUser.setLoginDetails(session['code'])
    order = Order()
    discount = Discount()

    order.setOrderDetails(session['orderID'])

    discountListID = order.getDiscountListID()
    discountListID = strip.it(discountListID)

    dIDs, dValues = discount.get_discounts()

    discountListIDs, orderIDs, discountIDs = order.getDiscountList(session['orderID'])
    discountList = []
    valueList = []
    i = 0
    while i < len(dIDs):
        if dIDs[i] in discountIDs:
            discountList.append(dIDs[i])
            valueList.append(dValues[i])
            dIDs.remove(dIDs[i])
        else:
            i += 1
        try:
            if request.method == "POST":
                chosenDiscountList = request.form['discountListID']
                chosenValue = order.getSpecificDiscountList(chosenDiscountList)
                chosenValue = strip.it(chosenValue)
                chosenValue = str(chosenValue).strip("[")
                chosenValue = str(chosenValue).strip("]")
                chosenValue = str(chosenValue).strip("'")
                print("!!!!!!! ORDER ID" + str(session['orderID']))
                print("!!!!!!!!!!!! DISCOUNT ID" + str(chosenValue))
                if order.removeDiscountFromOrder(session['orderID'],chosenValue, chosenDiscountList):
                    flash("Successfully removed discount", "success")
                    return redirect(url_for('createOrder2'))
                else:
                    flash("Error removing discount", "danger")
                    return redirect(url_for('removeDiscountOrder'))
        except Exception as e:
            return render_template('removeDiscountOrder.html', title="Remove Discount From Order", logged_in=logged_in, authLevel=authLevel,discountList=discountList, valueList=valueList, discountLen=len(discountList), discountListID=discountListID, error=e)
    
    return render_template('removeDiscountOrder.html', title="Remove Discount From Order", logged_in=logged_in, authLevel=authLevel,discountList=discountList, valueList=valueList, discountLen=len(discountList), discountListID=discountListID)


@app.route("/reservation/", methods=['POST', 'GET'])
@login_required
def reservation():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    currentUser = User()
    reservation = Reservation()

    currentUser.setLoginDetails(session['code'])
    
    currentRestaurant = currentUser.getBaseRestaurant()
    
    namesList = []
    tempNamesList = reservation.getNameList(currentRestaurant)
    namesList = strip.it(tempNamesList)
    
    tablesList = []
    tempTablesList = reservation.getTablesList(currentRestaurant)
    tablesList = strip.it(tempTablesList)
    
    startTimeList = []
    tempStartTimeList = reservation.getStartTimeList(currentRestaurant)
    startTimeList = strip.it(tempStartTimeList)
    
    endTimeList = []
    tempEndTimeList = reservation.getEndTimeList(currentRestaurant)
    endTimeList = strip.it(tempEndTimeList)

    return render_template('reservation.html', title="Reservation", logged_in=logged_in, authLevel=authLevel, Name=namesList, tables=tablesList, startTime=startTimeList, endTime=endTimeList, listLen=len(namesList))


@app.route("/createReservation/", methods=['POST', 'GET'])
@login_required
def createReservation():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    currentUser = User()
    reservation = Reservation()
    
    currentUser.setLoginDetails(session['code'])

    currentRestaurant = currentUser.getBaseRestaurant()
    print(currentRestaurant)
    
    error = ''
    
    try:
        if request.method == "POST":
            #getting data from form 
            Name = request.form['Name']
            numberOfTables = int(request.form['numberOfTables'])
            startDate = request.form['dateStart']
            startTime = request.form['timeStart']
            endDate = request.form['dateEnd']
            endTime = request.form['timeEnd']
            
            start = datetime.datetime.strptime(startDate + " " + startTime + ":00", "%Y-%m-%d %H:%M:%S")
            end = datetime.datetime.strptime(endDate + " " + endTime + ":00", "%Y-%m-%d %H:%M:%S")

            if numberOfTables != None and start != None and end != None and Name != None:
                if reservation.validateTables(numberOfTables, currentRestaurant) == 1:
                    if reservation.validateStartTime(start) == 1:
                        if reservation.validateEndTime(end, start) == 1:
                            if reservation.validateName(Name) == 1:
                                if reservation.createReservation(currentRestaurant, numberOfTables, start, end, Name) == 1:                      
                                    flash("Reservation is now registered", "success")
                                    return redirect(url_for('reservations'))
                                else:
                                    flash("Invalid reservation syntax", "danger")
                                    return render_template('createReservation.html', error=error, title="Create Reservation", logged_in=logged_in, authLevel=authLevel)
                            else:
                                flash("Invalid name input (more than 3 characters)")
                                return render_template('createReservation.html', error=error, title="Create Reservation", logged_in=logged_in, authLevel=authLevel)
                        else:
                            flash("Invalid end time can't be before the start time", "danger")
                            return render_template('createReservation.html', error=error, title="Create Reservation", logged_in=logged_in, authLevel=authLevel)
                    else:
                        flash("Invalid start time can't be before today", "danger")
                        return render_template('createReservation.html', error=error, title="Create Reservation", logged_in=logged_in, authLevel=authLevel)
                else:
                    flash("Invalid table number can't be more than restaurant tables", "danger")
                    return render_template('createReservation.html', error=error, title="Create Reservation", logged_in=logged_in, authLevel=authLevel)
            else:                
                flash("Fields cannot be empty", "danger")
                return render_template('createReservation.html', error=error, title="Create Reservation", logged_in=logged_in, authLevel=authLevel)
        else:            
            return render_template('createReservation.html', error=error, title="Create Reservation", logged_in=logged_in, authLevel=authLevel)        
    except Exception as e:                
        return render_template('createReservation.html', title="Create Reservation", logged_in=logged_in, authLevel=authLevel)


    

@app.route("/updateReservation/", methods=['POST', 'GET'])
@login_required
def updateReservation():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
   
    currentUser = User()
    reservation = Reservation()

    currentUser.setLoginDetails(session['code'])
    
    currentRestaurant = currentUser.getBaseRestaurant()
    
    reservationIDList = []
    tempReservationIDList = reservation.getIDList(currentRestaurant)
    reservationIDList = strip.it(tempReservationIDList)
    
    namesList = []
    tempNamesList = reservation.getNameList(currentRestaurant)
    namesList = strip.it(tempNamesList)
    
    tablesList = []
    tempTablesList = reservation.getTablesList(currentRestaurant)
    tablesList = strip.it(tempTablesList)
    
    startTimeList = []
    tempStartTimeList = reservation.getStartTimeList(currentRestaurant)
    startTimeList = strip.it(tempStartTimeList)
    
    endTimeList = []
    tempEndTimeList = reservation.getEndTimeList(currentRestaurant)
    endTimeList = strip.it(tempEndTimeList)

    return render_template('updateReservation.html', title="Update Reservation", logged_in=logged_in, authLevel=authLevel, Name=namesList, tables=tablesList, startTime=startTimeList, endTime=endTimeList, reservationID=reservationIDList, listLen=len(namesList))


@app.route("/updateReservation2/", methods=['POST', 'GET'])
@login_required
def updateReservation2():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    if request.method == "POST":
        reservationID = request.form['reservationID']
        session['reservationID'] = reservationID
        
    return render_template('updateReservation2.html', title="Update Reservation", logged_in=logged_in, authLevel=authLevel)

@app.route("/updateReservation3/", methods=['POST', 'GET'])
@login_required
def updateReservation3():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    reservationID = session['reservationID']
    
    reservation = Reservation()
    reservation.setReservationDetails(reservationID)
    restaurantName = reservation.getRestaurantName()
    print(restaurantName)
    try:
        if request.method == "POST":
            
            numberOfTables = int(request.form['numberOfTables'])
            startDate = request.form['dateStart']
            startTime = request.form['timeStart']
            endDate = request.form['dateEnd']
            endTime = request.form['timeEnd']
            
            start = datetime.datetime.strptime(startDate + " " + startTime + ":00", "%Y-%m-%d %H:%M:%S")
            end = datetime.datetime.strptime(endDate + " " + endTime + ":00", "%Y-%m-%d %H:%M:%S")
            
            if numberOfTables != None and start != None and end != None:
                if reservation.validateTables(numberOfTables, restaurantName) == 1:
                    if reservation.validateStartTime(start) == 1:
                        if reservation.validateEndTime(end, start) == 1:
                            if reservation.updateStartTime(reservationID, start, end):
                                if reservation.updateEndTime(reservationID, end, start):
                                    
                                    flash("You have successfully updated the reservation", 'info')
                                    return redirect(url_for('reservation'))
                                else:
                                    flash("End time has to be after today and the start time", "danger")
                                    return render_template('updateReservation2.html', title="Update Reservation", logged_in=logged_in, authLevel=authLevel)
                            else:
                                flash("Start time has to be later than current time", "danger")
                                return render_template('updateReservation2.html', title="Update Reservation", logged_in=logged_in, authLevel=authLevel)
                        else:
                            flash("End time has to be after today and the start time", "danger")
                            return render_template('updateReservation2.html', title="Update Reservation", logged_in=logged_in, authLevel=authLevel)        
                    else:
                        flash("Start time has to be later than current time", "danger")
                        return render_template('updateReservation2.html', title="Update Reservation", logged_in=logged_in, authLevel=authLevel)
                else:
                    flash("Table number cannot be larger than the restaurants availability", "danger")
                    return render_template('updateReservation2.html', title="Update Reservation", logged_in=logged_in, authLevel=authLevel)
            else:                
                flash("Please don't leave any field empty", "danger")
                return render_template('updateReservation2.html', title="Update Reservation", logged_in=logged_in, authLevel=authLevel)
    except Exception as e:                
        return render_template('updateReservation2.html', title="Update Reservation", logged_in=logged_in, authLevel=authLevel)
        


@app.route("/deleteReservation/")
@login_required
def deleteReservation():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    currentUser = User()
    reservation = Reservation()

    currentUser.setLoginDetails(session['code'])
    
    currentRestaurant = currentUser.getBaseRestaurant()
    
    reservationIDList = []
    tempReservationIDList = reservation.getIDList(currentRestaurant)
    reservationIDList = strip.it(tempReservationIDList)
    
    namesList = []
    tempNamesList = reservation.getNameList(currentRestaurant)
    namesList = strip.it(tempNamesList)
    
    tablesList = []
    tempTablesList = reservation.getTablesList(currentRestaurant)
    tablesList = strip.it(tempTablesList)
    
    startTimeList = []
    tempStartTimeList = reservation.getStartTimeList(currentRestaurant)
    startTimeList = strip.it(tempStartTimeList)
    
    endTimeList = []
    tempEndTimeList = reservation.getEndTimeList(currentRestaurant)
    endTimeList = strip.it(tempEndTimeList)

    return render_template('deleteReservation.html', title="Delete Reservation", logged_in=logged_in, authLevel=authLevel, Name=namesList, tables=tablesList, startTime=startTimeList, endTime=endTimeList, reservationID=reservationIDList, listLen=len(namesList))

@app.route("/deleteReservation2/", methods=['GET', 'POST'])
@login_required
def deleteReservation2():
    reservation = Reservation()

    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    try:
        if request.method == "POST":
            # Item name that you wanna delete
            reservationID = request.form['reservationID']
        
  
            if reservation.deleteReservation(reservationID):
                flash("You have successfully deleted the reservation", 'info')
                return redirect(url_for('reservation'))
            else:
                flash("Reservation does not exist", 'danger')
                return redirect(url_for('deleteReservation'))
                
    except Exception as e:  
        return render_template('deleteReservation.html', error=e, title="Delete Reservation", logged_in=logged_in, authLevel=authLevel)



@app.route("/menu/", methods = ['GET', 'POST'])
@login_required
def menu():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    

    currentUser = User()
    currentUser.setLoginDetails(session['code'])

    currentRestaurant = currentUser.getBaseRestaurant()


    currentMenu = Menu()

    
    foodList, priceList, allergyList, idList, isAvailableList = currentMenu.getAvailableMenuList(currentRestaurant)


    return render_template('menu.html', title = "Menu" , logged_in=logged_in, authLevel=authLevel, foodList = foodList, priceList = priceList, allergyList = allergyList, listLen = len(foodList))


@app.route("/deleteMenu/", methods = ['GET', 'POST'])
@login_required
def deleteMenu():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    

    currentMenu = Menu()
    
    currentUser = User()
    currentUser.setLoginDetails(session['code'])

    currentRestaurant = currentUser.getBaseRestaurant()

    foodList, priceList, allergyList, idList, isAvailableList = currentMenu.getMenuList(currentRestaurant)


    error = ""

    try:
        if request.method == "POST":

            foodID = request.form['foodID']

            print(foodID)

            if foodID != None:
                
                if currentMenu.delete_menu(foodID) == 1:
                                                           
                    flash ("Food successfully deleted from the menu", "success")
                    return redirect(url_for('deleteMenu'))

                else:
                    flash ("Error deleting food from the menu", "danger")
                    return render_template('deleteMenu.html',error = e ,title="Delete Menu", logged_in=logged_in, authLevel=authLevel, foodList = foodList, priceList = priceList, allergyList = allergyList, idList = idList, listLen = len(priceList))


            else:
                flash ("Select a food to delete from the menu", "danger")
                return render_template('deleteMenu.html',error = e ,title="Delete Menu", logged_in=logged_in, authLevel=authLevel, foodList = foodList, priceList = priceList, allergyList = allergyList, idList = idList, listLen = len(priceList))
            
        else:
            return render_template('deleteMenu.html',error = e ,title="Delete Menu", logged_in=logged_in, authLevel=authLevel, foodList = foodList, priceList = priceList, allergyList = allergyList, idList = idList, listLen = len(priceList))

    

    except Exception as e:
        return render_template('deleteMenu.html',error = e ,title="Delete Menu", logged_in=logged_in, authLevel=authLevel, foodList = foodList, priceList = priceList, allergyList = allergyList, idList = idList, listLen = len(priceList))
    


@app.route("/account/", methods = ['GET'])
@login_required
def account():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    

    currentUser = User()
    currentUser.setLoginDetails(session['code'])

    currentRestaurant = currentUser.getBaseRestaurant()

    print(currentRestaurant)

    currentCode = currentUser.getCode()

    currentLevel = currentUser.getAuthorisation()



    return render_template('account.html', title = "Account" , logged_in=logged_in, authLevel=authLevel, currentLevel = currentLevel, currentCode = currentCode, currentRestaurant = currentRestaurant )








@app.route('/createFood/', methods=['POST', 'GET'])
@login_required
@admin_required
def createFood():

    currentUser = User()
    currentFood = Food()
    currentMenu = Menu()

    logged_in = session['logged_in']
    authLevel = session['authLevel']

    
    currentUser.setLoginDetails(session['code'])

    currentRestaurant = currentUser.getBaseRestaurant()

    print ("The restaurant is: ", currentRestaurant)
    
    error = ''

    try: 
        if request.method == "POST":

            print("here3")

            foodName = request.form['foodName']
            print(foodName)
            foodAllergy = request.form['foodAllergy']
            print(foodAllergy)
            foodPrice = request.form['priceOfFood']
        
            print(foodPrice)

            if foodName != None and foodAllergy != None and foodPrice != None:

                if  currentFood.validateName(foodName) == 1:
                    
                    if currentFood.validateAllergyInfo(foodAllergy) == 1:

                        if currentFood.validatePrice(foodPrice) == 1:
                            
                            if currentFood.checkName(foodName) != 1: #if food exists in table food

                            
                                if currentFood.createFood(foodName, foodPrice, foodAllergy) == 1:   #creates food in food table
                                    
                                    flash("Item has successfully been added to the Food Database", "success")
                                    return redirect(url_for('createFood'))
                                
                                else:
                                    flash("Item Failed to be added to the Food Database", "error")
                                    return redirect(url_for('createFood'))


                            else:
                                flash ("Restaurant is Invalid", "danger")
                                return render_template('createFood.html', error=error, title="Create Food", logged_in=logged_in, authLevel=authLevel)

                        else:
                            flash ("Failed to create food in food table", "danger")
                            return render_template('createFood.html', error=error, title="Create Food", logged_in=logged_in, authLevel=authLevel)
                    else:  
                        flash ("Food price is invalid", "danger")
                        return render_template('createFood.html', error=error, title="Create Food", logged_in=logged_in, authLevel=authLevel)

                else:
                    flash ("Food allergy is invalid", "danger")
                    return render_template('createFood.html', error=error, title="Create Food", logged_in=logged_in, authLevel=authLevel)

            else:
                flash ("Food name is invalid", "danger")
                return render_template('createFood.html', error=error, title="Create Food", logged_in=logged_in, authLevel=authLevel)

        else:
            
            return render_template('createFood.html', error=error, title="Create Food", logged_in=logged_in, authLevel=authLevel)

        
    except Exception as e:
        return render_template('createFood.html', title="Create Food", error=e, logged_in=logged_in, authLevel=authLevel)



@app.route("/updateFood/", methods = ['GET', 'POST'])
@login_required
def updateFood():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    


    currentFood = Food()

    foodList = currentFood.get_food_list()

    foodName = [item[0] for item in foodList]
    foodPrice = [item[1] for item in foodList]
    


    return render_template('updateFood.html', title = "Update Food" , logged_in=logged_in, authLevel=authLevel, foodName = foodName, foodPrice = foodPrice, listLen = len(foodName))



@app.route("/updateFood2/", methods = ['GET', 'POST'])
@login_required
def updateFood2():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    

    currentFood = Food()

    try:
        if request.method == "POST":


            foodName = request.form['foodName']

            session['foodName'] = foodName

            currentFood.setFoodDetails(foodName)

            foodPrice = currentFood.getPrice()
            allergyInfo = currentFood.getAllergyInfo()

            print(foodPrice)
            print(foodName)

            return render_template('updateFood2.html', title = "Update Food" , logged_in=logged_in, authLevel=authLevel, foodName = foodName, foodPrice = foodPrice, allergyInfo=allergyInfo)
            


    except Exception as e:
        
        return render_template('adminOptions.html', error=e, title="Restaurant Options", logged_in=logged_in, authLevel=authLevel)



@app.route("/updateFood3/", methods = ['GET', 'POST'])
@login_required
def updateFood3():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    currentFoodName = session['foodName']
    

    currentFood = Food()

    try:
        if request.method == "POST":

            print("method is posting at upd food 3")

            foodName = request.form['foodName']
            foodAllergy = request.form['foodAllergy']
            foodPrice = request.form['foodPrice']
            
            
            if foodName != None and foodAllergy != None and foodPrice != None:

                if currentFood.validateName(foodName) == 1:

                    if currentFood.validateAllergyInfo(foodAllergy) == 1:
                        
                        if currentFood.validatePrice(foodPrice) == 1:

                            if session['foodName'] == foodName:

                                if currentFood.updatePrice(foodPrice, foodName) ==1:

                                    if currentFood.updateAllergyInfo(foodAllergy, foodName) == 1:
                                        
                                            
                                        flash("Food updated successfully", "success")
                                        return redirect(url_for('updateFood'))


                                    else:
                                        flash("Error updating food allergy information", "danger")
                                        return redirect(url_for('updateFood'))

                                else:
                                    flash("Error updating food price", "danger")
                                    return redirect(url_for('updateFood'))


                            
                            
                            
                            else:

                                if currentFood.checkName(foodName) != 1:

                                    if currentFood.updateFoodName(session['foodName'], foodName) == 1:

                                        if currentFood.updatePrice(foodPrice, foodName) ==1:

                                            if currentFood.updateAllergyInfo(foodAllergy, foodName) == 1:
                                        
                                            
                                                flash("Food updated successfully", "success")
                                                return redirect(url_for('updateFood'))

                                            else:
                                                flash("Error updating food allergy information", "danger")
                                                return redirect(url_for('updateFood'))

                                        else:
                                            flash("Error updating food price", "danger")
                                            return redirect(url_for('updateFood'))

                                    else:
                                        flash("Food availability should either be 1 or 0", "danger")
                                        return redirect(url_for('updateFood'))

                                else:
                                    flash("This food already exist in the database", "danger")
                                    return redirect(url_for('updateFood'))

                        else:
                            flash("Food price is invalid (greater than 0)", "danger")
                            return redirect(url_for('updateFood'))



                    else:
                        flash("Food allergy is not valid (over 3 characters)", "danger")
                        return redirect(url_for('updateFood'))       

                else:
                    flash("Food name not valid (over 3 characters)", "danger")
                    return redirect(url_for('updateFood'))


            else:
                flash("Please fill in all forms", "danger")
                return redirect(url_for('updateFood'))

            


    except Exception as e:
        
        return render_template('adminOptions.html', error=e, title="Restaurant Options", logged_in=logged_in, authLevel=authLevel)




@app.route("/deleteFood/", methods = ['GET', 'POST'])
@login_required
def deleteFood():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    currentFood = Food()

    foodList = currentFood.get_food_list()

    foodName = [item[0] for item in foodList]
    foodPrice = [item[1] for item in foodList]
    foodAllergy = [item[2] for item in foodList]

    


    return render_template('deleteFood.html', title = "Delete Food" , logged_in=logged_in, authLevel=authLevel, foodName = foodName, foodPrice = foodPrice, listLen = len(foodName))


@app.route("/deleteFood2/", methods = ['GET', 'POST'])
@login_required

def deleteFood2():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    error = ""

    
    currentFood = Food()

    try:
        if request.method == "POST":

            print("method is posting")

            foodName = request.form['foodName']

            
            print(foodName)

            if foodName != None:
                
                if currentFood.delete_food(foodName) == 1:
                                                           
                    flash ("Food successfully deleted from the Food database", "success")
                    return redirect(url_for('deleteFood'))

                else:
                    flash ("Error deleting food from the menu", "danger")
                    return render_template('deleteFood.html', error=error, title="Create Food", logged_in=logged_in, authLevel=authLevel)


            else:
                flash ("Select a food to delete", "danger")
                return render_template('deleteFood.html', error=error, title="Create Food", logged_in=logged_in, authLevel=authLevel)


        else:
            return redirect(url_for('deleteFood'))


    except Exception as e:
        
        return render_template('home.html', error=e, title="Restaurant Options", logged_in=logged_in, authLevel=authLevel)



#STAFF / USER CRUD FOR MANAGER

@app.route('/createStaff/', methods=['POST', 'GET'])
@login_required
@manager_required

def createStaff():

    logged_in = session['logged_in']
    authLevel = session['authLevel']



    currentUser = User()
    currentUser.setLoginDetails(session['code'])

    currentRestaurant = currentUser.getBaseRestaurant()




    error = ''

    try:
        if request.method == "POST": 
            #getting data from form        
            code = request.form['code']
            BR = currentRestaurant
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
                            return redirect(url_for('admin'))
                        else:
                            flash("Invalid username syntax", "danger")
                            return render_template('createStaff.html', error=error, title="Create User", logged_in=logged_in, authLevel=authLevel)
                    else:
                        flash("Invalid password syntax", "danger")
                        return render_template('createStaff.html', error=error, title="Create User", logged_in=logged_in, authLevel=authLevel)
                else:
                    flash("Invalid username syntax", "danger")
                    return render_template('createStaff.html', error=error, title="Create User", logged_in=logged_in, authLevel=authLevel)
            else:                
                flash("Password and Confirm Password fields need to match", "danger")
                print("Passwords don't match")
                return render_template('createStaff.html', error=error, title="Create User", logged_in=logged_in, authLevel=authLevel)
        else:            
            return render_template('createStaff.html', error=error, title="Create User", logged_in=logged_in, authLevel=authLevel)        
    except Exception as e:                
        return render_template('createStaff.html', error=e, title="Create User", logged_in=logged_in, authLevel=authLevel)



@app.route("/deleteStaff/", methods=['GET', 'POST'])
@login_required
@manager_required

def deleteStaff():
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    currentUser = User()
    currentUser.setLoginDetails(session['code'])

    employeeCode = []
    tempEmployeeCode = currentUser.getStaffEmployeeCodes()
    employeeCode = strip.it(tempEmployeeCode)


    baseRestaurant = []
    tempBaseRestaurant = currentUser.getBaseRestaurants()
    baseRestaurant = strip.it(tempBaseRestaurant)

    authorisationLevel = []
    tempAuthorisationLevel = currentUser.getAuthorisationLevels()
    authorisationLevel = strip.it(tempAuthorisationLevel)

    try:
        if request.method == "POST":
            # Code that you wanna delete
            code = request.form['code']

            # Users code. DON'T DELETE
            usercode = session['code']

            if code != usercode:
                if currentUser.deleteUser(code):
                    flash(f"You have successfully deleted the user {code}", 'info')
                    return redirect(url_for('deleteStaff'))
                else:
                    flash(f"Account \"{code}\" does not exist", 'danger')
                    return redirect(url_for('deleteStaff'))
            else:
                flash("You cannot delete your own user", "danger")
                return redirect(url_for('deleteStaff'))
    except Exception as e:  
        return render_template('deleteStaff.html', error=e, title="Delete Staff", logged_in=logged_in, authLevel=authLevel)



    return render_template('deleteStaff.html', title = "Delete Staff", logged_in=logged_in, authLevel=authLevel, baseRestaurant=baseRestaurant, authorisationLevel=authorisationLevel, employeeCode=employeeCode, codeLen=len(employeeCode))



@app.route("/updateStaff/", methods=['GET', 'POST'])
@login_required
@manager_required

def updateStaff():
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    currentUser = User()
    currentUser.setLoginDetails(session['code'])

    employeeCode = []
    tempEmployeeCode = currentUser.getStaffEmployeeCodes() 
    employeeCode = strip.it(tempEmployeeCode)


    baseRestaurant = []
    tempBaseRestaurant = currentUser.getBaseRestaurants()
    baseRestaurant = strip.it(tempBaseRestaurant)


    authorisationLevel = []
    tempAuthorisationLevel = currentUser.getAuthorisationLevels()
    authorisationLevel = strip.it(tempAuthorisationLevel)

    return render_template('updateStaff.html', title = "Update Staff", logged_in=logged_in, authLevel=authLevel, baseRestaurant=baseRestaurant, authorisationLevel=authorisationLevel, employeeCode=employeeCode, codeLen=len(employeeCode))




@app.route("/updateStaff2/", methods=['GET', 'POST'])
@login_required
@manager_required
def updateStaff2():
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    currentUser = User()
    currentUser.setLoginDetails(session['code'])

    currentRestaurant = currentUser.getBaseRestaurant()




    if request.method == "POST":
        code = request.form['code']
        session['previousCode'] = code
        currentUser.setLoginDetails(session['previousCode'])

        AL = currentUser.getAuthorisation()

        BR = currentRestaurant

        print(BR)
        print(AL)


        return render_template("updateStaff2.html", title = "Update Staff", logged_in=logged_in, authLevel=authLevel, AL=AL, BR=BR, code=code)
    
    return render_template("updateStaff2.html", title = "Update Staff", logged_in=logged_in, authLevel=authLevel)




@app.route("/updateStaff3/", methods=['GET', 'POST'])
@login_required
@manager_required

def updateStaff3():
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    currentUser = User()

    currentUser.setLoginDetails(session['code'])

    currentRestaurant = currentUser.getBaseRestaurant()

    

    try:
        if request.method == "POST":
            
            code = request.form['code']
            base = currentRestaurant
            auth = request.form['auth']
            print(base)



            if code != None and base != None and auth != None:
    
                if currentUser.validateCodeSyntax(code) == 1:
        
                    if currentUser.validateAuthorisationSyntax(auth) == 1:
            
                        if currentUser.validateBaseRestaurantSyntax(base) == 1:
                

                            previousCode = session['previousCode']
                            
                            currentUser.updateBaseRestaurant(previousCode, base)
                            currentUser.updateAuthorisation(previousCode, auth)
                            session['authLevel'] = auth
                            authLevel = session['authLevel']
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
                            return render_template('updateStaff2.html', error="", title = "Update User", logged_in=logged_in, authLevel=authLevel)
                    else:
                        return render_template('updateStaff2.html', error="", title = "Update User", logged_in=logged_in, authLevel=authLevel)
                else:
                    return render_template('updateStaff2.html', error="", title = "Update User", logged_in=logged_in, authLevel=authLevel)
            else:                
                flash("Please don't leave any field empty", "danger")
                return render_template('updateStaff2.html', error="", title = "Update User", logged_in=logged_in, authLevel=authLevel)
    except Exception as e:                
        return render_template('updateStaff2.html', error=e, title = "Update User", logged_in=logged_in, authLevel=authLevel)



@app.route("/createItem/", methods = ['GET', 'POST'])
@login_required
@admin_required

def createItem():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    item = Item()
    
    error = ''
    
    try:
        if request.method == "POST": 
            #getting data from form        
            itemName = request.form['itemName']
            quantity = request.form['itemQuantity']
            stockLimit = request.form['itemSL']                   
            if itemName != None and quantity != None and stockLimit != None:
                if item.validateName(itemName) == 1:
                    if item.validateQuantity(quantity) == 1:
                        if item.validateQuantity2(quantity, stockLimit) == 1:
                            if item.validateStockLimit(stockLimit) == 1:
                                if item.checkName(itemName) != 1:
                                    if item.createItem(itemName, quantity, stockLimit) == 1:               
                                        flash("Item has been created", "success")
                                        return redirect(url_for('home'))
                                    else:
                                        flash("Could not create item", "danger")
                                        return render_template('createItem.html', error=error, title="Create Invnentory", logged_in=logged_in, authLevel=authLevel)
                                else:
                                    flash("Item already exists in the restaurant", "danger")
                                    return render_template('createItem.html', error=error, title="Create Item", logged_in=logged_in, authLevel=authLevel)
                            else:
                                flash("Invalid stock limit", "danger")
                                return render_template('createItem.html', error=error, title="Create Item", logged_in=logged_in, authLevel=authLevel)
                        else:
                            flash("Quantity cannot be more than stock limit", "danger")
                            return render_template('createItem.html', error=error, title="Create Item", logged_in=logged_in, authLevel=authLevel)
                    else:
                        flash("Invalid quantity", "danger")
                        return render_template('createItem.html', error=error, title="Create Item", logged_in=logged_in, authLevel=authLevel)
                else:
                    flash("Item not available in the warehouse", "danger")
                    return render_template('createItem.html', error=error, title="Create Item", logged_in=logged_in, authLevel=authLevel)
            else:                
                flash("Fields cannot be empty", "danger")
                return render_template('createItem.html', error=error, title="Create Item", logged_in=logged_in, authLevel=authLevel)
        else:            
            return render_template('createItem.html', error=error, title="Create Item", logged_in=logged_in, authLevel=authLevel)        
    except Exception as e:                
        return render_template('createItem.html', error=e, title="Create Item", logged_in=logged_in, authLevel=authLevel)


@app.route("/deleteItem/", methods = ['GET', 'POST'])
@login_required
@admin_required
def deleteItem():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    
    item = Item()
    
    
    itemList = item.get_item_list()
    itemName, itemQuantity, itemSL = itemList
    


    return render_template('deleteItem.html', title = "Delete Item" , logged_in=logged_in, authLevel=authLevel, itemName=itemName,itemQuantity=itemQuantity, itemSL=itemSL, listLen=len(itemName))

@app.route("/deleteItem2/", methods = ['GET', 'POST'])
@login_required
@admin_required
def deleteItem2():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    item = Item()
    
    try:
        if request.method == "POST":
            # Item name that you wanna delete
            itemName = request.form['itemName']
  
            if item.delete_item(itemName):
                flash(f"You have successfully deleted the item {itemName}", 'info')
                return redirect(url_for('deleteItem'))
            else:
                flash(f"Item \"{itemName}\" does not exist", 'danger')
                return redirect(url_for('deleteItem'))
                
    except Exception as e:  
        return render_template('deleteItem.html', title = "Delete Item" , logged_in=logged_in, authLevel=authLevel)


   




@app.route("/updateItem/", methods = ['GET', 'POST'])
@login_required
@admin_required

def updateItem():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    
    item = Item()
    
    
    itemList = item.get_item_list()
    itemName, itemQuantity, itemSL = itemList



    return render_template('updateItem.html', title = "Update Item" , logged_in=logged_in, authLevel=authLevel, itemName=itemName,itemQuantity=itemQuantity, itemSL=itemSL, listLen=len(itemName))




@app.route("/updateItem2/", methods = ['GET', 'POST'])
@login_required
@admin_required
def updateItem2():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    
    itemName = request.form['itemName']
    session['itemName'] = itemName


    return render_template('updateItem2.html', title = "Update Item" , logged_in=logged_in, authLevel=authLevel)


@app.route("/updateItem3/", methods = ['GET', 'POST'])
@login_required
@admin_required

def updateItem3():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    itemName = session['itemName']

    item = Item()
    
    try:
        if request.method == "POST":
            
            itemSL = request.form['itemSL']
            
            if itemSL != None:
                if item.validateStockLimit(itemSL) == 1:
                    if item.updateStockLimit(itemSL, itemName):
                        flash(f"You have successfully updated the item stock limit {itemName}", 'info')
                        return redirect(url_for('updateItem'))
                    else:
                        flash("Invalid stock limit input", "danger")
                        return render_template('updateItem2.html', title = "Update Item" , logged_in=logged_in, authLevel=authLevel)
                else:
                    flash("Invalid stock limit input", "danger")
                    return render_template('updateItem2.html', title = "Update Item" , logged_in=logged_in, authLevel=authLevel)
            else:                
                flash("Please don't leave any field empty", "danger")
                return render_template('updateItem2.html', title = "Update Item" , logged_in=logged_in, authLevel=authLevel)
    except Exception as e:                
        return render_template('updateItem2.html', title = "Update Item" , logged_in=logged_in, authLevel=authLevel)



@app.route("/orderItems/", methods=['GET', 'POST'])
@login_required
@chef_required
def orderItems():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    
    item = Item()
    
    
    itemList = item.get_item_list()
    itemName, itemQuantity, itemSL = itemList

    return render_template('orderItemsWarehouse.html', title = "Order Item" , logged_in=logged_in, authLevel=authLevel, itemName=itemName,itemQuantity=itemQuantity, itemSL=itemSL, listLen=len(itemName))


@app.route("/orderItems2/", methods=['GET', 'POST'])
@login_required
@chef_required
def orderItems2():
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    item = Item()
    
    if request.method == "POST":
        
        itemName = request.form['itemName']
        session['itemName'] = itemName

        item.setItemDetails(itemName)

        itemQuant = item.getQuantity()

        itemSL = item.getStockLimit()

    
    return render_template('orderItemsWarehouse2.html', title = "Order Item" , logged_in=logged_in, authLevel=authLevel, itemQuant=itemQuant, itemSL=itemSL)


@app.route("/orderItems3/", methods=['GET', 'POST'])
@login_required
@chef_required
def orderItems3():
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    itemName = session['itemName']
    
    item = Item()
    
    item.setItemDetails(itemName)
    
    itemName = item.getName()
    
    try:
        
        if request.method == "POST":
            
            
            quantToAdd = int(request.form['itemQuant'])
            
            
            if quantToAdd != None:
                itemSL = int(item.getStockLimit())
                itemQuant = int(item.getQuantity())
                

                if item.checkItemQuantLessThanStockLimit(itemSL, itemQuant, quantToAdd) == 1:

                    item.updateQuantity(quantToAdd + itemQuant, itemName)

                    flash(f"You have successfully updated the item {itemName}", 'info')
                    return redirect(url_for('adminOptions'))
                else:
                    flash("The quantity must be smaller than the stock limit", "danger")
                    return render_template('orderItemsWarehouse2.html', title = "Order Item" , logged_in=logged_in, authLevel=authLevel, itemQuant=itemQuant, itemSL=itemSL)
            else:                
                flash("Please don't leave any field empty", "danger")
                return render_template('orderItemsWarehouse2.html', title = "Order Item" , logged_in=logged_in, authLevel=authLevel, itemQuant=itemQuant, itemSL=itemSL)
    except Exception as e:                
        flash(e)
        return render_template('home.html', title = "Order Item" , logged_in=logged_in, authLevel=authLevel)


@app.route("/payment/", methods = ['GET', 'POST'])
def payment():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    
    

    return render_template('payment.html', title = "Update Item" , logged_in=logged_in, authLevel=authLevel)



@app.route("/receipt/", methods = ['GET', 'POST'])
def receipt():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    orderPay = Order()

    sameData, diffData = orderPay.showReceipt(session['orderID'])

    sameData.insert(0, request.form['name'])
    
    session['name'] = request.form['name']
    
    if sameData[5] != None:
        sameData[5] = sameData[5][0:10]

    print(sameData[5])
    


    return render_template('receipt.html', title = "Receipt" , logged_in=logged_in, authLevel=authLevel, sameData=sameData, diffData=diffData, dataLen=len(diffData))

@app.route("/generate_pdfReceipt/", methods=['GET', 'POST'])
def generate_pdfReceipt():
    name = session['name']
    orderPay = Order()
    sameData, diffData = orderPay.showReceipt(session['orderID'])
    
    sameData.insert(0, name)
    
    if sameData[5] is not None:
        sameData[5] = sameData[5][0:10]
    #rendered_html = render_template('receipt.html', sameData=sameData, diffData=diffData, dataLen=len(diffData))

    # Get food items for the order
    food_items = orderPay.getSpecificFoodList(session['orderID'])

    # Create PDF using ReportLab
    response = make_response()
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=receipt.pdf'

    # Create a PDF buffer using ReportLab
    pdf_buffer = response.stream
    c = canvas.Canvas(pdf_buffer, pagesize=letter)

    # Set up the title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Receipt")

    # Set up the first table header
    first_table_header = ["Name", "Order ID", "Restaurant Name", "Total Price", "Table Number", "Date Of Payment", "Discount Value"]
    
    sameData = ["None" if empty == None else empty for empty in sameData]
    
    # Create data for the first table
    first_table_data = [sameData]

    # Insert first table header
    first_table_data.insert(0, first_table_header)

    # Create the first table and set style
    first_table = Table(first_table_data)
    first_table_style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                    ('GRID', (0, 0), (-1, -1), 1, colors.black)])
    first_table.setStyle(first_table_style)

    # Calculate first table width and height
    first_table_width, first_table_height = first_table.wrap(400, 200)

    # Draw the first table on the canvas
    first_table.drawOn(c, (letter[0] - first_table_width) / 2, 600 - first_table_height)

    # Set up the second table header
    second_table_header = ["Food", "Price"]

    # Create data for the second table
    second_table_data = diffData

    # Insert second table header
    second_table_data.insert(0, second_table_header)

    # Create the second table and set style
    second_table = Table(second_table_data)
    second_table_style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                                     ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                     ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                     ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                     ('GRID', (0, 0), (-1, -1), 1, colors.black)])
    second_table.setStyle(second_table_style)

    # Calculate second table width and height
    second_table_width, second_table_height = second_table.wrap(400, 200)

    # Draw the second table on the canvas
    second_table.drawOn(c, (letter[0] - second_table_width) / 2, 600 - first_table_height - second_table_height - 30)

    c.showPage()
    c.save()

    return response

if __name__ == "__main__":
    app.run( debug=True ,host="127.0.0.1", port=5050)