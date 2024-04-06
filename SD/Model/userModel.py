from passlib.hash import sha256_crypt
import re
from Model.Database import *
from flask import flash

#User class
class User:
    def __init__(self):
        # Because of the model = User() line in App we need all of these to be empty to begin with
        self.__employeeCode = ""
        self.__password = ""
        self.__authorisationLevel = ""
        self.__baseRestaurant = ""
        self.__loggedStatus = False

    #getters
    def getPassword(self):
        return self.__password
    
    def getCode(self):
        return self.__employeeCode
    
    def getAuthorisation(self):
        return self.__authorisationLevel
    
    def getBaseRestaurant(self):
        return self.__baseRestaurant
    
    def getPasswordLength(self):
        return len(self.getPassword())

    def getLoggedStatus(self):
        return self.__loggedStatus
    
    def get_users(self):
        try:
            conn, cur = openConnection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM users")
            rows = cur.fetchall()
            users = [(row[0], row[2], row[3]) for row in rows]
            conn.close()
            return users
        except sqlite3.Error as e:
            print("Error fetching discounts:", e)
            return []
        
    #setters
    
    #making logging in true when user loggs in needs a bit of fixing
    def setLoggedStatus(self, usercode, password):
        self.__loggedStatus = True
        return 1 
        
    def setPassword(self, password):



        if self.validateUserpasswordSyntax(password):
            self.__password = sha256_crypt.hash(str(password))
            return 1
        else:
            return 0

    def setCode(self, code):
         if self.validateCodeSyntax(code):
             self.__employeeCode = code
             return 1
         else:
             return 0

        
    def setAuthorisation(self, authorisation):
        if self.validateAuthorisationSyntax(authorisation):
            self.__authorisationLevel = authorisation
            return 1
        else:
            return 0
        
    def setBaseRestaurant(self, base):
        if self.validateBaseRestaurantSyntax(base):
            self.__baseRestaurant = base
            return 1
        else:
            return 0

    def checkPassword(self, tempPassword):
        return sha256_crypt.verify(tempPassword, self.getPassword())

    #updaters
    def updatePassword(self, code, pw):
        conn, cur = openConnection()
        if self.validateUserpasswordSyntax(pw):
            query = 'UPDATE users SET password = ? WHERE employeeCode = ?;'
            cur.execute(query, (pw, code))
            conn.commit()
            conn.close()
            return 1
        else:
            conn.close()
            return 0

    def updateCode(self, code, newCode):
        conn, cur = openConnection()
        if self.validateCodeSyntax(newCode):
            query1 = "SELECT * FROM users WHERE employeeCode = ?;"
            cur.execute(query1, (newCode, ))
            record = cur.fetchone()
            if record is not None:
                print("Employee code already exists")
                conn.close()
                return 0
            else:
                query2 = "UPDATE users SET employeeCode = ? WHERE employeeCode = ?;"
                cur.execute(query2, (newCode, code))
                conn.commit()
                conn.close()
                return 1
        else:
            conn.close()
            return 0

    def updateAuthorisation(self, code, auth):
        conn, cur = openConnection()
        if self.validateAuthorisationSyntax(auth):
            query = "UPDATE users SET authorisationLevel = ? WHERE employeeCode = ?;"
            cur.execute(query, (auth, code))
            conn.commit()
            conn.close()
            return 1
        else:
            conn.close()
            return 0

    def updateBaseRestaurant(self, code, base):
        conn, cur = openConnection()
        if self.validateBaseRestaurantSyntax(base):
            query = "UPDATE users SET baseRestaurant = ? WHERE employeeCode = ?;"
            cur.execute(query, (base, code))
            conn.commit()
            conn.close()
            return 1
        else:
            conn.close()
            return 0
        

    #validators
    def validateCodeSyntax(self, code):
        if len(code) > 0:
            pattern = r'[A-Za-z0-9]{2,}'
            if re.fullmatch(pattern, code):
                return 1
            else:
                flash("Invalid employee code syntax", "danger")
                return 0
        else:
            flash("Invalid employee code syntax", "danger")
            return 0
        
    def validateAuthorisationSyntax(self, code):
        if code not in ["staff", "chef", "manager", "admin"]:
            return 0
        else:
            return 1
        
    def validateBaseRestaurantSyntax(self, base):
        conn, cur = openConnection()
        query = 'SELECT restaurantID FROM restaurant WHERE restaurantID = ?;'
        cur.execute(query, (base,))
        record = cur.fetchone()
        if record is not None:
            print("restaurant exists - baseRestaurant validation")
            conn.close()
            return 1
        else:
            print("restaurant does not exist")
            conn.close()
            return 0

    def validateUserpasswordSyntax(self, pw):
        if isinstance(pw, int):
            return 0
        elif isinstance(pw, str) and len(pw) > 0:
            pattern = r'[A-Za-z0-9 ]{6,}' 
            if re.fullmatch(pattern, pw):
                return 1
            else:
                flash("Invalid password syntax", "danger")
                return 0
        else:
            flash("Invalid password syntax", "danger")
            return 0

    
    # Checks whether the usercode and password exist. Returns true if it exists
    def checkCodePassword(self, code, pw): #check if code and password exist 
        conn, cur = openConnection()
        query = 'SELECT password, authorisationLevel, baseRestaurant FROM users WHERE employeeCode = ?;' #checks that username and password match
        cur.execute(query, (code,))
        records = cur.fetchone()
        
        if records is not None:
            print('Record exists')

            if sha256_crypt.verify(pw, records[0]):
                conn.close()
                return 1    # correct username and password
            else:
                flash("Incorrect password. Please try again", "danger")
                conn.close()
                return 0  # incorrect password

        else:
            print('Record does not exist')
            flash("Account does not exist", "danger")
            conn.close()
            return 0    #record does not exist

    def checkEmployeeCode(self, code):
        conn, cur = openConnection()
        query = "SELECT employeeCode FROM users WHERE employeeCode = ?;"
        cur.execute(query, (code,))
        records = cur.fetchone()
        if records is not None:
            print("Account already exists")
            conn.close()
            return 1
        else:
            print("Account doesn't exist")
            conn.close()
            return 0 
        
    # Saves the users details in the database
    def saveUserDetails(self, code, pw, al, br): #save user attributes in database - only admins can do this
        conn, cur = openConnection()
        if self.checkEmployeeCode(code):  
            print('Employee Code or Password already exists or syntax error')
            flash("Employee Code already exists", "danger")
            conn.close()
            return 0
        else:
            query = 'INSERT INTO users (employeeCode, password, authorisationLevel, baseRestaurant) VALUES (? , ?,  ?,  ?);'
            cur.execute(query, (code, sha256_crypt.hash(pw), al, br))
            print('Account details successfully saved')
            conn.commit()
            conn.close()
            return 1
        
    def deleteUser(self, code):
        conn, cur = openConnection()
        if self.checkEmployeeCode(code):
            query = 'DELETE FROM users WHERE employeeCode = ?;'

            cur.execute(query, (code,))

            print("Account successfully deleted")
            conn.commit()
            conn.close()
            return 1
        else:
            print("Account doesn't exist or invalid syntax")
            conn.close()
            return 0
    
    def setLoginDetails(self, code, pw):
        conn, cur = openConnection()
        query = "SELECT authorisationLevel, baseRestaurant FROM users WHERE employeeCode = ?;"
        cur.execute(query, (code,))
        record = cur.fetchone()
        self.setCode(code)
        self.setPassword(pw)
        self.setAuthorisation(record[0])
        print(record[0])
        self.setBaseRestaurant(record[1])
        conn.close()

    def getAuthorisationLevels(self):
        conn, cur = openConnection()
        query = "SELECT authorisationLevel FROM users;"
        cur.execute(query)
        record = cur.fetchall()
        conn.close()
        return record
    
    def getBaseRestaurants(self):
        conn, cur = openConnection()
        query = "SELECT baseRestaurant FROM users;"
        cur.execute(query)
        record = cur.fetchall()
        conn.close()
        return record
    
    def getEmployeeCodes(self):
        conn, cur = openConnection()
        query = "SELECT employeeCode FROM users;"
        cur.execute(query)
        record = cur.fetchall()
        conn.close()
        return record
    
    def getSpecificBaseRestaurant(self, code):
        conn, cur = openConnection()
        query = "SELECT baseRestaurant FROM users WHERE employeeCode = ?;"
        cur.execute(query, (code,))
        record = cur.fetchone()
        conn.close()
        return record
    
    def getSpecificAuthorisationLevel(self, code):
        conn, cur = openConnection()
        query = "SELECT baseRestaurant FROM users WHERE employeeCode = ?;"
        cur.execute(query, (code,))
        record = cur.fetchone()
        conn.close()
        return record
    
        

    def __str__(self):
        print("Employee Code: " + self.getCode() + " Password: " + self.getPassword() + "Authorisation Level:" + self.getAuthorisation() + "Base Restaurant:" + self.getBaseRestaurant())
        
    #start of discount model
    def create_discount(self, discount_value):
        try:
            conn, cur = openConnection()
            cur = conn.cursor()
            if self.check_discount_value(discount_value):
                    cur.execute("INSERT INTO discounts (discountValue) VALUES (?)", (discount_value,))
                    conn.commit()
                    conn.close()
                    return 1
            else:
                    conn.close()
                    return 0
        except sqlite3.Error as e:
            print("Error creating discount:", e)

    def delete_discount(self, discount_id):
        try:
            conn, cur = openConnection()
            cur = conn.cursor()
    
            cur.execute("DELETE FROM discounts WHERE discountID = ?", (discount_id,))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print("Error deleting discount:", e)

    def get_discounts(self):
        try:
            conn, cur = openConnection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM discounts")
            rows = cur.fetchall()
            discounts = [(row[0], row[1]) for row in rows]
            conn.close()
            return discounts
        except sqlite3.Error as e:
            print("Error fetching discounts:", e)
            return []

    def change_discount(self, discount_id, new_value):
        try:
            conn, cur = openConnection()
            cur = conn.cursor()
            if self.check_discount_value(new_value):
                cur.execute("UPDATE discounts SET discountValue = ? WHERE discountID = ?", (new_value, discount_id))
                conn.commit()
                conn.close()
                return 1
            else:
                conn.close()
                return 0
        except sqlite3.Error as e:
            print("Error updating discount:", e)
            
    def check_discount_value(self,value):
        conn, cur = openConnection()
        cur = conn.cursor()
        query='SELECT * FROM discounts WHERE discountValue = ?;'
        cur.execute(query, (value,))

        result = cur.fetchall()
        if len(result)>0:
            print("Discount exists")
            conn.close()
            return 0
        else:
            print("Discount does not exist")
            conn.close()
            return 1

    def validate_discount_value(self, discount_value):
        pattern = r'^(?:[1-9][0-9]?|100)$'
        if re.match(pattern, str(discount_value)):
            return  # Value matches the pattern, so it's within the accepted range
        else:
            raise ValueError('Discount value should be between 1 and 100')
    #end of discount model
    #start of food model
    def validatePrice(self,price):
        try:
            # Convert price to float and handle potential exceptions for invalid input
            price_float = float(price)
            if price_float > 0:
                return True  # Valid float value greater than 0
            else:
                print("Price should be greater than 0")
                return False
        except ValueError:
            print("Invalid price format")
            return False
        
    def validateName(self, name):
        if len(name)>0:
            pattern = r'[A-Za-z]{5,}'
            if re.fullmatch(pattern, name):
                return 1
            else:
                print("Invalid Syntax of Name")
                return 0
        else:
            print("Invalid Syntax of Name")
            return 0

    def validateAllergyInfo(self, allergyInfo):
        if len(allergyInfo)>0:
            pattern = r'[A-Za-z]{5,}'
            if re.fullmatch(pattern, allergyInfo):
                return 1
            else:
                print("Invalid Syntax of Allergy")
                return 0
        else:
            print("Invalid Syntax of Allergy")
            return 0

    def checkFoodName(self, name):
        conn, cur = openConnection()
        query = "SELECT name FROM food WHERE name = ?;"
        cur.execute(query, (name,))
        records = cur.fetchone()
        if records is not None:  # Check if records is not None
            print("Food already exists")
            conn.close()
            return 0
        else:
            conn.close()
            return 1

        
    def updateFood(self, price, name, allergyInfo, foodID):
        isAvailable = True 

        conn, cur = openConnection()
        if (self.checkFoodName(name)) and (self.validatePrice(price)) and (self.validateName(name)) and (self.validateAllergyInfo(allergyInfo)):
            query = 'UPDATE food SET price = ?, isAvailable = ?, name = ?, allergyInfo = ? WHERE foodID = ?;'
            cur.execute(query, (price, isAvailable, name, allergyInfo, foodID))
            conn.commit()
            print("Updated food")
            conn.close()
            return 1
        else:
            print("Food does not exist or invalid syntax")
            conn.close()
            return 0

        
    def createFood(self, price, name, allergyInfo):
        conn, cur = openConnection()
        if (self.validatePrice(price)) and (self.validateName(name)) and (self.validateAllergyInfo(allergyInfo)):
            query = 'INSERT INTO food (price, name, isAvailable, allergyInfo) VALUES (? , ?, ?, ?);'
            cur.execute(query, (price, name, True, allergyInfo))
            conn.commit()
            print("new food created")
            conn.close()
            return 1
        else:
            print("Syntax error")
            return 0
    def get_food_list(self):
        try:
            conn, cur = openConnection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM food")
            rows = cur.fetchall()
            food_list = [(row[0], row[1], row[2], row[3], row[4]) for row in rows]
            conn.close()
            return food_list
        except sqlite3.Error as e:
            print("Error fetching food list:", e)
            return []
    def delete_food(self, food_id):
        try:
            conn, cur = openConnection()
            cur.execute("DELETE FROM food WHERE foodID = ?", (food_id,))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print("Error deleting food:", e)
            


    def get_restaurants(self):
        try:
            conn, cur = openConnection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM restaurant")
            rows = cur.fetchall()
            restaurants = [(row[0], row[1], row[2]) for row in rows]
            # Close the connection after fetching data
            conn.close()
            return restaurants
        except sqlite3.Error as e:
            print("Error fetching restaurants:", e)
            return []
        
    def get_food_list(self):
        try:
            conn, cur = openConnection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM food")
            rows = cur.fetchall()
            food_list = [(row[0], row[1], row[2], row[3], row[4]) for row in rows]
            conn.close()
            return food_list
        except sqlite3.Error as e:
            print("Error fetching food list:", e)
            return []
        
    def get_orders_list(self, restaurant_id):
        try:
            conn, cur = openConnection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM orders WHERE restaurantID = ?", (restaurant_id,))
            rows = cur.fetchall()
            orders_list = [
                (row[0], row[1], row[2], row[3], row[4], row[5], row[6]) for row in rows
            ]
            conn.close()
            return orders_list
        except sqlite3.Error as e:
            print("Error fetching orders list by restaurant ID:", e)
            return []
        
    ###### Report Function
        
    # HR can choose which restaurant or restaurants they want to see the sales of or they can see all of the the restaurants
    # Managers can only see the sales of their own restaurants
    def sales(self, startDate, endDate, restaurantName = None):
        conn, cur = openConnection()

        if restaurantName == None:
            query = """SELECT sum(orderPrice), restaurantName 
                    FROM orders JOIN restaurant on orders.restaurantID = restaurant.restaurantID 
                    WHERE orders.startTime BETWEEN (?) AND (?)
                    GROUP by orders.restaurantID;"""
            cur.execute(query, (startDate, endDate))

        elif type(restaurantName) == str:
            query = """SELECT sum(orderPrice), restaurantName 
                    FROM orders JOIN restaurant on orders.restaurantID = restaurant.restaurantID 
                    WHERE orders.startTime BETWEEN (?) AND (?) AND restaurant.restaurantName = (?)
                    GROUP by orders.restaurantID;"""
            cur.execute(query, (startDate, endDate, restaurantName))

        else:
            values = [startDate, endDate, restaurantName[0]]

            query = """SELECT sum(orderPrice), restaurantName 
                    FROM orders JOIN restaurant on orders.restaurantID = restaurant.restaurantID 
                    WHERE orders.startTime BETWEEN (?) AND (?) AND (restaurant.restaurantName = (?)"""
            
            for name in range(1, len(restaurantName)):
                query += " OR restaurant.restaurantName = (?)"
                values.append(restaurantName[name])

            query += """) GROUP by orders.restaurantID;"""

            cur.execute(query, tuple(values))

        

        records = cur.fetchall()
        conn.close()

        return records
    
    # HR can choose which restaurant they want to see the averageSales of or they can see all of the the restaurants
    # Managers can only see the averageSales of their own restaurants
    def averageSales(self, startDate, endDate, restaurantName = None):
        conn, cur = openConnection()

        if restaurantName == None:
            query = """SELECT avg(orderPrice), restaurantName 
                    FROM orders JOIN restaurant on orders.restaurantID = restaurant.restaurantID 
                    WHERE orders.startTime BETWEEN (?) AND (?)
                    GROUP by orders.restaurantID;"""
            cur.execute(query, (startDate, endDate))

        elif type(restaurantName) == str:
            query = """SELECT avg(orderPrice), restaurantName 
                    FROM orders JOIN restaurant on orders.restaurantID = restaurant.restaurantID 
                    WHERE orders.startTime BETWEEN (?) AND (?) AND restaurant.restaurantName = (?)
                    GROUP by orders.restaurantID;"""
            cur.execute(query, (startDate, endDate, restaurantName))

        else:
            values = [startDate, endDate, restaurantName[0]]

            query = """SELECT avg(orderPrice), restaurantName 
                    FROM orders JOIN restaurant on orders.restaurantID = restaurant.restaurantID 
                    WHERE orders.startTime BETWEEN (?) AND (?) AND (restaurant.restaurantName = (?)"""
            
            for name in range(1, len(restaurantName)):
                query += " OR restaurant.restaurantName = (?)"
                values.append(restaurantName[name])

            query += """) GROUP by orders.restaurantID;"""

            cur.execute(query, tuple(values))
            

        

        records = cur.fetchall()
        conn.close()

        return records