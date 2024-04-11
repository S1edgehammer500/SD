import sqlite3

def openConnection():
    conn = sqlite3.connect('HorizonRestaurantDB.db')
    cur = conn.cursor()
    
    return conn, cur