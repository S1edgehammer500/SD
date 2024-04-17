from passlib.hash import sha256_crypt
import re
from Model.Database import *

#User class
class Discount:
    def __init__(self):
        # Because of the model = User() line in App we need all of these to be empty to begin with
        self.__discountID = ""
        self.__discountValue = ""


    #getters
    def getDiscountID(self):
        return self.__discountID
    
    def getDiscountValue(self):
        return self.__discountValue
    
    def getDiscounts(self):
        try:
            conn, cur = openConnection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM discount")
            rows = cur.fetchall()
            users = [(row[0], row[1]) for row in rows]
            conn.close()
            return users
        except sqlite3.Error as e:
            print("Error fetching discounts:", e)
            return []
        
    #setters
    
    def setDiscountID(self, discountID):
        self.__discountID = discountID
        
    def setDiscountValue(self, discountValue):
        self.__discountValue = discountValue

    #updaters

    def updateDiscountValue(self, dID, dValue):
        conn, cur = openConnection()
        if self.validateDiscountValueSyntax(dID):
            query = "UPDATE discounts SET discountValue = ? WHERE discountID = ?;"
            cur.execute(query, (dValue, dID))
            conn.commit()
            conn.close()
            return 1
        else:
            conn.close()
            return 0
        

    #validators
        
    def validateDiscountValueSyntax(self, dValue):
        if len(dValue) > 0:
            dValue = int(dValue)
            if dValue > 0 and dValue < 101:
                return 1
            else:
                return 0
        else:
            return 0
        
    # Delete records

    def deleteDiscount(self, dID):
        conn, cur = openConnection()
        
        query = 'DELETE FROM discounts WHERE discountID = ?;'

        cur.execute(query, (dID,))

        print("Discount successfully deleted")
        conn.commit()
        conn.close()
        return 1
        

    def checkDiscountValue(self, dValue):
        conn, cur = openConnection()
        query = "SELECT discountValue FROM discounts WHERE discountValue = ?;"
        cur.execute(query, (dValue,))
        records = cur.fetchone()
        if records is not None:
            print("Discount exists")
            conn.close()
            return 1
        else:
            print("Discount doesn't exist")
            conn.close()
            return 0 
        
    # Saves the users details in the database
    def createDiscount(self, dValue): #save discount attributes in database
        conn, cur = openConnection()
        if self.checkDiscountValue(dValue):  
            print('Discount value already exists')
            conn.close()
            return 0
        elif not (self.validateDiscountValueSyntax(dValue)):
            print("Discount value syntax is incorrect")
            conn.close()
            return 0
        else:

            query = 'INSERT INTO discounts (discountValue) VALUES (?);'
            cur.execute(query, (dValue,))
            
            print('Discount details successfully saved')
            conn.commit()
            conn.close()
            return 1
        
    
    def setDiscountDetails(self, dID):
        conn, cur = openConnection()
        query = "SELECT discountValue FROM discounts WHERE discountID = ?;"
        cur.execute(query, (dID,))
        record = cur.fetchone()
        self.setDiscountID(dID)
        self.setDiscountValue(record[0])
        print("Login details set")
        conn.close()

    def get_discounts(self):
        try:
            conn, cur = openConnection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM discounts")
            records = cur.fetchall()
            dIDs = [row[0] for row in records]
            dValues = [row[1] for row in records]
            # Close the connection after fetching data
            conn.close()
            return dIDs, dValues
        except sqlite3.Error as e:
            print("Error fetching discounts:", e)
            return []
    
        

    def __str__(self):
        print("Employee Code: " + self.getCode() + " Password: " + self.getPassword() + "Authorisation Level:" + self.getAuthorisation() + "Base Restaurant:" + self.getBaseRestaurant())