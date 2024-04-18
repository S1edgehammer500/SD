from Model.Database import *
import re

class Item: #item class

    def __init__(self):
        self.__name = ""
        self.__quantity = ""
        self.__stockLimit = ""

    def setItemDetails(self, name):
         conn, cur = openConnection()
         query = "SELECT * FROM item WHERE itemName = ?;"
         cur.execute(query,(name,))
         record = cur.fetchone()
         quantity = record[1]
         stockLimit = record[2]
         self.setName(name)
         self.setStockLimit(stockLimit)
         self.setQuantity(quantity)
         conn.close()


    #setters  
    def setQuantity(self, quantity):
        if self.validateQuantity(quantity):
            self.__quantity = quantity
            return 1
        else:
            return 0

    def setName(self, name):
        if self.validateName(name):
            self.__name = name
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
    def getQuantity(self):
        return self.__quantity
    
    def getName(self):
        return self.__name
    
    def getStockLimit(self):
        return self.__stockLimit

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

    def validateQuantity(self, quantity):
        if int(quantity)>0:
            pattern = r'[0-9]{1,4}' 
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
            print("Quantity is above stock limit")
            return 1

    def validateStockLimit(self, stockLimit):
        if int(stockLimit):
            pattern = r'[0-9]{1,4}'
            if re.fullmatch(pattern, str(stockLimit)):
                return 1
            else:
                print("Invalid Stock Syntax")
                return 0
        else:
            print("Invalid Stock Syntax")
            return 0
        
    def checkName(self, itemName):
        conn, cur = openConnection()
        query = "SELECT * FROM item WHERE itemName = ?;"
        cur.execute(query, (itemName,))
        records = cur.fetchone()
        if records is not None:  # Check if records is not None
            print("Item already exists")
            conn.close()
            return 1
        else:
            conn.close()
            return 0
        
    def updateItemName(self, previousName, currentName):
        if previousName != None and currentName != None:
            if self.validateName(currentName):
                if self.checkName(previousName):
                    if not self.checkName(currentName):
                        conn, cur = openConnection()
                        query = 'UPDATE item SET itemName = ? WHERE itemName = ?;'
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
            
    def updateQuantity(self, quantity, foodName):
        if quantity != None:
            stockLimit = self.getStockLimit()
            if self.validateQuantity(quantity) and self.validateQuantity2(quantity, stockLimit):
                if self.checkName(foodName):
                    conn, cur = openConnection()
                    query = 'UPDATE item SET quantity = ? WHERE itemName = ?;'
                    cur.execute(query, (quantity, foodName))
                    conn.commit()
                    conn.close()
                    return 1
                else:
                    return 0
            else:
                return 0
        else:
            return 0
        
            
    def updateStockLimit(self, stockLimit, foodName):
        if stockLimit != None:
            if self.validateStockLimit(stockLimit):
                if self.checkName(foodName):
                    conn, cur = openConnection()
                    query = 'UPDATE item SET stockLimit = ? WHERE itemName = ?;'
                    cur.execute(query, (stockLimit, foodName))
                    conn.commit()
                    conn.close()
                    return 1
                else:
                    return 0
            else:
                return 0
        else:
            return 0
        
    def createItem(self, name, quantity, stockLimit):
        conn, cur = openConnection()
        if not self.checkName(name):
            if (self.validateQuantity(quantity)) and (self.validateName(name)) and (self.validateStockLimit(stockLimit)) and (self.validateQuantity2(quantity, stockLimit)):
                query = 'INSERT INTO item (itemName, quantity, stockLimit) VALUES (?,?,?);'
                cur.execute(query, (name, quantity, stockLimit))
                conn.commit()
                print("new item created")
                conn.close()
                return 1
            else:
                return 0
        else:
            print("Syntax error")
            return 0
        
    def get_item_list(self):
        try:
            conn, cur = openConnection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM item")
            rows = cur.fetchall()
            item_list = [(row[0], row[1], row[2]) for row in rows]
            itemName = [row[0] for row in rows]
            quantity = [row[1] for row in rows]
            stockLimit = [row[2] for row in rows]
            conn.close()
            return itemName, quantity, stockLimit
        except sqlite3.Error as e:
            print("Error fetching item list:", e)
            return []
        
    def delete_item(self, itemName):
        try:
            conn, cur = openConnection()
            if self.checkName(itemName):
                query = "DELETE FROM item WHERE itemName = ?;"
                cur.execute(query, (itemName,))
                conn.commit()
                conn.close()
                return 1
            else:
                print("Item doesn't exists or invalid syntax")
                conn.close()
                return 0
        except sqlite3.Error as e:
            print("Error deleting item:", e)


    def isThereMoreItems(self, itemName, quantity):
        conn, cur = openConnection()
        query = "SELECT quantity FROM item WHERE itemName = ?;"
        cur.execute(query, (itemName,))
        record = cur.fetchone()
        conn.close()

        if record is not None:
            if record[0] >= quantity:
                return 1
            else:
                return 0 
        else:
            conn.close()
            return 0

    def takeAwayItems(self, quantity, itemName):
        if quantity != None:
            if self.getName(itemName):
                itemQuant = self.getQuantity(itemName)


                quantity = itemQuant - quantity

                conn, cur = openConnection()
                query = 'UPDATE item SET quantity = ? WHERE itemName = ?;'
                cur.execute(query, (quantity, itemName))
                conn.commit()
                conn.close()
                return 1
            else:
                return 0
        else:
            return 0
        
    def checkItemQuantLessThanStockLimit(self, itemSL, itemQuant, quantToAdd):
        if (quantToAdd + itemQuant) > itemSL:
            return 0
        else: return 1