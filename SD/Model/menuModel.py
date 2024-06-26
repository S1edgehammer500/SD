from Model.Database import *
import re

class Menu: #menu class

    def __init__(self):
        self.__ID = ""
        self.__restaurantName = ""
        self.__foodName = ""
        self.__isAvailable = ""

    def setMenuDetails(self, id):
         conn, cur = openConnection()
         query = "SELECT * FROM menu WHERE menuID = ?;"
         cur.execute(query,(id,))
         record = cur.fetchone()
         restaurantName = record[1]
         foodName = record[2]
         isAvailable = record[3]
         self.setRestaurantName(restaurantName)
         self.setID(id)
         self.setFoodName(foodName)
         self.setIsAvailable(isAvailable)
         conn.close()


    #setters  
    def setRestaurantName(self, restaurantName):
        if self.validateRestaurantName(restaurantName):
            self.__restaurantName = restaurantName
            return 1
        else:
            return 0

    def setID(self, id):
        self.__ID = id
        
    def setFoodName(self, foodName):
        if self.validateFoodName(foodName):
            self.__foodName = foodName
            return 1
        else:
            return 0
        
    def setIsAvailable(self, isAvailable):
        if self.validateAvailability(isAvailable):
            self.__isAvailable = isAvailable
            return 1
        else:
            return 0
    
    #getters
    def getRestaurantName(self):
        return self.__restaurantName
    
    def getID(self):
        return self.__ID
    
    def getFoodName(self):
        return self.__foodName
    
    def getIsAvailable(self):
        return self.__isAvailable

    #validators

    def validateRestaurantName(self, restaurantName):
        conn, cur = openConnection()
        query = 'SELECT restaurantName FROM restaurant WHERE restaurantName = ?;'
        cur.execute(query, (restaurantName,))
        record = cur.fetchone()
        if record is not None:
            print("restaurant exists")
            conn.close()
            return 1
        else:
            print("Restaurant does not exist")
            conn.close()
            return 0

    def validateFoodName(self, foodName):
        conn, cur = openConnection()
        query = 'SELECT foodName FROM food WHERE foodName = ?;'
        cur.execute(query, (foodName,))
        record = cur.fetchone()
        if record is not None:
            print("Item exists")
            conn.close()
            return 1
        else:
            print("Food does not exist")
            conn.close()
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
        
    def checkID(self, ID):
        conn, cur = openConnection()
        query = 'SELECT * FROM menu WHERE menuID = ?;'
        cur.execute(query, (ID,))
        record = cur.fetchone()
        if record is not None:
            
            print("menu exists")
            conn.close()  # Close the connection
            return 1
        else:
            print("menu does not exist")
            conn.close()  # Close the connection
            return 0
        
    def checkRestaurantFood(self, restaurantName, foodName):
        conn, cur = openConnection()
        query = 'SELECT * FROM menu WHERE restaurantName = ? AND foodName = ?;'
        cur.execute(query, (restaurantName, foodName))
        record = cur.fetchone()
        if record is not None:
            print("Restaurant and food combination exists")
            conn.close()
            return 1
        else:
            print("Restaurant and food combination don't exist")
            conn.close()
            return 0
        
    def updateAvailability(self, availability, ID):
        if availability != None:
            if self.validateAvailability(availability):
                conn, cur = openConnection()
                query = 'UPDATE menu SET isAvailable = ? WHERE menuID = ?;'
                cur.execute(query, (availability, ID))
                conn.commit()
                conn.close()
                return 1
            else:
                return 0
        else:
            return 0

        
    def createMenu(self, restaurantName, foodName):
        conn, cur = openConnection()
        if (self.validateRestaurantName(restaurantName)) and (self.validateFoodName(foodName)) and not (self.checkRestaurantFood(restaurantName, foodName)):
            query = 'INSERT INTO menu (restaurantName, foodName, isAvailable) VALUES (?,?,?);'
            cur.execute(query, (restaurantName, foodName, True))
            conn.commit()
            print("new menu created")
            conn.close()
            return 1
        else:
            return 0
        
    def getRestaurantNames(self, restaurantName):
        conn, cur = openConnection()
        query = 'SELECT restaurantName FROM menu WHERE restaurantName = ? ORDER BY menuID;'
        cur.execute(query, (restaurantName,))
        record = cur.fetchall()
        conn.close()
        return record
    
    def getfoodNames(self, restaurantName):
        conn, cur = openConnection()
        query = 'SELECT foodName FROM menu WHERE restaurantName = ? ORDER BY menuID;'
        cur.execute(query, (restaurantName,))
        record = cur.fetchall()
        conn.close()
        return record
    
    def getMenuList(self,restaurantName):
        conn, cur = openConnection()
        query = 'SELECT food.foodName, price, allergyInfo, menu.menuID, isAvailable FROM food JOIN menu ON food.foodName == menu.foodName WHERE menu.restaurantName = ? ORDER BY menu.menuID;'

        cur.execute(query, (restaurantName,))
        records = cur.fetchall()
        foodList = [row[0] for row in records]
        priceList = [row[1] for row in records]
        allergyList = [row[2] for row in records]
        idList = [row[3] for row in records]
        isAvailableList = [row[4] for row in records]

        # Close the connection after fetching data
        conn.close()
        return foodList, priceList, allergyList, idList, isAvailableList
    
    def getAvailableMenuList(self,restaurantName):
        conn, cur = openConnection()
        query = 'SELECT food.foodName, price, allergyInfo, menu.menuID, isAvailable FROM food JOIN menu ON food.foodName == menu.foodName WHERE menu.restaurantName = ? AND menu.isAvailable=? ORDER BY menu.menuID;'

        cur.execute(query, (restaurantName,True))
        records = cur.fetchall()
        foodList = [row[0] for row in records]
        priceList = [row[1] for row in records]
        allergyList = [row[2] for row in records]
        idList = [row[3] for row in records]
        isAvailableList = [row[4] for row in records]
        
        # Close the connection after fetching data
        conn.close()
        return foodList, priceList, allergyList, idList, isAvailableList

        
    def delete_menu(self, id):
        try:
            conn, cur = openConnection()
            if self.checkID(id):
                query = "DELETE FROM menu WHERE menuID = ?;"
                cur.execute(query, (id,))
                conn.commit()
                conn.close()
                return 1
            else:
                print("menu doesn't exists or invalid syntax")
                conn.close()
                return 0
        except sqlite3.Error as e:
            print("Error deleting menu:", e)
