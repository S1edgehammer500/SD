from Model.Database import *
import re

class Food: #food class

    def __init__(self):
        self.__price = ""
        self.__name = ""
        self.__isAvailable = ""
        self.__allergyInfo = ""

    def setFoodDetails(self, name):
         conn, cur = openConnection()
         query = "SELECT * FROM food WHERE name = ?;"
         cur.execute(query,(id,))
         record = cur.fetchone()
         price = record[1]
         name = record[2]
         isAvailable = record[3]
         allergyInfo = record[4]
         food = Food()
         food.setPrice(price)
         food.setName(name)
         food.setIsAvailable(isAvailable)
         food.setAllergyInfo(allergyInfo)
         conn.close()
         return food


    #setters  
    def setPrice(self, price):
        if self.validatePrice(price):
            self.__price = price
            return 1
        else:
            return 0

    def setName(self, name):
        if self.validateName(name):
            self.__name = name
            return 1
        else:
            return 0
        
    def setIsAvailable(self, isAvailable):
        if self.validateAvailability(isAvailable):
            self.__isAvailable = isAvailable
            return 1
        else:
            return 0

    def setAllergyInfo(self, allergyInfo):
        if self.validateAllergyInfo(allergyInfo):
            self.__allergyInfo = allergyInfo
            return 1
        else:
            return 0
    
    #getters
    def getPrice(self):
        return self.__price
    
    def getName(self):
        return self.__name
    
    def getIsAvailable(self):
        return self.__isAvailable
    
    def getAllergyInfo(self):
        return self.__allergyInfo

    #validators
        
    def validateName(self, name):
        if len(name)>0:
            pattern = r'[A-Za-z]{3,}'
            if re.fullmatch(pattern, name):
                return 1
            else:
                print("Invalid Syntax")
                return 0
        else:
            print("Invalid Syntax")
            return 0

    def validateAllergyInfo(self, allergyInfo):
        if allergyInfo is not None and len(allergyInfo) > 0:
            pattern = r'[A-Za-z]{3,}'
            if re.fullmatch(pattern, allergyInfo):
                return 1
            else:
                print("Invalid Syntax")
                return 0
        else:
            print("Invalid Syntax")
            return 0

    #start of food model
    def validatePrice(self,price):
        try:
            # Convert price to float and handle potential exceptions for invalid input
            price_float = float(price)
            if price_float > 0:
                return 1  # Valid float value greater than 0
            else:
                print("Price should be greater than 0")
                return 0
        except ValueError:
            print("Invalid price format")
            return 0

    def validateAvailability(self, availability):
        try:
            availability_int = int(availability)
            if availability_int == 0 or availability_int == 1:
                return 1
            else:
                return 0
        except ValueError:
            print("Invalid availability format")
            return 0
        


    def checkFoodName(self, foodName, restaurantName):
        conn, cur = openConnection()
        query = "SELECT name FROM food WHERE name = ?;"
        cur.execute(query, (name,))
        records = cur.fetchone()
        if records is not None:  # Check if records is not None
            print("Food already exists in this restaurant")
            conn.close()
            return 1
        else:
            conn.close()
            return 0

        
    def updateFood(self, foodID=None, price=None, availability=None ):
        isAvailable = True 
        if foodID != None:
            conn, cur = openConnection()
            if price != None:
                query = 'UPDATE food SET price = ? WHERE foodID = ?;'
                cur.execute(query, (price, foodID))
                conn.commit()
                conn.close()
                print("price updated")
                return 1
            if availability != None:
                query2 = 'UPDATE food SET isAvailable = ? WHERE foodID = ?;'
                cur.execute(query2, (availability, foodID))
                conn.commit()
                conn.close()
                print("availability updated")
                return 1
            else:
                return 0
        else:
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
    def delete_food(self, foodID):
        try:
            conn, cur = openConnection()
            if self.checkFoodID(foodID):
                cur.execute("DELETE FROM food WHERE foodID = ?", (foodID,))
                conn.commit()
                conn.close()
                return 1
            else:
                print("Food doesn't exists or invalid syntax")
                conn.close()
                return 0
        except sqlite3.Error as e:
            print("Error deleting food:", e)
