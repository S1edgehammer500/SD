import sqlite3

def openConnection():
    conn = sqlite3.connect('HorizonRestaurantDB.db')
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()
    return conn, cur