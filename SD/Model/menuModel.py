from Model.Database import *
import re

class Menu: #menu class

    def __init__(self):
        self.__ID = ""
        self.__restaurantName = ""
        self.__foodName = ""

    def setMenuDetails(self, id):
         conn, cur = openConnection()
         query = "SELECT * FROM menu WHERE menuID = ?;"
         cur.execute(query,(id,))
         record = cur.fetchone()
         restaurantName = record[1]
         foodName = record[2]
         self.setRestaurantName(restaurantName)
         self.setID(id)
         self.setFoodName(foodName)
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
    
    #getters
    def getRestaurantName(self):
        return self.__restaurantName
    
    def getID(self):
        return self.__ID
    
    def getFoodName(self):
        return self.__foodName

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
            print("Item does not exist")
            conn.close()
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
            
    def updateRestaurantName(self, restaurantName, id):
        if restaurantName != None:
            if self.checkID(id):
                if self.validateRestaurantName(restaurantName):
                    if not self.checkRestaurantFood(restaurantName, self.__foodName):
                        conn, cur = openConnection()
                        query = 'UPDATE menu SET restaurantName = ? WHERE menuID = ?;'
                        cur.execute(query, (restaurantName, id))
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
        
            
    def updateFoodName(self, foodName, id):
        if foodName != None:
            if self.checkID(id):
                if self.validateFoodName(foodName):
                    if not self.checkRestaurantFood(self.__restaurantName, foodName):
                        conn, cur = openConnection()
                        query = 'UPDATE menu SET foodName = ? WHERE menuID = ?;'
                        cur.execute(query, (foodName, id))
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

        
    def createMenu(self, restaurantName, foodName):
        conn, cur = openConnection()
        if (self.validateRestaurantName(restaurantName)) and (self.validateFoodName(foodName)) and not (self.checkRestaurantFood(restaurantName, foodName)):
            query = 'INSERT INTO menu (restaurantName, foodName) VALUES (?,?);'
            cur.execute(query, (restaurantName, foodName))
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
        query = 'SELECT food.foodName, price, allergyInfo FROM food JOIN menu ON food.foodName == menu.foodName WHERE menu.restaurantName = ? ORDER BY menu.menuID;'

        cur.execute(query, (restaurantName,))
        records = cur.fetchall()
        foodList = [row[0] for row in records]
        priceList = [row[1] for row in records]
        allergyList = [row[2] for row in records]

        # Close the connection after fetching data
        conn.close()
        return foodList, priceList, allergyList

        
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
