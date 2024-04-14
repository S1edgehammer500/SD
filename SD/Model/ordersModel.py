from Model.Database import *
import re
import datetime

class Order: #menu class

    def __init__(self):
        self.__restaurantName = ""
        self.__ID = ""
        self.__status = ""
        self.__price = ""
        self.__table = ""
        self.__startTime = ""
        self.__readyTime = ""

    def setOrderDetails(self, id):
         conn, cur = openConnection()
         query = "SELECT * FROM orders WHERE orderID = ?;"
         cur.execute(query,(id,))
         record = cur.fetchone()
         restaurantName = record[0]
         status = record[2]
         price = record[3]
         tableNumber = record[4]
         startTime = record[5]
         readyTime = record[6]
         self.setRestaurantName(restaurantName)
         self.setID(id)
         self.setStatus(status)
         self.setPrice(price)
         self.setTableNumber(tableNumber)
         self.setStartTime(startTime)
         self.setReadyTime(readyTime)
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
        
    def setStatus(self, status):
        if self.validateStatus(status):
            self.__status = status
            return 1
        else:
            return 0
        
    def setPrice(self, price):
        if self.validatePrice(price):
            self.__price = price
            return 1
        else:
            return 0
        
    def setTableNumber(self, tableNumber):
        if self.validateTableNumber(tableNumber):
            self.__table = tableNumber
            return 1
        else:
            return 0
        
    def setStartTime(self, startTime):
        if self.validateStartTime(startTime):
            self.__startTime = startTime
            return 1
        else:
            return 0
        
    def setReadyTime(self, readyTime):
        if self.validateReadyTime(readyTime):
            self.__readyTime = readyTime
            return 1
        else:
            return 0
    
    
    #getters
    def getRestaurantName(self):
        return self.__restaurantName
    
    def getID(self):
        return self.__ID
    
    def getStatus(self):
        return self.__status
    
    def getPrice(self):
        return self.__price
    
    def getTableNumber(self):
        return self.__table
    
    def getStartTime(self):
        return self.__startTime
    
    def getReadyTime(self):
        return self.__readyTime

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

    def validateStatus(self, status):
        if status not in ['Order Created','Cooking', 'Ready', 'Delivered', 'Payment Completed','Cancelled']:
            return 0
        else:
            return 1
        
    def validatePrice(self,price):
        try:
            # Convert price to float and handle potential exceptions for invalid input
            price_float = float(price)
            if 0 <= price_float:
                return 1  # Valid float value greater than 0
            else:
                print("Price should be greater than 0")
                return 0
        except ValueError:
            print("Invalid price format")
            return 0
        
    def validateTableNumber(self, tableNumber, restaurantName):
        if not isinstance(tableNumber, int):
            return 0  # Returning error message for non-integer input

        if 1 <= tableNumber <= 99:  # Checking if tableNumber is within the range
            conn, cur = openConnection()
            query2 = "SELECT numberOfTables FROM restaurant WHERE restaurantName = ?;"
            cur.execute(query2, (restaurantName,))
            record2 = cur.fetchone()

            if record2 is not None and tableNumber <= record2[0]:
                conn.close()
                return 1  # Valid table number within the restaurant's table count
            else:
                conn.close()
                return 0  # Indicates invalid table number or table number too large
        else:
            return 0  # Indicates table number out of range
        
    def validateStartTime(self, startTime):
        try:
            if startTime != None:
                startTime = datetime.datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")
                now = datetime.datetime.now()-datetime.timedelta(minutes=10)
                if startTime < now:
                    print("Time out of range")
                    return 0
                else:
                    return 1
            else:
                return 1
        except ValueError:
            return 0
    
    def validateReadyTime(self, readyTime):
        try:
            if readyTime != None:
                ready_time = datetime.datetime.strptime(readyTime, "%Y-%m-%d %H:%M:%S")
                now = datetime.datetime.now() - datetime.timedelta(minutes=10)

                if ready_time < now:
                    print("Time out of range")
                    return 0
                else:
                    return 1
            else:
                return 1
        except ValueError:
            return 0  # Return 0 if unable to convert input to datetime
        
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
        query = 'SELECT * FROM orders WHERE orderID = ?;'
        cur.execute(query, (ID,))
        record = cur.fetchone()
        if record is not None:
            print("order exists")
            conn.close()  # Close the connection
            return 1
        else:
            print("order does not exist")
            conn.close()  # Close the connection
            return 0
        
    def checkDiscountID(self, ID):
        conn, cur = openConnection()
        query = 'SELECT * FROM discounts WHERE discountID = ?;'
        cur.execute(query, (ID,))
        record = cur.fetchone()
        if record is not None:
            print("discount exists")
            conn.close()  # Close the connection
            return 1
        else:
            print("discount does not exist")
            conn.close()  # Close the connection
            return 0
        
    def checkFoodListID(self, ID):
        conn, cur = openConnection()
        query = 'SELECT * FROM foodList WHERE foodListID = ?;'
        cur.execute(query, (ID,))
        record = cur.fetchone()
        if record is not None:
            print("foodList exists")
            conn.close()  # Close the connection
            return 1
        else:
            print("foodList does not exist")
            conn.close()  # Close the connection
            return 0
        
    def checkDiscountListID(self, ID):
        conn, cur = openConnection()
        query = 'SELECT * FROM discountList WHERE discountListID = ?;'
        cur.execute(query, (ID,))
        record = cur.fetchone()
        if record is not None:
            print("discount list exists")
            conn.close()  # Close the connection
            return 1
        else:
            print("discount list does not exist")
            conn.close()  # Close the connection
            return 0
        
    def checkFoodInOrder(self, orderID, foodName):
        conn, cur = openConnection()
        query = 'SELECT * FROM foodList WHERE orderID = ? AND foodName = ?;'
        cur.execute(query, (orderID, foodName))
        record = cur.fetchone()
        if record is not None:
            print("Food is in order")
            conn.close()
            return 1
        else:
            print("Food is not in order")
            conn.close()
            return 0
        
    def checkDiscountInOrder(self, orderID, discountID):
        conn, cur = openConnection()
        query = 'SELECT * FROM discountList WHERE orderID = ? AND discountID = ?;'
        cur.execute(query, (orderID, discountID))
        record = cur.fetchone()
        if record is not None:
            print("Discount is in order")
            conn.close()
            return 1
        else:
            print("Discount is not in order")
            conn.close()
            return 0

    def updateRestaurantName(self, restaurantName, id):
        if restaurantName != None:
            if self.checkID(id):
                if self.validateRestaurantName(restaurantName):
                    conn, cur = openConnection()
                    query = 'UPDATE orders SET restaurantName = ? WHERE orderID = ?;'
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
        
    def updateStatus(self, status, id):
        if status != None:
            if self.checkID(id):
                if self.validateStatus(status):
                    conn, cur = openConnection()
                    query = 'UPDATE orders SET status = ? WHERE orderID = ?;'
                    cur.execute(query, (status, id))
                    conn.commit()
                    conn.close()
                    return 1
                else:
                    return 0
            else:
                return 0
        else:
            return 0
        
    def updatePrice(self, price, id):
        if price != None:
            if self.checkID(id):
                if self.validatePrice(price):
                    conn, cur = openConnection()
                    query = 'UPDATE orders SET orderPrice = ? WHERE orderID = ?;'
                    cur.execute(query, (price, id))
                    conn.commit()
                    conn.close()
                    return 1
                else:
                    return 0
            else:
                return 0
        else:
            return 0
        
    def updateTable(self, table, id):
        if table != None:
            if self.checkID(id):
                if self.validateTableNumber(table):
                    conn, cur = openConnection()
                    query = 'UPDATE orders SET tableNumber = ? WHERE orderID = ?;'
                    cur.execute(query, (table, id))
                    conn.commit()
                    conn.close()
                    return 1
                else:
                    return 0
            else:
                return 0
        else:
            return 0
        
    def updateStartTime(self, startTime, id):
        if startTime != None:
            if self.checkID(id):
                if self.validateStartTime(startTime):
                    conn, cur = openConnection()
                    query = 'UPDATE orders SET startTime = ? WHERE orderID = ?;'
                    cur.execute(query, (startTime, id))
                    conn.commit()
                    conn.close()
                    return 1
                else:
                    return 0
            else:
                return 0
        else:
            return 1
        
    def updateReadyTime(self, readyTime, id):
        if readyTime != None:
            if self.checkID(id):
                if self.validateReadyTime(readyTime):
                    conn, cur = openConnection()
                    query = 'UPDATE orders SET readyTime = ? WHERE orderID = ?;'
                    cur.execute(query, (readyTime, id))
                    conn.commit()
                    conn.close()
                    return 1
                else:
                    return 0
            else:
                return 0
        else:
            return 1

        
    def createOrder(self, restaurantName, status, tableNumber, startTime, readyTime):
        conn, cur = openConnection()
        if (self.validateRestaurantName(restaurantName)) and (self.validateStatus(status)) and (self.validateTableNumber(tableNumber) and (self.validateStartTime(startTime) and (self.validateReadyTime(readyTime)))):
            query = 'INSERT INTO orders (restaurantName, status, price, tableNumber, startTime, readyTime) VALUES (?,?,?,?,?,?);'
            cur.execute(query, (restaurantName, status, 0, tableNumber, startTime, readyTime))
            conn.commit()
            print("new order created")
            conn.close()
            return 1
        else:
            return 0
        
    def addFoodToOrder(self, orderID, foodName):
        conn, cur = openConnection()
        if (self.validateFoodName(foodName) and self.checkID(orderID)):
            query = 'INSERT INTO foodList (orderID, foodName) VALUES (?,?);'
            cur.execute(query, (orderID, foodName))
            conn.commit()
            query2 = 'SELECT price FROM food WHERE foodName = ?;'
            cur.execute(query2, (foodName, ))
            foodPrice = cur.fetchone()
            print("RECORD IS!!!!!!!!!!!!!!!!!! " + str(foodPrice))
            query3 = 'SELECT price FROM orders WHERE orderID = ?;'
            cur.execute(query3, (orderID,))
            orderPrice = cur.fetchone()
            query4 = 'UPDATE orders SET price = ? WHERE orderID = ?;'
            newPrice = int(orderPrice)+int(foodPrice)
            cur.execute(query4, (newPrice, orderID))
            conn.commit()
            conn.close()
            return 1
        else:
            return 0
        
    def removeFoodFromOrder(self, orderID, foodName, foodListID):
        conn, cur = openConnection()
        if (self.validateFoodName(foodName) and self.checkID(orderID) and self.checkFoodListID(foodListID) and self.checkFoodInOrder(orderID, foodName)):
            query = 'SELECT price FROM food WHERE foodName = ?;'
            cur.execute(query, (foodName, ))
            foodPrice = cur.fetchone()
            query2 = 'SELECT price FROM orders WHERE orderID = ?;'
            cur.execute(query2, (orderID,))
            orderPrice = cur.fetchone()
            query3 = 'UPDATE orders SET price = ? WHERE orderID = ?;'
            newPrice = int(orderPrice) - int(foodPrice)
            cur.execute(query3, (newPrice, orderID))
            conn.commit()
            query4 = 'DELETE FROM foodList WHERE foodListID = ?;'
            cur.execute(query4, (foodListID,))
            conn.commit()
            conn.close()
            return 1
        else:
            return 0
        
    def addDiscountToOrder(self, orderID, discountID):
        conn, cur = openConnection()
        if (self.checkDiscountID(discountID) and self.checkID(orderID)):
            query = 'INSERT INTO discountList (orderID, discountID) VALUES (?,?);'
            cur.execute(query, (orderID, discountID))
            conn.commit()
            query2 = 'SELECT discountValue FROM discounts WHERE discountID = ?;'
            cur.execute(query2, (discountID, ))
            discountValue = cur.fetchone()
            query3 = 'SELECT price FROM orders WHERE orderID = ?;'
            cur.execute(query3, (orderID,))
            orderPrice = cur.fetchone()
            query4 = 'UPDATE orders SET price = ? WHERE orderID = ?;'
            newPrice = int(orderPrice) * (1-(int(discountValue)/100))
            cur.execute(query4, (newPrice, orderID))
            conn.commit()
            conn.close()
            return 1
        else:
            return 0
        
    def removeDiscountFromOrder(self, orderID, discountID, discountListID):
        conn, cur = openConnection()
        if (self.checkDiscountID(discountID) and self.checkID(orderID) and self.checkDiscountListID(discountListID) and self.checkDiscountInOrder(orderID, discountID)):
            query = 'SELECT discountValue FROM discounts WHERE discountID = ?;'
            cur.execute(query, (discountID, ))
            discountValue = cur.fetchone()
            query2 = 'SELECT price FROM orders WHERE orderID = ?;'
            cur.execute(query2, (orderID,))
            orderPrice = cur.fetchone()
            query3 = 'UPDATE orders SET price = ? WHERE orderID = ?;'
            newPrice = int(orderPrice) / (1-(int(discountValue)/100))
            cur.execute(query3, (newPrice, orderID))
            conn.commit()
            query4 = 'DELETE FROM discountList WHERE discountListID = ?;'
            cur.execute(query4, (discountListID,))
            conn.commit()
            conn.close()
            return 1
        else:
            return 0
    
    def get_order(self):
        try:
            conn, cur = openConnection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM orders")
            rows = cur.fetchall()
            orders = [(row[0], row[1], row[2], row[3], row[4], row[5], row[6]) for row in rows]
            # Close the connection after fetching data
            conn.close()
            return orders
        except sqlite3.Error as e:
            print("Error fetching orders:", e)
            return []
        
    def get_foodList(self, orderID):
        try:
            conn, cur = openConnection()
            cur = conn.cursor()
            query = "SELECT * FROM foodList WHERE orderID = ?;"
            cur.execute(query, (orderID,))
            rows = cur.fetchall()
            orders = [(row[0], row[1], row[2]) for row in rows]
            # Close the connection after fetching data
            conn.close()
            return orders
        except sqlite3.Error as e:
            print("Error fetching food list:", e)
            return []
        
    def get_discountList(self, orderID):
        try:
            conn, cur = openConnection()
            cur = conn.cursor()
            query = "SELECT * FROM discountList WHERE orderID = ?;"
            cur.execute(query, (orderID,))
            rows = cur.fetchall()
            orders = [(row[0], row[1], row[2]) for row in rows]
            # Close the connection after fetching data
            conn.close()
            return orders
        except sqlite3.Error as e:
            print("Error fetching discount list:", e)
            return []
        
    def delete_order(self, id):
        try:
            conn, cur = openConnection()
            if self.checkID(id):
                query = "DELETE FROM orders WHERE orderID = ?;"
                cur.execute(query, (id,))
                conn.commit()
                conn.close()
                return 1
            else:
                print("order doesn't exists or invalid syntax")
                conn.close()
                return 0
        except sqlite3.Error as e:
            print("Error deleting order:", e)
