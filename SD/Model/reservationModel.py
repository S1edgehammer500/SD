from Model.Database import *
import re
import datetime

class Reservation: #offers class

    def __init__(self):
        self.__ID = ""
        self.__restaurantName = ""
        self.__tables = ""
        self.__startTime = ""
        self.__endTime = ""
        self.__Name = ""

    def setReservationDetails(self, ID):
         conn, cur = openConnection()
         query = "SELECT * FROM reservation WHERE reservationID = ?;"
         cur.execute(query,(ID,))
         record = cur.fetchone()
         restaurantName = record[1]
         tables = record[2]
         startTime = record[3]
         endTime = record[4]
         Name = record[5]
         self.setTables(tables, restaurantName)
         self.setStartTime(startTime)
         self.setEndTime(endTime, startTime)
         self.setID(ID)
         self.setRestaurantName(restaurantName)
         self.setName(Name)
         conn.close()


    #setters  
    def setTables(self, tables, restaurantName):
        if self.validateTables(tables, restaurantName):
            self.__tables = tables
            return 1
        else:
            return 0
        
    def setStartTime(self, startTime):
        if self.validateStartTime(startTime):
            self.__startTime = startTime
            return 1
        else:
            return 0 

    def setEndTime(self, endTime, startTime):
        if self.validateEndTime(endTime, startTime):
            self.__endTime = endTime
            return 1
        else:
            return 0 
    
    def setID(self, ID):
        self.__ID = ID
        return 1
    
    def setRestaurantName(self, restaurantName):
        if self.validateRestaurantName(restaurantName):
            self.__restaurantName = restaurantName
            return 1
        else:
            return 0
    
    def setName(self, Name):
        if self.validateName(Name):
            self.__Name = Name
            return 1
        else:
            return 0 
    #getters
    def getTables(self):
        return self.__tables
    
    def getStartTime(self):
        return self.__startTime
    
    def getEndTime(self):
        return self.__endTime
    
    def getID(self):
        return self.__ID
    
    def getRestaurantName(self):
        return self.__restaurantName
    
    def getName(self):
        return self.__Name
    
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
        
    def checkID(self, ID):
        conn, cur = openConnection()
        query = 'SELECT * FROM reservation WHERE reservationID = ?;'
        cur.execute(query, (ID,))
        record = cur.fetchone()
        if record is not None:
            print("Reservation exists")
            conn.close()  # Close the connection
            return 1
        else:
            print("Reservation does not exist")
            conn.close()  # Close the connection
            return 0

    def validateTables(self, tables, restaurantName):
        if not isinstance(tables, int):
            return 0  # Returning error message for non-integer input

        if 1 <= tables <= 99:  # Checking if tableNumber is within the range
            conn, cur = openConnection()
            query2 = "SELECT tables FROM restaurant WHERE restaurantName = ?;"
            cur.execute(query2, (restaurantName,))
            record2 = cur.fetchone()

            if record2 is not None and tables <= record2[0]:
                conn.close()
                print("Valid table number")
                return 1  # Valid table number within the restaurant's table count
            else:
                conn.close()
                print("Invalid table number")
                return 0  # Indicates invalid table number or table number too large
        else:
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
        
    def validateEndTime(self, endTime, startTime):
        if endTime != None:
            end_time = datetime.datetime.strptime(endTime, "%Y-%m-%d %H:%M:%S")
            start_time = datetime.datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")

            if end_time < start_time:
                print("Time out of range")
                return 0
            else:
                return 1
        else:
            return 1
        
    def validateName(self, Name):
        if len(Name)>0:
            pattern = r'[A-Za-z]{3,}'
            if re.fullmatch(pattern, Name):
                return 1
            else:
                print("Invalid Name Syntax")
                return 0
        else:
            print("Name length too small")
            return 0
   
        
    def createReservation(self, restaurantName, tables, startTime, endTime, Name):
        conn, cur = openConnection()
        if (self.validateTables(tables,restaurantName)) and (self.validateStartTime(startTime) and self.validateEndTime(endTime, startTime) and self.validateName(Name)):
            query = 'INSERT INTO reservation (restaurantName, tables, startTime, endTime, Name) VALUES (?, ?, ?, ?, ?);'
            cur.execute(query, (restaurantName, tables, startTime, endTime, Name))
            conn.commit()
            print("new reservation created")
            conn.close()
            return 1
        else:
            return 0
        
    def deleteReservation(self, ID):
        try:
            conn, cur = openConnection()
            if self.checkID(ID):
                query = "DELETE FROM reservation WHERE offerID = ?;"
                cur.execute(query, (ID,))
                conn.commit()
                conn.close()
                return 1
            else:
                print("Reservation doesn't exists or invalid syntax")
                conn.close()
                return 0
        except sqlite3.Error as e:
            print("Error deleting reservation:", e)
            
    def updateName(self, ID, Name):
        if Name != None:
            if self.validateName(Name):
                if self.checkID(ID):
                    conn, cur = openConnection()
                    query = 'UPDATE reservation SET Name = ? WHERE reservationID = ?;'
                    cur.execute(query, (Name,ID))
                    conn.commit()
                    conn.close()
                    return 1
                else:
                    return 0
            else:
                return 0
        else:
            return 0
                                
            
    def updateTables(self, ID, tables):
        if tables != None:
            self.setReservationDetails(ID)
            restaurantName = self.getRestaurantName()
            if self.validateTables(tables, restaurantName):
                if self.checkID(ID):
                    conn, cur = openConnection()
                    query = 'UPDATE reservation SET tables = ? WHERE reservationID = ?;'
                    cur.execute(query, (tables,ID))
                    conn.commit()
                    conn.close()
                    return 1
                else:
                    return 0
            else:
                return 0
        else:
            return 0
        
    def updateStartTime(self, ID, startTime, endTime):
        if startTime != None:
            if self.validateStartTime(startTime):
                if self.validateEndTime(endTime, startTime):
                    if self.checkID(ID):
                        conn, cur = openConnection()
                        query = 'UPDATE reservation SET startTime = ? WHERE reservationID = ?;'
                        cur.execute(query, (startTime,ID))
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
        
    def updateStartTime(self, ID, endTime, startTime):
        if endTime != None:
            if self.validateStartTime(endTime):
                if self.validateEndTime(endTime, startTime):
                    if self.checkID(ID):
                        conn, cur = openConnection()
                        query = 'UPDATE reservation SET endTime = ? WHERE reservationID = ?;'
                        cur.execute(query, (endTime,ID))
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
        
    def getIDList(self, restaurantName):
        conn, cur = openConnection()
        query = 'SELECT reservationID FROM reservation WHERE restaurantName = ? ORDER BY restaurantName;'
        cur.execute(query, (restaurantName,))
        record = cur.fetchall()
        conn.close()
        return record
    
    def getTablesList(self, restaurantName):
        conn, cur = openConnection()
        query = 'SELECT tables FROM reservation WHERE restaurantName = ? ORDER BY restaurantName;'
        cur.execute(query, (restaurantName,))
        record = cur.fetchall()
        conn.close()
        return record
    
    def getStartTimeList(self, restaurantName):
        conn, cur = openConnection()
        query = 'SELECT startTime FROM reservation WHERE restaurantName = ? ORDER BY restaurantName;'
        cur.execute(query, (restaurantName,))
        record = cur.fetchall()
        conn.close()
        return record
    
    def getEndTimeList(self, restaurantName):
        conn, cur = openConnection()
        query = 'SELECT endTime FROM reservation WHERE restaurantName = ? ORDER BY restaurantName;'
        cur.execute(query, (restaurantName,))
        record = cur.fetchall()
        conn.close()
        return record
    
        
    def getNameList(self, restaurantName):
        conn, cur = openConnection()
        query = 'SELECT Name FROM reservation WHERE restaurantName = ? ORDER BY restaurantName;'
        cur.execute(query, (restaurantName,))
        record = cur.fetchall()
        conn.close()
        return record