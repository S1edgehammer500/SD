import re
from Model.Database import *


conn, cur = openConnection()

query = """SELECT avg(orderPrice - (orderPrice * (discountValue / 100))), restaurantName
                FROM orders JOIN discounts JOIN discountList
                WHERE orders.orderID = discountList.orderID AND discounts.discountID = discountList.discountID AND orders.startTime BETWEEN (?) AND (?)
                GROUP by orders.restaurantName;"""

cur.execute(query, ("2024-01-01", "2024-01-31"))

records = []
    

rows = cur.fetchall()

for row in rows:
    records.append([round(row[0], 2), row[1]])

conn.close()

print(records)