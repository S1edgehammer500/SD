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
from Model.menuModel import *
from Model.foodModel import *
from Model.reportModel import *
from Model.inventoryModel import *
from Model.itemModel import *


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
                            return redirect(url_for('createMenu'))

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

    
    foodList, priceList, allergyList, idList = currentMenu.getMenuList(currentRestaurant)


    return render_template('updateMenu.html', title = "Update Menu" , logged_in=logged_in, authLevel=authLevel, foodList = foodList, priceList = priceList, listLen = len(foodList), idList = idList)

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

    
    

    if request.method == "POST":
        name = request.form['foodName']
        currentFood.setFoodDetails(name)

        price = currentFood.getPrice()

        allergy = currentFood.getAllergyInfo()






    return render_template('updateMenu2.html', title = "Update Menu" , logged_in=logged_in, authLevel=authLevel, price = price, name = name, allergy = allergy)


@app.route("/updateMenu3/", methods = ['GET', 'POST'])
@login_required
def updateMenu3():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    

    currentUser = User()
    currentUser.setLoginDetails(session['code'])

    currentRestaurant = currentUser.getBaseRestaurant()


    currentMenu = Menu()
    currentFood = Food()


    return redirect(url_for('updateMenu'))





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
            discountID = request.form['discountID']
            discountValue = request.form['discountValue']

                 
            if discountID != None and discountValue != None:
                if discount.checkDiscountValue(discountValue) != 1:
                    if discount.validateDiscountIDSyntax(discountID) == 1:
                        if discount.validateDiscountValueSyntax(discountValue) == 1:
        

                            if discount.createDiscount(discountID, discountValue) == 1:                      
                                flash("Discount is now registered", "success")
                                return redirect(url_for('home'))
                            else:
                                flash("Unexpected Error occured", "danger")
                                return render_template('home.html', error=error, title="Discount Options", logged_in=logged_in, authLevel=authLevel)
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

    print("delete")

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
        
            
            dID = request.form['discountID']
            dValue = request.form['discountValue']

            print(f"dID {dID}")
            print(f"dValue {dValue}")

            if dID != None and dValue != None:
    
                if discount.validateDiscountIDSyntax(dID) == 1:
        
                    if discount.validateDiscountValueSyntax(dValue) == 1:

                        previousdID = session['previousdID']
                        

                        if discount.updateDiscountValue(previousdID, dValue):
                            print(f"Previous dID {previousdID}")

                            if dID != previousdID:
                                discount.updateDiscountID(previousdID, dID)


                            flash(f"You have successfully updated the discount {dID}", 'info')
                            return redirect(url_for('adminOptions'))
                        else:
                            flash("Unexpected error occured")
                            return render_template('updateDiscount2.html', error="", title = "Update Discount", logged_in=logged_in, authLevel=authLevel)
                    else:
                        flash("Discount value is in the wrong format")
                        return render_template('updateDiscount2.html', error="", title = "Update Discount", logged_in=logged_in, authLevel=authLevel)
                else:
                    flash("Discount ID is in the wrong format")
                    return render_template('updateDiscount2.html', error="", title = "Update Discount", logged_in=logged_in, authLevel=authLevel)
            else:                
                flash("Please don't leave any field empty", "danger")
                return render_template('updateDiscount2.html', error="", title = "Update Discount", logged_in=logged_in, authLevel=authLevel)
    except Exception as e:                
        return render_template('updateDiscount2.html', error=e, title = "Update Discount", logged_in=logged_in, authLevel=authLevel)


#### Reports

@app.route("/salesReport/", methods=['GET', 'POST'])
@login_required
@admin_required
def salesReport():  
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    startDate = "2024-01-01"
    endDate = "2024-01-31"


    selected_restaurant = "Manchester"
    
        
    records = sales(startDate, endDate)
    

    if records == []:
        flash("No information for this date range")
        return redirect(url_for('adminOptions'))
    
    return render_template('salesReport.html', title = "Sales Report", logged_in=logged_in, authLevel=authLevel, records=records, recordsLen=len(records))
    
@app.route("/averageSalesReport/", methods=['GET', 'POST'])
@login_required
@admin_required
def averageSalesReport():  
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    startDate = "2024-01-01"
    endDate = "2024-01-31"


    selected_restaurant = "Manchester"
    
        
    records = averageSales(startDate, endDate)
    

    if records == []:
        flash("No information for this date range")
        return redirect(url_for('adminOptions'))
    
    return render_template('averageSalesReport.html', title = "Average Sales Report", logged_in=logged_in, authLevel=authLevel, records=records, recordsLen=len(records))
    

@app.route("/averageServingTimeReport/", methods=['GET', 'POST'])
@login_required
@admin_required
def averageServingTimeReport():  
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    startDate = "2024-01-01"
    endDate = "2024-01-31"


    selected_restaurant = "Manchester"
    
        
    records = averageServingTime(startDate, endDate)
    

    if records == []:
        flash("No information for this date range")
        return redirect(url_for('adminOptions'))
    
    return render_template('averageServingTimeReport.html', title = "Average Sales Report", logged_in=logged_in, authLevel=authLevel, records=records, recordsLen=len(records))

@app.route("/totalDiscountAmountReport/", methods=['GET', 'POST'])
@login_required
@admin_required
def totalDiscountAmountReport():  
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    startDate = "2024-01-01"
    endDate = "2024-01-31"


    selected_restaurant = "Manchester"
    
        
    records = totalDiscountAmount(startDate, endDate)
    

    if records == []:
        flash("No information for this date range")
        return redirect(url_for('adminOptions'))
    
    return render_template('totalDiscountAmountReport.html', title = "Total Discount Amount Report", logged_in=logged_in, authLevel=authLevel, records=records, recordsLen=len(records))

@app.route("/averageDiscountAmountReport/", methods=['GET', 'POST'])
@login_required
@admin_required
def averageDiscountAmountReport():  
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    startDate = "2024-01-01"
    endDate = "2024-01-31"


    selected_restaurant = "Manchester"
    
        
    records = averageDiscountAmount(startDate, endDate)
    

    if records == []:
        flash("No information for this date range")
        return redirect(url_for('adminOptions'))
    
    return render_template('averageDiscountAmountReport.html', title = "Total Discount Amount Report", logged_in=logged_in, authLevel=authLevel, records=records, recordsLen=len(records))


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








@app.route("/order/")
@login_required
def order():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    return render_template('order.html', title="order", logged_in=logged_in, authLevel=authLevel)

@app.route("/createOrder/")
@login_required
def createOrder():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    currentUser = User()
    currentUser.setLoginDetails(session['code'])

    currentRestaurant = currentUser.getBaseRestaurant()


    currentMenu = Menu()

    
    foodList, priceList, allergyList, idList = currentMenu.getMenuList(currentRestaurant)
    
    return render_template('createOrder.html', title="order", logged_in=logged_in, authLevel=authLevel, foodList = foodList, priceList = priceList, allergyList = allergyList, idList = idList, listLen = len(foodList))





@app.route("/createOrder2/")
@login_required
def createOrder2():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    currentUser = User()
    currentUser.setLoginDetails(session['code'])

    currentRestaurant = currentUser.getBaseRestaurant()


    currentMenu = Menu()

    
    foodList, priceList, allergyList, idList = currentMenu.getMenuList(currentRestaurant)
    
    return render_template('createOrder2.html', title="order", logged_in=logged_in, authLevel=authLevel, foodList = foodList, priceList = priceList, allergyList = allergyList, idList = idList, listLen = len(foodList))


@app.route("/deleteOrder/")
@login_required
def deleteOrder():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    return render_template('deleteOrder.html', title="order", logged_in=logged_in, authLevel=authLevel)

@app.route("/updateOrder/")
@login_required
def updateOrder():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    return render_template('updateOrder.html', title="order", logged_in=logged_in, authLevel=authLevel)


@app.route("/removeFromOrder/")
@login_required
def removeFromOrder():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    return render_template('removeFromOrder.html', title="order", logged_in=logged_in, authLevel=authLevel)



@app.route("/applyDiscountOrder/")
@login_required
def applyDiscountOrder():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    discount = Discount()

    dIDs, dValues = discount.get_discounts()
  
    return render_template('applyDiscountOrder.html', title = "Update Discount", logged_in=logged_in, authLevel = authLevel, dIDs=dIDs, dValues=dValues, discountsLen = len(dIDs))


@app.route("/reservation/")
@login_required
def reservation():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    return render_template('reservation.html', title="Admin Options", logged_in=logged_in, authLevel=authLevel)


@app.route("/createReservation/")
@login_required
def createReservation():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    return render_template('createReservation.html', title="Admin Options", logged_in=logged_in, authLevel=authLevel)

@app.route("/updateReservation/")
@login_required
def updateReservation():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    return render_template('updateReservation.html', title="Admin Options", logged_in=logged_in, authLevel=authLevel)

@app.route("/deleteReservation/")
@login_required
def deleteReservation():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']

    return render_template('deleteReservation.html', title="Admin Options", logged_in=logged_in, authLevel=authLevel)




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

    
    foodList, priceList, allergyList, idList = currentMenu.getMenuList(currentRestaurant)


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

    foodList, priceList, allergyList, idList = currentMenu.getMenuList(currentRestaurant)


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

            print(foodPrice)
            print(foodName)

            return render_template('updateFood2.html', title = "Update Food" , logged_in=logged_in, authLevel=authLevel, foodName = foodName, foodPrice = foodPrice)
            


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
            foodAvailable = request.form['foodAvailable']
            
            
            if foodName != None and foodAllergy != None and foodPrice != None and foodAvailable !=None:

                if currentFood.validateName(foodName) == 1:

                    if currentFood.validateAllergyInfo(foodAllergy) == 1:
                        
                        if currentFood.validatePrice(foodPrice) == 1:

                            if currentFood.validateAvailability(foodAvailable) == 1:
                                

                                if session['foodName'] == foodName:

                                    if currentFood.updatePrice(foodPrice, foodName) ==1:

                                        if currentFood.updateAllergyInfo(foodAllergy, foodName) == 1:
                                            
                                            if currentFood.updateAvailability(foodAvailable, foodName) == 1:
                                                
                                                flash("Food updated successfully", "success")
                                                return redirect(url_for('updateFood'))

                                            else:
                                                flash("Food availability should either be 1 or 0", "danger")
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
                                            
                                                    if currentFood.updateAvailability(foodAvailable, foodName) == 1:
                                                
                                                        flash("Food updated successfully", "success")
                                                        return redirect(url_for('updateFood'))

                                                    else:
                                                        flash("Food availability should either be 1 or 0", "danger")
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
                                flash("Food availability should either be 1 or 0", "danger")
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
    foodAvailable = [item[2] for item in foodList]
    foodAllergy = [item[3] for item in foodList]

    


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
    tempEmployeeCode = currentUser.getEmployeeCodes()
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
    
    



    return render_template('createItem.html', title = "Create Item" , logged_in=logged_in, authLevel=authLevel)



@app.route("/deleteItem/", methods = ['GET', 'POST'])
@login_required
@admin_required

def deleteItem():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    



    return render_template('deleteItem.html', title = "Delete Item" , logged_in=logged_in, authLevel=authLevel)




@app.route("/updateItem/", methods = ['GET', 'POST'])
@login_required
@admin_required

def updateItem():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    



    return render_template('updateItem.html', title = "Update Item" , logged_in=logged_in, authLevel=authLevel)




@app.route("/updateItem2/", methods = ['GET', 'POST'])
@login_required
@admin_required

def updateItem2():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    



    return render_template('updateItem2.html', title = "Update Item" , logged_in=logged_in, authLevel=authLevel)


@app.route("/updateItem3/", methods = ['GET', 'POST'])
@login_required
@admin_required

def updateItem3():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    



    return render_template('updateItem2.html', title = "Update Item" , logged_in=logged_in, authLevel=authLevel)


@app.route("/orderItem/", methods = ['GET', 'POST'])
@login_required
@admin_required

def orderItem():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    



    return render_template('orderItem.html', title = "Update Item" , logged_in=logged_in, authLevel=authLevel)



@app.route("/orderItem2/", methods = ['GET', 'POST'])
@login_required
@admin_required

def orderItem2():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    



    return render_template('orderItem2.html', title = "Update Item" , logged_in=logged_in, authLevel=authLevel)


@app.route("/orderItem3/", methods = ['GET', 'POST'])
@login_required
@admin_required

def orderItem3():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    



    return render_template('orderItem2.html', title = "Update Item" , logged_in=logged_in, authLevel=authLevel)





if __name__ == "__main__":
    app.run( debug=True ,host="127.0.0.1", port=5050)