from passlib.hash import sha256_crypt
import re
from Model.Database import *

#User class
class User:
    def __init__(self):
        # Because of the model = User() line in App we need all of these to be empty to begin with
        self.__employeeCode = ""
        self.__password = ""
        self.__authorisationLevel = ""
        self.__baseRestaurant = ""
        self.__loggedStatus = False

    #getters
    def getPassword(self):
        return self.__password
    
    def getCode(self):
        return self.__employeeCode
    
    def getAuthorisation(self):
        return self.__authorisationLevel
    
    def getBaseRestaurant(self):
        return self.__baseRestaurant

    def getLoggedStatus(self):
        return self.__loggedStatus
    
    def get_users(self):
        try:
            conn, cur = openConnection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM users")
            rows = cur.fetchall()
            users = [(row[0], row[2], row[3]) for row in rows]
            conn.close()
            return users
        except sqlite3.Error as e:
            print("Error fetching discounts:", e)
            return []
        
    #setters
    
    def setLoggedStatus(self):
        self.__loggedStatus = True
        return 1 
        
    def setPassword(self, password):
        if self.validateUserpasswordSyntax(password):
            self.__password = sha256_crypt.hash(str(password))
            return 1
        else:
            return 0

    def setCode(self, code):
         if self.validateCodeSyntax(code):
             self.__employeeCode = code
             return 1
         else:
             return 0

        
    def setAuthorisation(self, authorisation):
        if self.validateAuthorisationSyntax(authorisation):
            self.__authorisationLevel = authorisation
            return 1
        else:
            return 0
        
    def setBaseRestaurant(self, base):
        if self.validateBaseRestaurantSyntax(base):
            self.__baseRestaurant = base
            return 1
        else:
            return 0

    def checkPassword(self, tempPassword):
        return sha256_crypt.verify(tempPassword, self.getPassword())

    #updaters
    def updatePassword(self, code, pw):
        conn, cur = openConnection()
        if self.validateUserpasswordSyntax(pw):
            query = 'UPDATE users SET password = ? WHERE employeeCode = ?;'
            cur.execute(query, (sha256_crypt.hash(pw), code))
            conn.commit()
            conn.close()
            return 1
        else:
            conn.close()
            return 0

    def updateCode(self, code, newCode):
        conn, cur = openConnection()
        if self.validateCodeSyntax(newCode):
            query1 = "SELECT * FROM users WHERE employeeCode = ?;"
            cur.execute(query1, (newCode, ))
            record = cur.fetchone()
            if record is not None:
                print("Employee code already exists")
                conn.close()
                return 0
            else:
                query2 = "UPDATE users SET employeeCode = ? WHERE employeeCode = ?;"
                cur.execute(query2, (newCode, code))
                conn.commit()
                conn.close()
                return 1
        else:
            conn.close()
            return 0

    def updateAuthorisation(self, code, auth):
        conn, cur = openConnection()
        if self.validateAuthorisationSyntax(auth):
            query = "UPDATE users SET authorisationLevel = ? WHERE employeeCode = ?;"
            cur.execute(query, (auth, code))
            conn.commit()
            conn.close()
            return 1
        else:
            conn.close()
            return 0

    def updateBaseRestaurant(self, code, base):
        conn, cur = openConnection()
        if self.validateBaseRestaurantSyntax(base):
            query = "UPDATE users SET baseRestaurant = ? WHERE employeeCode = ?;"
            cur.execute(query, (base, code))
            conn.commit()
            conn.close()
            return 1
        else:
            conn.close()
            return 0
        

    #validators
    def validateCodeSyntax(self, code):
        if len(code) > 0:
            pattern = r'[A-Za-z0-9]{2,}'
            if re.fullmatch(pattern, code):
                return 1
            else:
                return 0
        else:
            return 0
        
    def validateAuthorisationSyntax(self, code):
        if code not in ["staff", "chef", "manager", "admin"]:
            return 0
        else:
            return 1
        
    def validateBaseRestaurantSyntax(self, base):
        conn, cur = openConnection()
        query = 'SELECT restaurantName FROM restaurant WHERE restaurantName = ?;'
        cur.execute(query, (base,))
        record = cur.fetchone()
        if record is not None:
            print("restaurant exists - baseRestaurant validation")
            conn.close()
            return 1
        else:
            print("restaurant does not exist")
            conn.close()
            return 0

    def validateUserpasswordSyntax(self, pw):
        if isinstance(pw, int):
            return 0
        elif isinstance(pw, str) and len(pw) > 0:
            pattern = r'[A-Za-z0-9 ]{6,}' 
            if re.fullmatch(pattern, pw):
                return 1
            else:
                return 0
        else:
            return 0

    
    # Checks whether the usercode and password exist. Returns true if it exists
    def checkCodePassword(self, code, pw): #check if code and password exist 
        conn, cur = openConnection()
        query = 'SELECT password, authorisationLevel, baseRestaurant FROM users WHERE employeeCode = ?;' #checks that username and password match
        cur.execute(query, (code,))
        records = cur.fetchone()
        
        if records is not None:
            print('Record exists')

            if sha256_crypt.verify(pw, records[0]):
                conn.close()
                return 1    # correct username and password
            else:
                conn.close()
                return 0  # incorrect password

        else:
            print('Record does not exist')
            conn.close()
            return 0    #record does not exist

    def checkEmployeeCode(self, code):
        conn, cur = openConnection()
        query = "SELECT employeeCode FROM users WHERE employeeCode = ?;"
        cur.execute(query, (code,))
        records = cur.fetchone()
        if records is not None:
            print("Account already exists")
            conn.close()
            return 1
        else:
            print("Account doesn't exist")
            conn.close()
            return 0 
        
    # Saves the users details in the database
    def saveUserDetails(self, code, pw, al, br): #save user attributes in database - only admins can do this
        conn, cur = openConnection()
        if self.checkEmployeeCode(code):  
            print('Employee Code or Password already exists')
            conn.close()
            return 0
        elif not (self.validateCodeSyntax(code)) and not (self.validateUserpasswordSyntax(pw)):
            print("Employee code or password syntax is incorrect")
            conn.close()
            return 0
        else:
            query = 'INSERT INTO users (employeeCode, password, authorisationLevel, baseRestaurant) VALUES (? , ?,  ?,  ?);'
            cur.execute(query, (code, sha256_crypt.hash(pw), al, br))
            print('Account details successfully saved')
            conn.commit()
            conn.close()
            return 1
        
    def deleteUser(self, code):
        conn, cur = openConnection()
        if self.checkEmployeeCode(code):
            query = 'DELETE FROM users WHERE employeeCode = ?;'

            cur.execute(query, (code,))

            print("Account successfully deleted")
            conn.commit()
            conn.close()
            return 1
        else:
            print("Account doesn't exist or invalid syntax")
            conn.close()
            return 0
    
    def setLoginDetails(self, code):
        conn, cur = openConnection()
        query = "SELECT password, authorisationLevel, baseRestaurant FROM users WHERE employeeCode = ?;"
        cur.execute(query, (code,))
        record = cur.fetchone()
        self.setCode(code)
        self.setPassword(record[0])
        self.setAuthorisation(record[1])
        self.setBaseRestaurant(record[2])
        print("Login details set")
        conn.close()

    def getAuthorisationLevels(self):
        conn, cur = openConnection()
        query = "SELECT authorisationLevel FROM users WHERE authorisationLevel != ? AND baseRestaurant = ? ORDER BY employeeCode;"
        cur.execute(query, ('admin', self.__baseRestaurant))
        record = cur.fetchall()
        conn.close()
        return record
    
    def getBaseRestaurants(self):
        conn, cur = openConnection()
        query = "SELECT baseRestaurant FROM users WHERE authorisationLevel != ? AND baseRestaurant = ? ORDER BY employeeCode;"
        cur.execute(query, ('admin', self.__baseRestaurant))
        record = cur.fetchall()
        conn.close()
        return record
    
    def getEmployeeCodes(self):
        conn, cur = openConnection()
        query = "SELECT employeeCode FROM users WHERE authorisationLevel != ? AND baseRestaurant = ? ORDER BY employeeCode;"
        cur.execute(query, ('admin', self.__baseRestaurant))
        record = cur.fetchall()
        conn.close()
        return record
    
    def getSpecificBaseRestaurant(self, code):
        conn, cur = openConnection()
        query = "SELECT baseRestaurant FROM users WHERE employeeCode = ?;"
        cur.execute(query, (code,))
        record = cur.fetchone()
        conn.close()
        return record
    
    def getSpecificAuthorisationLevel(self, code):
        conn, cur = openConnection()
        query = "SELECT baseRestaurant FROM users WHERE employeeCode = ?;"
        cur.execute(query, (code,))
        record = cur.fetchone()
        conn.close()
        return record
    
    def getStaffEmployeeCodes(self):
        conn, cur = openConnection()
        query = "SELECT employeeCode FROM users WHERE authorisationLevel != ? AND authorisationLevel != ? AND baseRestaurant = ? ORDER BY employeeCode;"
        cur.execute(query, ('manager', 'admin', self.__baseRestaurant))
        record = cur.fetchall()
        conn.close()
        return record
        

    def __str__(self):
        print("Employee Code: " + self.getCode() + " Password: " + self.getPassword() + "Authorisation Level:" + self.getAuthorisation() + "Base Restaurant:" + self.getBaseRestaurant())