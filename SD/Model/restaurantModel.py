from Model.Database import *
#from Model.menuModel import *
#from Model.ordersModel import *
import re

class Restaurant: #restaurant class
    def __init__(self):
        self.__restaurantID = ""
        self.__restaurantName = ""
        self.__numberOfTables = ""

    def setRestaurantDetails(self, id):
        conn, cur = openConnection()
        query = "SELECT * FROM restaurant WHERE restaurantID = ?;"
        cur.execute(query,(id,))
        record = cur.fetchone()
        name = record[1]
        tables = record[2]
        restaurant = Restaurant()
        restaurant.setRestaurantID(id)
        restaurant.setRestaurantName(name)
        restaurant.setNumberOfTables(tables)
        conn.close()
        return restaurant

    #setters
    def setRestaurantID(self, id):
        if self.checkRestaurantID(id):
            self.__restaurantID = id
            return 1
        else:
            return 0

    def setRestaurantName(self, resName):
        if self.validateRestaurantSyntax(resName):
            self.__restaurantName = resName
            return 1
        else:
            return 0

    def setNumberOfTables(self, resTables):
        if self.validateTableNumberSyntax(resTables):
            self.__numberOfTables = resTables
            return 1
        else:
            return 0
    
    #getters
    def getRestaurantID(self):
        return self.__restaurantID

    def getRestaurantName(self):
        return self.__restaurantName

    def getNumberOfTables(self):
        return self.__numberOfTables

    #validators
    def validateTableNumberSyntax(self, tables):
        if int(tables) > 0:
            pattern = r'[0-9]{1,2}' # 1 or 2 digit number
            if re.fullmatch(pattern, str(tables)):
                return 1
            else:
                return 0
        else:
            return 0
        
    def validateRestaurantSyntax(self, resName):
        if len(resName) > 0:
            pattern = r'[A-Za-z]{4,}' # At least a 6 letter word
            if re.fullmatch(pattern, resName):
                return 1
            else:
                return 0
        else:
            return 0
        
    def checkRestaurantID(self, restaurantID): #checks if restaurant exists
        conn, cur = openConnection()
        query = 'SELECT restaurantID FROM restaurant WHERE restaurantID = ?;'
        cur.execute(query, (restaurantID,))
        record = cur.fetchone()
        if record is not None:
            print("restaurant exists")
            conn.close()
            return 1
        else:
            print("Restaurant does not exist")
            conn.close()
            return 0
    
    def checkRestaurantName(self, restaurantName):
        conn, cur = openConnection()
        query = 'SELECT * FROM restaurant WHERE restaurantName = ?;'
        cur.execute(query, (restaurantName,))
        record = cur.fetchone()
        if record is not None:
            
            print("Restaurant exists")
            conn.close()  # Close the connection
            return 1
        else:
            print("Restaurant does not exist")
            conn.close()  # Close the connection
            return 0

        
    def updateRestaurant(self, restaurantName=None, numberOfTables=None, restaurantID=None):
        conn, cur = openConnection()
        if restaurantName != None:
            query = 'UPDATE restaurant SET restaurantName = ?  WHERE restaurantID = ?;'
            cur.execute(query, (restaurantName, restaurantID))
            conn.commit()
            print("Updated restaurant name")
            conn.close()
        else:
            print("restaurant name is none")
            conn.close
        if numberOfTables != None:
            query2 = 'UPDATE restaurant SET numberOfTables = ?  WHERE restaurantID = ?;'
            cur.execute(query2, (numberOfTables, restaurantID))
            conn.commit()
            print("Updates table number")
            conn.close()
        else:
            print("restaurant tableNumber is none")
            conn.close
        return 1
        
    def createRestaurant(self, restaurantName, numberOfTables):
        conn, cur = openConnection()
        if not self.checkRestaurantName(restaurantName):
            if (self.validateRestaurantSyntax(restaurantName)) and (self.validateTableNumberSyntax(numberOfTables)):
                query = 'INSERT INTO restaurant (restaurantName, numberOfTables) VALUES (? , ?);'
                cur.execute(query, (restaurantName, numberOfTables))
                conn.commit()
                print("new restaurant created")
                conn.close()
                return 1
            else:
                print("Syntax error")
                return 0
        else:
            print("Restaurant already exists")
            conn.close()
            return 0
        
    def getAllRestaurants(self):
        conn, cur = openConnection()
        query = 'SELECT restaurantName FROM restaurant;'
        cur.execute(query)
        records = cur.fetchall()
        conn.close()
        return records

    def getRestaurantIDFromName(self, name): # drop down menu returns name selected. This is to be used in controller after they have received the name in order to get the ID and call createRestaurantInstance
        conn, cur = openConnection()
        query = "SELECT restaurantID FROM Restaurant WHERE restaurantName = ?;"
        cur.execute(query, (name,))
        record = cur.fetchone()
        conn.close()
        print("Restaurant ID!!!!!!!" + str(record[0]))
        return record[0]
    
    def getRestaurantNameFromID(self, ID): # drop down menu returns name selected. This is to be used in controller after they have received the name in order to get the ID and call createRestaurantInstance
        conn, cur = openConnection()
        query = "SELECT restaurantName FROM Restaurant WHERE restaurantID = ?;"
        cur.execute(query, (ID,))
        record = cur.fetchone()
        conn.close()
        print("Restaurant ID!!!!!!!" + str(record[0]))
        return record[0]
        
    def deleteRestaurant(self, ID):
        conn, cur = openConnection()
        if self.checkRestaurantID(ID):
            query = 'DELETE FROM restaurant WHERE restaurantID = ?;'
            cur.execute(query, (ID,))
            conn.commit()
            print("Restaurant successfully deleted")
            conn.commit()
            conn.close()
            return 1
        else:
            print("Restaurant doesn't exist or invalid syntax")
            conn.close()
            return 0
        



    def get_restaurants(self):
        try:
            conn, cur = openConnection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM restaurant")
            rows = cur.fetchall()
            restaurants = [(row[0], row[1], row[2]) for row in rows]
            # Close the connection after fetching data
            conn.close()
            return restaurants
        except sqlite3.Error as e:
            print("Error fetching restaurants:", e)
            return []
