from Model.Database import *
import re

class Inventory: #inventory class

    def __init__(self):
        self.__ID = ""
        self.__restaurantName = ""
        self.__itemName = ""

    def setInventoryDetails(self, id):
         conn, cur = openConnection()
         query = "SELECT * FROM inventory WHERE inventoryID = ?;"
         cur.execute(query,(id,))
         record = cur.fetchone()
         restaurantName = record[1]
         itemName = record[2]
         self.setrestaurantName(restaurantName)
         self.setID(id)
         self.setitemName(itemName)
         conn.close()


    #setters  
    def setrestaurantName(self, restaurantName):
        if self.validateRestaurantName(restaurantName):
            self.__restaurantName = restaurantName
            return 1
        else:
            return 0

    def setID(self, id):
        self.__ID = id
        
    def setItemName(self, itemName):
        if self.validateItemName(itemName):
            self.__itemName = itemName
            return 1
        else:
            return 0
    
    #getters
    def getrestaurantName(self):
        return self.__restaurantName
    
    def getID(self):
        return self.__ID
    
    def getItemName(self):
        return self.__itemName

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

    def validateItemName(self, itemName):
        conn, cur = openConnection()
        query = 'SELECT itemName FROM item WHERE itemName = ?;'
        cur.execute(query, (itemName,))
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
        query = 'SELECT * FROM inventory WHERE inventoryID = ?;'
        cur.execute(query, (ID,))
        record = cur.fetchone()
        if record is not None:
            
            print("Inventory exists")
            conn.close()  # Close the connection
            return 1
        else:
            print("Inventory does not exist")
            conn.close()  # Close the connection
            return 0
        
    def checkRestaurantItem(self, restaurantName, itemName):
        conn, cur = openConnection()
        query = 'SELECT * FROM inventory WHERE restaurantName = ? AND itemName = ?;'
        cur.execute(query, (restaurantName, itemName))
        record = cur.fethcone()
        if record is not None:
            print("Restaurant and item combination exists")
            conn.close()
            return 1
        else:
            print("Restaurant and item combination don't exist")
            conn.close()
            return 0
            
    def updateRestaurantName(self, restaurantName, id):
        if restaurantName != None:
            if self.checkID(id):
                if self.validateRestaurantName(restaurantName):
                    if not self.checkRestaurantItem(restaurantName, self.__itemName):
                        conn, cur = openConnection()
                        query = 'UPDATE inventory SET restaurantName = ? WHERE inventoryID = ?;'
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
        
            
    def updateItemName(self, itemName, id):
        if itemName != None:
            if self.checkID(id):
                if self.validateItemName(itemName):
                    if not self.checkRestaurantItem(self.__restaurantName, itemName):
                        conn, cur = openConnection()
                        query = 'UPDATE inventory SET itemName = ? WHERE inventoryID = ?;'
                        cur.execute(query, (itemName, id))
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

        
    def createInventory(self, restaurantName, itemName):
        conn, cur = openConnection()
        if (self.validateRestaurantName(restaurantName)) and (self.validateItemName(itemName)) and not (self.checkRestaurantItem(restaurantName, itemName)):
            query = 'INSERT INTO inventory (restaurantName, itemName) VALUES (?,?);'
            cur.execute(query, (restaurantName, itemName))
            conn.commit()
            print("new inventory created")
            conn.close()
            return 1
        else:
            return 0
        
    def getRestaurantNames(self, restaurantName):
        conn, cur = openConnection()
        query = 'SELECT restaurantName FROM inventory WHERE restaurantName = ? ORDER BY inventoryID;'
        conn.execute(query, (restaurantName,))
        record = cur.fetchall()
        conn.close()
        return record
    
    def getItemNames(self, itemName):
        conn, cur = openConnection()
        query = 'SELECT itemName FROM inventory WHERE itemName = ? ORDER BY inventoryID;'
        conn.execute(query, (itemName,))
        record = cur.fetchall()
        conn.close()
        return record
        
    def delete_inventory(self, id):
        try:
            conn, cur = openConnection()
            if self.checkID(id):
                query = "DELETE FROM inventory WHERE inventoryID = ?;"
                cur.execute(query, (id,))
                conn.commit()
                conn.close()
                return 1
            else:
                print("Inventory doesn't exists or invalid syntax")
                conn.close()
                return 0
        except sqlite3.Error as e:
            print("Error deleting inventory:", e)
