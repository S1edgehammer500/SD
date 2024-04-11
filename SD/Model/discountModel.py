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
    def updateDiscountID(self, dID, newdID):
        conn, cur = openConnection()
        if self.validateDiscountIDSyntax(newdID):
            query1 = "SELECT * FROM discounts WHERE discountID = ?;"
            cur.execute(query1, (newdID, ))
            record = cur.fetchone()
            if record is not None:
                print("Discount ID already exists")
                conn.close()
                return 0
            else:
                query2 = "UPDATE discount SET discountID = ? WHERE discountID = ?;"
                cur.execute(query2, (newdID, dID))
                conn.commit()
                conn.close()
                return 1
        else:
            conn.close()
            return 0

    def updateDiscountValue(self, dID, dCode):
        conn, cur = openConnection()
        if self.validateDiscountValueSyntax(dCode):
            query = "UPDATE users SET discountValue = ? WHERE discountID = ?;"
            cur.execute(query, (dCode, dID))
            conn.commit()
            conn.close()
            return 1
        else:
            conn.close()
            return 0
        

    #validators
    def validateDiscountIDSyntax(self, dID):
        if len(dID) > 0:
            # 2 digits
            pattern = r'[0-9]{2,2}'
            if re.fullmatch(pattern, dID):
                return 1
            else:
                return 0
        else:
            return 0
        
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
        if self.checkEmployeeCode(dID):
            query = 'DELETE FROM discounts WHERE discountID = ?;'

            cur.execute(query, (dID,))

            print("Discount successfully deleted")
            conn.commit()
            conn.close()
            return 1
        else:
            print("Discount doesn't exist or invalid syntax")
            conn.close()
            return 0
        

    def checkDiscountID(self, dID):
        conn, cur = openConnection()
        query = "SELECT discountID FROM discounts WHERE discountID = ?;"
        cur.execute(query, (dID,))
        records = cur.fetchone()
        if records is not None:
            print("Discount already exists")
            conn.close()
            return 1
        else:
            print("Discount doesn't exist")
            conn.close()
            return 0 

    def checkDiscountValue(self, dValue):
        conn, cur = openConnection()
        query = "SELECT discountValue FROM discounts WHERE discountValue = ?;"
        cur.execute(query, (dValue,))
        records = cur.fetchone()
        if records is not None:
            print("Discount already exists")
            conn.close()
            return 1
        else:
            print("Discount doesn't exist")
            conn.close()
            return 0 
        
    # Saves the users details in the database
    def createDiscount(self, dID, dValue): #save discount attributes in database
        conn, cur = openConnection()
        if self.checkDiscountValue(dValue):  
            print('Discount value already exists')
            conn.close()
            return 0
        elif self.checkDiscountID(dID):
            print('Discount ID already exists')
            conn.close()
            return 0
        elif not (self.validateDiscountValueSyntax(dValue)):
            print("Discount value syntax is incorrect")
            conn.close()
            return 0
        else:
            query = 'INSERT INTO discounts (discountID, discountValue) VALUES (? , ?);'
            cur.execute(query, (dID, dValue))
            print('Discount details successfully saved')
            conn.commit()
            conn.close()
            return 1
        
    
    def setDiscountDetails(self, dID):
        conn, cur = openConnection()
        query = "SELECT password, authorisationLevel, baseRestaurant FROM users WHERE employeeCode = ?;"
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
            rows = cur.fetchall()
            records = [(row[0], row[1]) for row in rows]
            # Close the connection after fetching data
            conn.close()
            return records
        except sqlite3.Error as e:
            print("Error fetching discounts:", e)
            return []
    
        

    def __str__(self):
        print("Employee Code: " + self.getCode() + " Password: " + self.getPassword() + "Authorisation Level:" + self.getAuthorisation() + "Base Restaurant:" + self.getBaseRestaurant())