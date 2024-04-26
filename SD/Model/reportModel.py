import re
from Model.Database import *
from datetime import datetime
    
# HR can choose which restaurant or restaurants they want to see the sales of or they can see all of the the restaurants
# Managers can only see the sales of their own restaurants
def sales(startDate, endDate, restaurantName = None):
    conn, cur = openConnection()

    if restaurantName == None:
        query = """SELECT sum(orderPrice), restaurantName 
                FROM orders
                WHERE orders.startTime BETWEEN (?) AND (?) AND status = "Delivered"
                GROUP by orders.restaurantName;"""
        cur.execute(query, (startDate, endDate))

    elif type(restaurantName) == str:
        query = """SELECT sum(orderPrice), restaurantName 
                FROM orders
                WHERE orders.startTime BETWEEN (?) AND (?) AND orders.restaurantName = (?) AND status = "Delivered"
                GROUP by orders.restaurantName;"""
        cur.execute(query, (startDate, endDate, restaurantName))


    else:
        values = [startDate, endDate, restaurantName[0]]

        query = """SELECT sum(orderPrice), restaurantName 
                FROM orders
                WHERE orders.startTime BETWEEN (?) AND (?) AND status = "Delivered" AND (orders.restaurantName = (?)"""
        
        for name in range(1, len(restaurantName)):
            query += " OR orders.restaurantName = (?)"
            values.append(restaurantName[name])

        query += """) GROUP by orders.restaurantName;"""

        cur.execute(query, tuple(values))

    records = []
    

    rows = cur.fetchall()

    for row in rows:
        records.append([round(row[0], 2), row[1]])

    
    conn.close()

    return records

# HR can choose which restaurant they want to see the averageSales of or they can see all of the the restaurants
# Managers can only see the averageSales of their own restaurants
def averageSales(startDate, endDate, restaurantName = None):
    conn, cur = openConnection()

    if restaurantName == None:
        query = """SELECT avg(orderPrice), restaurantName 
                FROM orders
                WHERE orders.startTime BETWEEN (?) AND (?) AND status = "Delivered"
                GROUP by orders.restaurantName;"""
        cur.execute(query, (startDate, endDate))

    elif type(restaurantName) == str:
        query = """SELECT avg(orderPrice), restaurantName 
                FROM orders
                WHERE orders.startTime BETWEEN (?) AND (?) AND orders.restaurantName = (?) AND status = "Delivered"
                GROUP by orders.restaurantName;"""
        cur.execute(query, (startDate, endDate, restaurantName))

    else:
        values = [startDate, endDate, restaurantName[0]]

        query = """SELECT avg(orderPrice), restaurantName 
                FROM orders 
                WHERE orders.startTime BETWEEN (?) AND (?)  AND status = "Delivered" AND (orders.restaurantName = (?)"""
        
        for name in range(1, len(restaurantName)):
            query += " OR orders.restaurantName = (?)"
            values.append(restaurantName[name])

        query += """) GROUP by orders.restaurantName;"""

        cur.execute(query, tuple(values))
        

    

    records = []
    

    rows = cur.fetchall()

    for row in rows:
        records.append([round(row[0], 2), row[1]])

    conn.close()

    return records


# HR can choose which restaurant they want to see the averageServingTime of or they can see all of the the restaurants
# Managers can only see the averageServingTime of their own restaurants
def averageServingTime(startDate, endDate, restaurantName = None):
    conn, cur = openConnection()

    if restaurantName == None:
        query = """SELECT avg(julianday(orders.readyTime) - julianday(orders.startTime)), restaurantName
                FROM orders 
                WHERE orders.startTime BETWEEN (?) AND (?)
                GROUP by orders.restaurantName;"""
        cur.execute(query, (startDate, endDate))

    elif type(restaurantName) == str:
        query = """SELECT avg(julianday(orders.readyTime) - julianday(orders.startTime)), restaurantName
                FROM orders
                WHERE orders.startTime BETWEEN (?) AND (?) AND orders.restaurantName = (?)
                GROUP by orders.restaurantName;"""
        cur.execute(query, (startDate, endDate, restaurantName))

    else:
        values = [startDate, endDate, restaurantName[0]]

        query = """SELECT avg(julianday(orders.readyTime) - julianday(orders.startTime)), restaurantName
                FROM orders 
                WHERE orders.startTime BETWEEN (?) AND (?) AND (orders.restaurantName = (?)"""
        
        for name in range(1, len(restaurantName)):
            query += " OR orders.restaurantName = (?)"
            values.append(restaurantName[name])

        query += """) GROUP by orders.restaurantName;"""

        cur.execute(query, tuple(values))

    records = cur.fetchall()

    records = [(round((record[0] * 24 * 60), 1), record[1]) for record in records] 


    conn.close()
    return records

def verifyStartBehindEnd(startDate, endDate):
    format = "%Y-%m-%d"
    if datetime.strptime(startDate, format) < datetime.strptime(endDate, format):
        return 1
    else:
        return 0
    

def totalDiscountAmount(startDate, endDate, restaurantName = None):
    conn, cur = openConnection()

    if restaurantName == None:
        query = """SELECT sum(orderPrice - (orderPrice * (discountValue / 100))), restaurantName
                FROM orders JOIN discounts JOIN discountList
                WHERE orders.orderID = discountList.orderID AND discounts.discountID = discountList.discountID AND orders.startTime BETWEEN (?) AND (?) AND status = "Delivered"
                GROUP by orders.restaurantName;"""
        cur.execute(query, (startDate, endDate))

    elif type(restaurantName) == str:
        query = """SELECT sum(orderPrice - (orderPrice * (discountValue / 100))), restaurantName
                FROM orders JOIN discounts JOIN discountList
                WHERE orders.orderID = discountList.orderID AND discounts.discountID = discountList.discountID AND orders.startTime BETWEEN (?) AND (?) AND orders.restaurantName = (?) AND status = "Delivered"
                GROUP by orders.restaurantName;"""
        cur.execute(query, (startDate, endDate, restaurantName))

    else:
        values = [startDate, endDate, restaurantName[0]]

        query = """SELECT sum(orderPrice - (orderPrice * (discountValue / 100))), restaurantName
                FROM orders JOIN discounts JOIN discountList
                WHERE orders.orderID = discountList.orderID AND discounts.discountID = discountList.discountID AND orders.startTime AND status = "Delivered" AND BETWEEN (?) AND (?)
                AND (orders.restaurantName = (?)"""
        
        for name in range(1, len(restaurantName)):
            query += " OR orders.restaurantName = (?)"
            values.append(restaurantName[name])

        query += """) GROUP by orders.restaurantName;"""

        cur.execute(query, tuple(values))

    records = []
    

    rows = cur.fetchall()

    for row in rows:
        records.append([round(row[0], 2), row[1]])          

    conn.close()
    return records


def averageDiscountAmount(startDate, endDate, restaurantName = None):
    conn, cur = openConnection()


    if restaurantName == None:
        query = """SELECT avg(orderPrice - (orderPrice * (discountValue / 100))), restaurantName
                FROM orders JOIN discounts JOIN discountList
                WHERE orders.orderID = discountList.orderID AND discounts.discountID = discountList.discountID AND orders.startTime BETWEEN (?) AND (?) AND status = "Delivered"
                GROUP by orders.restaurantName;"""
        cur.execute(query, (startDate, endDate))

    elif type(restaurantName) == str:
        query = """SELECT avg(orderPrice - (orderPrice * (discountValue / 100))), restaurantName
                FROM orders JOIN discounts JOIN discountList
                WHERE orders.orderID = discountList.orderID AND discounts.discountID = discountList.discountID AND orders.startTime BETWEEN (?) AND (?) AND orders.restaurantName = (?) AND status = "Delivered"
                GROUP by orders.restaurantName;"""
        cur.execute(query, (startDate, endDate, restaurantName))

    else:
        values = [startDate, endDate, restaurantName[0]]

        query = """SELECT avg(orderPrice - (orderPrice * (discountValue / 100))), restaurantName
                FROM orders JOIN discounts JOIN discountList
                WHERE orders.orderID = discountList.orderID AND discounts.discountID = discountList.discountID AND orders.startTime BETWEEN (?) AND (?)
                AND status = "Delivered" AND (orders.restaurantName = (?)"""
        
        for name in range(1, len(restaurantName)):
            query += " OR orders.restaurantName = (?)"
            values.append(restaurantName[name])

        query += """) GROUP by orders.restaurantName;"""

        cur.execute(query, tuple(values))

    records = []
    

    rows = cur.fetchall()

    for row in rows:
        records.append([round(row[0], 2), row[1]])          


    conn.close()
    return records