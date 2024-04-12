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


@app.route("/deleteFoodMenu/", methods = ['GET', 'POST'])
@login_required
def deleteFoodMenu():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    

    currentUser = User()
    currentUser.setLoginDetails(session['code'])

    currentRestaurant = currentUser.getBaseRestaurant()


    currentMenu = Menu()

    
    foodList, priceList, allergyList, idList = currentMenu.getMenuList(currentRestaurant)


    return render_template('deleteFoodMenu.html', title = "Delete Menu" , logged_in=logged_in, authLevel=authLevel, foodList = foodList, priceList = priceList, listLen = len(foodList), idList = idList)


@app.route("/deleteFoodMenu2/", methods = ['GET', 'POST'])
@login_required
def deleteFoodMenu2():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    error = ""

    
    currentMenu = Menu()

    try:
        if request.method == "POST":

            print("method is posting")

            foodID = request.form['foodID']

            
            print(foodID)

            if foodID != None:
                
                if currentMenu.delete_menu(foodID) == 1:
                                                           
                    flash ("Food successfully deleted from the menu", "success")
                    return redirect(url_for('deleteFoodMenu'))

                else:
                    flash ("Error deleting food from the menu", "danger")
                    return render_template('deleteFoodMenu.html', error=error, title="Create Food", logged_in=logged_in, authLevel=authLevel)


            else:
                flash ("Select a food to delete", "danger")
                return render_template('deleteFoodMenu.html', error=error, title="Create Food", logged_in=logged_in, authLevel=authLevel)


        else:
            return redirect(url_for('deleteFoodMenu'))


    except Exception as e:
        
        return render_template('home.html', error=e, title="Restaurant Options", logged_in=logged_in, authLevel=authLevel)


    



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


@app.route('/createFoodMenu/', methods=['POST', 'GET'])
@login_required
@admin_required
def createFoodMenu():

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
                            
                            if currentFood.checkName(foodName) == 1: #if food exists in table food

                                if currentMenu.validateRestaurantName(currentRestaurant) == 1: 
                                    
                                        if currentMenu.validateFoodName(foodName) == 1:
                                            
                                            if currentMenu.checkRestaurantFood(currentRestaurant,foodName) != 1:

                                                if currentMenu.createMenu(currentRestaurant, foodName) == 1:

                                                    flash("Item has successfully been added to the menu", "success")
                                                    return redirect(url_for('menu'))

                                                else:
                                                    flash ("Failed to add item to the menu", "danger")
                                                    return render_template('createFoodMenu.html', error=error, title="Create Food", logged_in=logged_in, authLevel=authLevel)


                                            else:
                                                flash ("Food item already exists in the menu table", "danger")
                                                return render_template('createFoodMenu.html', error=error, title="Create Food", logged_in=logged_in, authLevel=authLevel)

                                        
                                        else:
                                            flash ("Food Item does not exist in food table", "danger")
                                            return render_template('createFoodMenu.html', error=error, title="Create Food", logged_in=logged_in, authLevel=authLevel)

                                else:
                                    flash ("Restaurant is Invalid", "danger")
                                    return render_template('createFoodMenu.html', error=error, title="Create Food", logged_in=logged_in, authLevel=authLevel)

                                

                            
                            else:   #if food doesnt exist in food
                                
                                if currentFood.createFood(foodName, foodPrice, foodAllergy) == 1:   #creates food in food table
                                    
                                    if currentMenu.validateRestaurantName(currentRestaurant) == 1: 
                                        
                                        if currentMenu.validateFoodName(foodName) == 1:
                                            
                                            if currentMenu.checkRestaurantFood(currentRestaurant,foodName) != 1:

                                                if currentMenu.createMenu(currentRestaurant, foodName) == 1:

                                                    flash("Item has successfully been added to the menu", "success")
                                                    return redirect(url_for('menu'))

                                                else:
                                                    flash ("Failed to add item to the menu", "danger")
                                                    return render_template('createFoodMenu.html', error=error, title="Create Food", logged_in=logged_in, authLevel=authLevel)


                                            else:
                                                flash ("Food item already exists in the menu table", "danger")
                                                return render_template('createFoodMenu.html', error=error, title="Create Food", logged_in=logged_in, authLevel=authLevel)

                                        
                                        else:
                                            flash ("Food Item does not exist in food table", "danger")
                                            return render_template('createFoodMenu.html', error=error, title="Create Food", logged_in=logged_in, authLevel=authLevel)

                                    else:
                                        flash ("Restaurant is Invalid", "danger")
                                        return render_template('createFoodMenu.html', error=error, title="Create Food", logged_in=logged_in, authLevel=authLevel)

                                else:
                                    flash ("Failed to create food in food table", "danger")
                                    return render_template('createFoodMenu.html', error=error, title="Create Food", logged_in=logged_in, authLevel=authLevel)
                        else:  
                            flash ("Food price is invalid", "danger")
                            return render_template('createFoodMenu.html', error=error, title="Create Food", logged_in=logged_in, authLevel=authLevel)

                    else:
                        flash ("Food allergy is invalid", "danger")
                        return render_template('createFoodMenu.html', error=error, title="Create Food", logged_in=logged_in, authLevel=authLevel)

                else:
                    flash ("Food name is invalid", "danger")
                    return render_template('createFoodMenu.html', error=error, title="Create Food", logged_in=logged_in, authLevel=authLevel)

            else:
                flash ("Fields cannot be empty", "danger")
                return render_template('createFoodMenu.html', error=error, title="Create Food", logged_in=logged_in, authLevel=authLevel)

            

        
        else: 
            return(render_template('createFoodMenu.html', title="Create Food", logged_in=logged_in, authLevel = authLevel))
    
    except Exception as e:
        print("here2")
        return(render_template('createFoodMenu.html', title="Create Food", error = e, logged_in=logged_in, authLevel = authLevel))
    

@app.route("/updateFoodMenu/", methods = ['GET', 'POST'])
@login_required
def updateFoodMenu():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    

    currentUser = User()
    currentUser.setLoginDetails(session['code'])

    currentRestaurant = currentUser.getBaseRestaurant()


    currentMenu = Menu()

    
    foodList, priceList, allergyList, idList = currentMenu.getMenuList(currentRestaurant)


    return render_template('updateFoodMenu.html', title = "Update Menu" , logged_in=logged_in, authLevel=authLevel, foodList = foodList, priceList = priceList, listLen = len(foodList), idList = idList)

@app.route("/updateFoodMenu2/", methods = ['GET', 'POST'])
@login_required
def updateFoodMenu2():
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






    return render_template('updateFoodMenu2.html', title = "Update Menu" , logged_in=logged_in, authLevel=authLevel, price = price, name = name, allergy = allergy)


@app.route("/updateFoodMenu3/", methods = ['GET', 'POST'])
@login_required
def updateFoodMenu3():
    # check to see what navbar to display
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    

    currentUser = User()
    currentUser.setLoginDetails(session['code'])

    currentRestaurant = currentUser.getBaseRestaurant()


    currentMenu = Menu()
    currentFood = Food()


    return redirect(url_for('updateFoodMenu'))





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
def deleteDiscount():
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    discount = Discount()
    
    dIDs, dValues = discount.get_discounts()

    return render_template('deleteDiscount.html', title = "Delete Discount", logged_in=logged_in, authLevel = authLevel, dIDs=dIDs, dValues=dValues, discountsLen = len(dIDs))

@app.route("/deleteDiscount2/", methods=['GET', 'POST'])
@login_required
@admin_required
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
def updateDiscount():
    
    logged_in = session['logged_in']
    authLevel = session['authLevel']
    
    discount = Discount()

    dIDs, dValues = discount.get_discounts()
  
    return render_template('updateDiscount.html', title = "Update Discount", logged_in=logged_in, authLevel = authLevel, dIDs=dIDs, dValues=dValues, discountsLen = len(dIDs))

@app.route("/updateDiscount2/", methods=['GET', 'POST'])
@login_required
@admin_required
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
@admin_required
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

                            print("hello")

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


if __name__ == "__main__":
    app.run( debug=True ,host="127.0.0.1", port=5050)