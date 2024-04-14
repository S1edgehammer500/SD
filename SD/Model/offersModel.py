from Model.Database import *
import re

class Offers: #offers class

    def __init__(self):
        self.__ID = ""
        self.__offerDescription = ""
        self.__restaurantName = ""

    def setOfferDetails(self, ID):
         conn, cur = openConnection()
         query = "SELECT * FROM offer WHERE offerID = ?;"
         cur.execute(query,(ID,))
         record = cur.fetchone()
         offerDescription = record[1]
         restaurantName = record[2]
         self.setOfferDescription(offerDescription)
         self.setID(ID)
         self.setRestaurantName(restaurantName)
         conn.close()


    #setters  
    def setOfferDescription(self, offerDescription):
        if self.validateOfferDescription(offerDescription):
            self.__offerDescription = offerDescription
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
    
    #getters
    def getOfferDescription(self):
        return self.__offerDescription
    
    def getID(self):
        return self.__ID
    
    def getRestaurantName(self):
        return self.__restaurantName
    
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
        
    def checkRestaurantDesc(self, restaurantName, offerDescription):
        conn, cur = openConnection()
        query = 'SELECT * FROM offer WHERE restaurantName = ? AND offerDescription = ?;'
        cur.execute(query, (restaurantName, offerDescription))
        record = cur.fetchone()
        if record is not None:
            print("Restaurant and description combination exists")
            conn.close()
            return 1
        else:
            print("Restaurant and description combination don't exist")
            conn.close()
            return 0
        
    def checkID(self, ID):
        conn, cur = openConnection()
        query = 'SELECT * FROM offer WHERE offerID = ?;'
        cur.execute(query, (ID,))
        record = cur.fetchone()
        if record is not None:
            print("Offer exists")
            conn.close()  # Close the connection
            return 1
        else:
            print("Offer does not exist")
            conn.close()  # Close the connection
            return 0

    def validateOfferDescription(self, offerDescription):
        if offerDescription is not None and len(offerDescription) > 0:
            pattern = r'[A-Za-z\s]{3,}'
            if re.fullmatch(pattern, offerDescription):
                return 1
            else:
                print("Invalid offer Syntax")
                return 0
        else:
            print("offer too small")
            return 0
        
    def updateOfferDescription(self, offerDescription, ID):
        if offerDescription != None:
            if self.validateOfferDescription(offerDescription):
                if self.checkID(ID) and not (self.checkRestaurantDesc(self.__restaurantName, offerDescription)):
                    conn, cur = openConnection()
                    query = 'UPDATE offer SET offerDescription = ? WHERE offerID = ?;'
                    cur.execute(query, (offerDescription,ID))
                    conn.commit()
                    conn.close()
                    return 1
                else:
                    return 0
            else:
                return 0
        else:
            return 0
        
    def createOffer(self, offerDescription, restaurantName):
        conn, cur = openConnection()
        if (self.validateOfferDescription(offerDescription)) and (self.validateRestaurantName(restaurantName)):
            query = 'INSERT INTO offer (offerDescription, restaurantName) VALUES (?, ?);'
            cur.execute(query, (offerDescription, restaurantName))
            conn.commit()
            print("new offer created")
            conn.close()
            return 1
        else:
            return 0
        
    def get_offer_list(self):
        try:
            conn, cur = openConnection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM offer")
            rows = cur.fetchall()
            offer_list = [(row[0], row[1], row[2]) for row in rows]
            conn.close()
            return offer_list
        except sqlite3.Error as e:
            print("Error fetching offer list:", e)
            return []
        
    def delete_offer(self, ID):
        try:
            conn, cur = openConnection()
            if self.checkID(ID):
                query = "DELETE FROM offer WHERE offerID = ?;"
                cur.execute(query, (ID,))
                conn.commit()
                conn.close()
                return 1
            else:
                print("Offer doesn't exists or invalid syntax")
                conn.close()
                return 0
        except sqlite3.Error as e:
            print("Error deleting offer:", e)
