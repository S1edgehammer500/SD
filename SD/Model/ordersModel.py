from Model.Database import *
import re
import datetime
import strip

class Order: #order class

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
         restaurantName = record[1]
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
         self.setReadyTime(readyTime, startTime)
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
        if self.validateTableNumber(tableNumber, self.__restaurantName):
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
        
    def setReadyTime(self, readyTime, startTime):
        if self.validateReadyTime(readyTime, startTime):
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
            print("Invalid status")
            return 0
        else:
            print("Valid status")
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
            print("Table number is not int")
            return 0  # Returning error message for non-integer input

        if 1 <= tableNumber <= 99:  # Checking if tableNumber is within the range
            conn, cur = openConnection()
            query2 = "SELECT numberOfTables FROM restaurant WHERE restaurantName = ?;"
            cur.execute(query2, (restaurantName,))
            record2 = cur.fetchone()

            if record2 is not None and tableNumber <= record2[0]:
                conn.close()
                print("Valid table number")
                return 1  # Valid table number within the restaurant's table count
            else:
                conn.close()
                print("Invalid table number")
                return 0  # Indicates invalid table number or table number too large
        else:
            print("Table number out of range")
            return 0  # Indicates table number out of range
        
    def validateStartTime(self, startTime):
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
    
    def validateReadyTime(self, readyTime, startTime):
        if readyTime != None:
            ready_time = datetime.datetime.strptime(readyTime, "%Y-%m-%d %H:%M:%S")
            start_time = datetime.datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")

            if ready_time < start_time:
                print("Time out of range")
                return 0
            else:
                return 1
        else:
            return 1
        
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
        
    def checkFoodInOrder(self, orderID, foodName, foodListID):
        conn, cur = openConnection()
        query = 'SELECT * FROM foodList WHERE foodListID = ?;'
        cur.execute(query, (foodListID,))
        record = cur.fetchone()
        if record is not None:
            if record[1] != orderID and record[2] != foodName:
                print("Food is not in order")
                conn.close()
                return 0
            else:
                print("Food is in order")
                conn.close()
                return 1
        else:
            print("Food is not in order")
            conn.close()
            return 0
        
    def checkDiscountInOrder(self, orderID, discountID, discountListID):
        conn, cur = openConnection()
        query = 'SELECT * FROM discountList WHERE orderID = ? AND discountID = ?;'
        cur.execute(query, (orderID, discountID))
        record = cur.fetchone()
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" + str(record))
        if record is not None:
            if record[0] != discountListID:
                conn.close()
                return 0
            else:
                conn.close()
                return 1
        else:
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
                    print("Update Status Worked")
                    return 1
                else:
                    print("Invalid status")
                    return 0
            else:
                print("Invalid ID")
                return 0
        else:
            print("None")
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
                if self.validateTableNumber(table, self.__restaurantName):
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
        
    def updateReadyTime(self, readyTime, id, startTime):
        if readyTime != None:
            if self.checkID(id):
                if self.validateReadyTime(readyTime, startTime):
                    conn, cur = openConnection()
                    query = 'UPDATE orders SET readyTime = ? WHERE orderID = ?;'
                    cur.execute(query, (readyTime, id))
                    conn.commit()
                    conn.close()
                    return 1
                else:
                    print("Invalid ready time")
                    return 0
            else:
                return 0
        else:
            return 1

        
    def createOrder(self, restaurantName, status, tableNumber, startTime, readyTime):
        conn, cur = openConnection()
        if (self.validateRestaurantName(restaurantName)) and (self.validateStatus(status)) and (self.validateTableNumber(tableNumber, restaurantName) and (self.validateStartTime(startTime) and (self.validateReadyTime(readyTime, startTime)))):
            query = 'INSERT INTO orders (restaurantName, status, orderPrice, tableNumber, startTime, readyTime) VALUES (?,?,?,?,?,?);'
            cur.execute(query, (restaurantName, status, 0, tableNumber, startTime, readyTime))
            conn.commit()
            orderID = cur.lastrowid
            self.setID(orderID)
            print("new order created")
            conn.close()
            return 1
        else:
            conn.close()
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
            foodPrice = str(foodPrice).strip("(")
            foodPrice = str(foodPrice).strip(")")
            foodPrice = str(foodPrice).strip(",")
            query3 = 'SELECT orderPrice FROM orders WHERE orderID = ?;'
            cur.execute(query3, (orderID,))
            orderPrice = cur.fetchone()
            orderPrice = str(orderPrice).strip("(")
            orderPrice = str(orderPrice).strip(")")
            orderPrice = str(orderPrice).strip(",")
            query4 = 'UPDATE orders SET orderPrice = ? WHERE orderID = ?;'
            newPrice = float(orderPrice)+float(foodPrice)
            cur.execute(query4, (newPrice, orderID))
            conn.commit()
            conn.close()
            return 1
        else:
            conn.close()
            return 0
        
    def removeFoodFromOrder(self, orderID, foodName, foodListID):
        conn, cur = openConnection()
        if (self.validateFoodName(foodName) and self.checkID(orderID) and self.checkFoodListID(foodListID) and self.checkFoodInOrder(orderID, foodName, foodListID)):
            query = 'SELECT price FROM food WHERE foodName = ?;'
            cur.execute(query, (foodName, ))
            foodPrice = cur.fetchone()
            foodPrice = str(foodPrice).strip("(")
            foodPrice = str(foodPrice).strip(")")
            foodPrice = str(foodPrice).strip(",")
            query2 = 'SELECT orderPrice FROM orders WHERE orderID = ?;'
            cur.execute(query2, (orderID,))
            orderPrice = cur.fetchone()
            orderPrice = str(orderPrice).strip("(")
            orderPrice = str(orderPrice).strip(")")
            orderPrice = str(orderPrice).strip(",")
            query3 = 'UPDATE orders SET orderPrice = ? WHERE orderID = ?;'
            newPrice = float(orderPrice) - float(foodPrice)
            cur.execute(query3, (newPrice, orderID))
            conn.commit()
            query4 = 'DELETE FROM foodList WHERE foodListID = ?;'
            cur.execute(query4, (foodListID,))
            conn.commit()
            conn.close()
            return 1
        else:
            conn.close()
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
            discountValue = str(discountValue).strip("(")
            discountValue = str(discountValue).strip(")")
            discountValue = str(discountValue).strip(",")
            query3 = 'SELECT orderPrice FROM orders WHERE orderID = ?;'
            cur.execute(query3, (orderID,))
            orderPrice = cur.fetchone()
            orderPrice = str(orderPrice).strip("(")
            orderPrice = str(orderPrice).strip(")")
            orderPrice = str(orderPrice).strip(",")
            query4 = 'UPDATE orders SET orderPrice = ? WHERE orderID = ?;'
            newPrice = float(orderPrice) * (1-(float(discountValue)/100))
            cur.execute(query4, (newPrice, orderID))
            conn.commit()
            conn.close()
            return 1
        else:
            conn.close()
            return 0
        
    def removeDiscountFromOrder(self, orderID, discountID, discountListID):
        conn, cur = openConnection()
        if (self.checkDiscountID(discountID)) and (self.checkID(orderID)) and (self.checkDiscountListID(discountListID)) and (self.checkDiscountInOrder(orderID, discountID, discountListID)):
            query = 'SELECT discountValue FROM discounts WHERE discountID = ?;'
            cur.execute(query, (discountID, ))
            discountValue = cur.fetchone()
            discountValue = str(discountValue).strip("(")
            discountValue = str(discountValue).strip(")")
            discountValue = str(discountValue).strip(",")
            query2 = 'SELECT orderPrice FROM orders WHERE orderID = ?;'
            cur.execute(query2, (orderID,))
            orderPrice = cur.fetchone()
            orderPrice = str(orderPrice).strip("(")
            orderPrice = str(orderPrice).strip(")")
            orderPrice = str(orderPrice).strip(",")
            query3 = 'UPDATE orders SET orderPrice = ? WHERE orderID = ?;'
            newPrice = float(orderPrice) / (1-(float(discountValue)/100))
            cur.execute(query3, (newPrice, orderID))
            conn.commit()
            query4 = 'DELETE FROM discountList WHERE discountListID = ?;'
            cur.execute(query4, (discountListID,))
            conn.commit()
            conn.close()
            return 1
        else:
            conn.close()
            return 0
    
    def get_order(self, restaurantName):
        try:
            conn, cur = openConnection()
            cur = conn.cursor()
            query = "SELECT * FROM orders WHERE restaurantName = ? AND status != ? AND status != ?;"
            cur.execute(query, (restaurantName,'Payment Completed', 'Cancelled'))
            rows = cur.fetchall()
            orders = [(row[0], row[1], row[2], row[3], row[4], row[5], row[6]) for row in rows]
            # Close the connection after fetching data
            conn.close()
            return orders
        except sqlite3.Error as e:
            print("Error fetching orders:", e)
            return []
        
    def getFoodList(self):
        conn, cur = openConnection()
        query = "SELECT foodName FROM foodList WHERE orderID == ? ORDER BY foodListID;"
        cur.execute(query, (self.__ID,))
        record = cur.fetchall()
        conn.close()
        return record
    
    def getSpecificFoodList(self, id):
        conn, cur = openConnection()
        query = "SELECT foodName FROM foodList WHERE foodListID = ?;"
        cur.execute(query, (id,))
        record = cur.fetchall()
        conn.close()
        return record
    
    def getFoodListPrice(self, foodName):
        conn, cur = openConnection()
        query = "SELECT price FROM food WHERE foodName = ?;"
        cur.execute(query, (foodName,))
        record = cur.fetchone()
        conn.close()
        return record
    
    def getFoodListID(self):
        conn, cur = openConnection()
        query = "SELECT foodListID FROM foodList WHERE orderID == ? ORDER BY foodListID;"
        cur.execute(query, (self.__ID,))
        record = cur.fetchall()
        conn.close()
        return record
        
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
        
    def getDiscountValues(self, orderID):
        conn, cur = openConnection()
        cur = conn.cursor()
        query = "SELECT discountID FROM discountList WHERE orderID = ?;"
        cur.execute(query, (orderID,))
        rows = cur.fetchall()
        discountIDs = []
        rows = strip.it(rows)
        for row in rows:
            query2 = "SELECT discountValue FROM discounts WHERE discountID = ?;"
            cur.execute(query2, (row,))
            record = cur.fetchone()
            record = strip.it(record)
            record = str(record)
            record = record.strip("[")
            record = record.strip("]")
            record = record.strip("'")
            record = record+"%"
            discountIDs.append(record)
        conn.close()
        return discountIDs
        
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
