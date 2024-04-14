from Model.Database import *
import re

class Inventory: #inventory class

    def __init__(self):
        self.__ID = ""
        self.__restaurantName = ""
        self.__itemName = ""
        self.__quantity = ""
        self.__stockLimit = ""

    def setInventoryDetails(self, id):
         conn, cur = openConnection()
         query = "SELECT * FROM inventory WHERE inventoryID = ?;"
         cur.execute(query,(id,))
         record = cur.fetchone()
         restaurantName = record[1]
         itemName = record[2]
         quantity = record[3]
         stockLimit = record[4]
         self.setRestaurantName(restaurantName)
         self.setID(id)
         self.setItemName(itemName)
         self.setQuantity(quantity)
         self.setStockLimit(stockLimit)
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
        
    def setItemName(self, itemName):
        if self.validateItemName(itemName):
            self.__itemName = itemName
            return 1
        else:
            return 0
    
    def setQuantity(self, quantity):
        if self.validateQuantity(quantity):
            self.__quantity = quantity
            return 1
        else:
            return 0
        
    def setStockLimit(self, stockLimit):
        if self.validateStockLimit(stockLimit):
            self.__stockLimit = stockLimit
            return 1
        else:
            return 0
    #getters
    def getRestaurantName(self):
        return self.__restaurantName
    
    def getID(self):
        return self.__ID
    
    def getItemName(self):
        return self.__itemName
    
    def getQuantity(self):
        return self.__quantity
    
    def getStockLimit(self):
        return self.__stockLimit

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
    
    def validateQuantity(self, quantity):
        if int(quantity)>0:
            pattern = r'[0-9]{1,2}' 
            if re.fullmatch(pattern, str(quantity)):
                return 1
            else:
                print("Incorrect Quantity syntax")
                return 0
        else:
            print("Incorrect Quantity Syntax")
            return 0
        
    def validateQuantity2(self, quantity, stockLimit):
        if int(quantity) > int(stockLimit):
            return 0
        else:
            print("Quantity is not above stock limit")
            return 1

    def validateStockLimit(self, stockLimit):
        if int(stockLimit):
            pattern = r'[0-9]{1,2}'
            if re.fullmatch(pattern, str(stockLimit)):
                return 1
            else:
                print("Invalid Stock Syntax")
                return 0
        else:
            print("Invalid Stock Syntax")
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
        record = cur.fetchone()
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

    def updateStockLimit(self, stockLimit, id):
        if stockLimit != None:
            if self.checkID(id):
                if self.validateStockLimit(stockLimit):
                    conn, cur = openConnection()
                    query = 'UPDATE inventory SET stockLimit = ? WHERE inventoryID = ?;'
                    cur.execute(query, (stockLimit, id))
                    conn.commit()
                    conn.close()
                    return 1
                else:
                    return 0
            else:
                return 0
        else:
            return 0
        
    def updateQuantity(self, quantity):
        if quantity != None:
            id = self.getID()
            if self.checkID(id):
                print(quantity)
                print(id)
                conn, cur = openConnection()
                query = 'UPDATE inventory SET quantity = ? WHERE inventoryID = ?;'
                cur.execute(query, (quantity, id))
                conn.commit()
                conn.close()
                return 1
            else:
                return 0
        else:
            return 0
        
    def createInventory(self, restaurantName, itemName, quantity, stockLimit):
        conn, cur = openConnection()
        if (self.validateRestaurantName(restaurantName)) and (self.validateItemName(itemName)) and not (self.checkRestaurantItem(restaurantName, itemName)) and (self.validateQuantity(quantity)) and (self.validateStockLimit(stockLimit)) and (self.validateQuantity2(quantity, stockLimit)):
            query = 'INSERT INTO inventory (restaurantName, itemName, quantity, stockLimit) VALUES (?,?,?,?);'
            cur.execute(query, (restaurantName, itemName, quantity, stockLimit))
            conn.commit()
            print("new inventory created")
            conn.close()
            return 1
        else:
            return 0
        
    def getRestaurantNames(self, restaurantName):
        conn, cur = openConnection()
        query = 'SELECT restaurantName FROM inventory WHERE restaurantName = ? ORDER BY inventoryID;'
        cur.execute(query, (restaurantName,))
        record = cur.fetchall()
        conn.close()
        return record
    
    def getItemNames(self, restaurantName):
        conn, cur = openConnection()
        query = 'SELECT itemName FROM inventory WHERE restaurantName = ? ORDER BY inventoryID;'
        cur.execute(query, (restaurantName,))
        record = cur.fetchall()
        conn.close()
        return record
    
    def getItemQuantity(self, restaurantName):
        conn, cur = openConnection()
        query = 'SELECT quantity FROM inventory WHERE restaurantName = ? ORDER BY inventoryID;'
        cur.execute(query, (restaurantName,))
        record = cur.fetchall()
        conn.close()
        return record
    
    def getItemStockLimit(self, restaurantName):
        conn, cur = openConnection()
        query = 'SELECT stockLimit FROM inventory WHERE restaurantName = ? ORDER BY inventoryID;'
        cur.execute(query, (restaurantName,))
        record = cur.fetchall()
        conn.close()
        return record
    
    def getInventoryList(self,restaurantName):
        conn, cur = openConnection()
        query = 'SELECT item.itemName, quantity, stockLimit FROM item JOIN inventory ON item.itemName == inventory.itemName WHERE inventory.restaurantName = ? ORDER BY inventory.inventoryID;'

        cur.execute(query, (restaurantName,))
        records = cur.fetchall()
        itemList = [row[0] for row in records]
        quantityList = [row[1] for row in records]
        stockLimitList = [row[2] for row in records]

        # Close the connection after fetching data
        conn.close()
        return itemList, quantityList, stockLimitList
    
    def getInventoryID(self, restaurantName):
        conn, cur = openConnection()
        query = 'SELECT inventoryID FROM inventory WHERE restaurantName = ? ORDER BY inventoryID;'
        cur.execute(query, (restaurantName,))
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


    def checkItemQuantLessThanStockLimit(self, itemSL, itemQuant, quantToAdd):
        if (quantToAdd + itemQuant) > itemSL:
            return 0
        else: return 1
