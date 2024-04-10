from Model.Database import *
#from Model.menuModel import *
#from Model.ordersModel import *
import re

class Restaurant: #restaurant class
    def __init__(self):
        self.__restaurantName = ""
        self.__numberOfTables = ""

    def setRestaurantDetails(self, restaurantName):
        conn, cur = openConnection()
        query = "SELECT * FROM restaurant WHERE restaurantName = ?;"
        cur.execute(query,(restaurantName,))
        record = cur.fetchone()
        name = record[0]
        tables = record[1]
        self.setRestaurantName(name)
        self.setNumberOfTables(tables)
        conn.close()

    #setters

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
                if not (self.checkRestaurantName(resName)):

                    return 1
                else:
                    return 0
            else:
                return 0
        else:
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

        
    def updateRestaurantName(self, previousName, currentName):
        conn, cur = openConnection()
        if previousName != None and currentName != None:
            if self.validateRestaurantSyntax(currentName):
                if self.checkRestaurantName(previousName):
                    if not(self.checkRestaurantName(currentName)):
                            query = 'UPDATE restaurant SET restaurantName = ? WHERE restaurantName = ?;'
                            cur.execute(query, (currentName, previousName))
                            conn.commit()
                            print("Updated restaurant name")
                            conn.close()
                    else:
                        return 0
                else:
                    return 0
            else:
                return 0
        else:
            print("restaurant name is none")
            conn.close
        return 1
    
    def updateNumberOfTables(self, restaurantName, numberOfTables):
        conn, cur = openConnection()
        if numberOfTables != None:
            if self.validateTableNumberSyntax(numberOfTables):
                query = 'UPDATE restaurant SET numberOfTables = ? WHERE restaurantName = ?;'
                cur.execute(query, (numberOfTables, restaurantName))
                conn.commit()
                print("Updated number of tables")
                conn.close()
                return 1
            else:
                return 0
        else:
            print("Number of tables is none")
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
        
    def deleteRestaurant(self, restaurantName):
        conn, cur = openConnection()
        if self.checkRestaurantName(restaurantName):
            query = 'DELETE FROM restaurant WHERE restaurantName = ?;'
            cur.execute(query, (restaurantName,))
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
            restaurants = [(row[0], row[1]) for row in rows]
            # Close the connection after fetching data
            conn.close()
            return restaurants
        except sqlite3.Error as e:
            print("Error fetching restaurants:", e)
            return []
