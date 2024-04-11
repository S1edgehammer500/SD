from passlib.hash import sha256_crypt
import re
from Model.Database import *


conn, cur = openConnection()
query = "SELECT employeeCode FROM users WHERE employeeCode = ?;"
cur.execute(query, ("Jake"))
records = cur.fetchone()
if records is not None:
    print("Account already exists")
    conn.close()
else:
    print("Account doesn't exist")
    conn.close()