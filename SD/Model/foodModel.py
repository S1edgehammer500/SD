from Model.Database import *
import re

class Food: #food class

    def __init__(self):
        self.__price = ""
        self.__name = ""
        self.__allergyInfo = ""

    def setFoodDetails(self, name):
         conn, cur = openConnection()
         query = "SELECT * FROM food WHERE foodName = ?;"
         cur.execute(query,(name,))
         record = cur.fetchone()
         price = record[1]
         allergyInfo = record[2]
         self.setPrice(price)
         self.setName(name)
         self.setAllergyInfo(allergyInfo)
         conn.close()


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
    
    def getAllergyInfo(self):
        return self.__allergyInfo

    #validators
        
    def validateName(self, name):
        if len(name)>0:
            pattern = r'[A-Za-z]{3,}'
            if re.fullmatch(pattern, name):
                return 1
            else:
                print("Invalid Name Syntax")
                return 0
        else:
            print("Name length too small")
            return 0

    def validateAllergyInfo(self, allergyInfo):
        if allergyInfo is not None and len(allergyInfo) > 0:
            pattern = r'[A-Za-z\s]{3,}'
            if re.fullmatch(pattern, allergyInfo):
                return 1
            else:
                print("Invalid allergy Syntax")
                return 0
        else:
            print("allergy Info too small")
            return 0

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
        


    def checkName(self, foodName):
        conn, cur = openConnection()
        query = "SELECT * FROM food WHERE foodName = ?;"
        cur.execute(query, (foodName,))
        records = cur.fetchone()
        if records is not None:  # Check if records is not None
            print("Food already exists in this restaurant")
            conn.close()
            return 1
        else:
            conn.close()
            return 0
        
    def updateFoodName(self, previousName, currentName):
        if previousName != None and currentName != None:
            if self.validateName(currentName):
                if self.checkName(previousName):
                    if not self.checkName(currentName):
                        conn, cur = openConnection()
                        query = 'UPDATE food SET foodName = ? WHERE foodName = ?;'
                        cur.execute(query, (currentName, previousName))
                        conn.commit()
                        conn.close()
                        return 1
                    else:
                        return 0
                else:
                    return 0
            else:
                return 0
        else:
            return 0
            
    def updatePrice(self, price, foodName):
        if price != None:
            if self.validatePrice(price):
                if self.checkName(foodName):
                    conn, cur = openConnection()
                    query = 'UPDATE food SET price = ? WHERE foodName = ?;'
                    cur.execute(query, (price, foodName))
                    conn.commit()
                    conn.close()
                    return 1
                else:
                    return 0
            else:
                return 0
        else:
            return 0
        
        
    def updateAllergyInfo(self, allergyInfo, foodName):
        if allergyInfo != None:
            if self.validateAllergyInfo(allergyInfo):
                if self.checkName(foodName):
                    conn, cur = openConnection()
                    query = 'UPDATE food SET allergyInfo = ? WHERE foodName = ?;'
                    cur.execute(query, (allergyInfo, foodName))
                    conn.commit()
                    conn.close()
                    return 1
                else:
                    return 0
            else:
                return 0
        else:
            return 0
        

        
    def createFood(self, name, price, allergyInfo):
        conn, cur = openConnection()
        if not self.checkName(name):
            if (self.validatePrice(price)) and (self.validateName(name)) and (self.validateAllergyInfo(allergyInfo)):
                query = 'INSERT INTO food (foodName, price, allergyInfo) VALUES (?,?,?);'
                cur.execute(query, (name, price, allergyInfo))
                conn.commit()
                print("new food created")
                conn.close()
                return 1
            else:
                return 0
        else:
            print("Syntax error")
            return 0
        
    def get_food_list(self):
        try:
            conn, cur = openConnection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM food")
            rows = cur.fetchall()
            food_list = [(row[0], row[1], row[2]) for row in rows]
            conn.close()
            return food_list
        except sqlite3.Error as e:
            print("Error fetching food list:", e)
            return []
        
    def delete_food(self, foodName):
        try:
            conn, cur = openConnection()
            if self.checkName(foodName):
                query = "DELETE FROM food WHERE foodName = ?;"
                cur.execute(query, (foodName,))
                conn.commit()
                conn.close()
                return 1
            else:
                print("Food doesn't exists or invalid syntax")
                conn.close()
                return 0
        except sqlite3.Error as e:
            print("Error deleting food:", e)
