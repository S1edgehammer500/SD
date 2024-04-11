import mysql.connector                      #Andre Barnett - 22025153
from mysql.connector import errorcode
 
hostname    = "localhost"
db = "horizontravels"
username    = "root"
passwd  = "fwdakiddre04" 


def getConnection():    
    try:
        conn = mysql.connector.connect(host=hostname,                              
                              user=username,
                              password=passwd,
                              database = db)  
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print('User name or Password is not working')
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print('Database does not exist')
        else:
            print(err)                        
    else:  #will execute if there is no exception raised in try block
        return conn   
                