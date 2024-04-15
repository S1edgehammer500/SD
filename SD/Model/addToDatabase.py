# 22013740 Luqmaan Abdullahi
# 22025153 Andre Barnett
# 22018158 Jake Tovey
# 22016129 Plamen Tyufekchiev
# 22062013 Serhii Mistota

from Database import *
from passlib.hash import sha256_crypt
import random as ran
import datetime as dt

conn, cur = openConnection()


# Food Data
food = ["Sushi", "Steak", "Pasta", "Salad", "Tacos", "Sushi Rolls", "Chicken Wings", "Ribs", "Soup", "Sandwiches", "Curry", "Seafood Platter", "Desserts", "Stir-Fry", "Dim Sum", "Nachos", "Pho", "Paella"]

allergyInfo = ["Milk", "Soy", "Shellfish", "Nut", "Eggs", "Wheat"]

for x in range(len(food)):
    query = """INSERT INTO food (foodName, price, isAvailable, allergyInfo)
VALUES (?, ?, ?, ?);"""
    cur.execute(query, (food[x], round(ran.uniform(10,30), 2), ran.randint(0,1), ran.choice(allergyInfo)))

# Orders Data
numOfOrders = 1000

def generate_random_dates(start_date, end_date, k):
    random_dates = []
    date_range = end_date - start_date
    for _ in range(k):
        random_days = ran.randint(0, date_range.days)
        random_date = start_date + dt.timedelta(seconds=ran.randint(0,60),minutes=ran.randint(0,60),hours=ran.randint(18, 23),days=random_days)
        random_dates.append(random_date)
    return random_dates
start_date = dt.datetime(2024, 1, 1)
end_date = dt.datetime(2024, 12, 31)
random_dates = generate_random_dates(start_date, end_date, numOfOrders)
readyTime = [date + dt.timedelta(minutes=ran.randint(0,60)) for date in random_dates]

statuses = ['Order Created','Cooking', 'Ready', 'Delivered', 'Payment Completed','Cancelled']

for restaurant in ["Bristol"]:
    
    for x in range(numOfOrders):
        singleOrder = x
        totalPrice = 0.0

        #print(singleOrder, restaurant, ran.choice(statuses), totalPrice, ran.randint(1,12), random_dates[x], readyTime[x])


        query = """INSERT INTO orders (orderID, restaurantName, status, orderPrice, tableNumber, startTime, readyTime)
    VALUES (?, ?, ?, ?, ?, ?, ?);"""
        cur.execute(query, (singleOrder, restaurant, ran.choice(statuses), totalPrice, ran.randint(1,12), random_dates[x], readyTime[x]))

        for y in range(ran.randint(1,5)):
            singleFood = ran.choice(food)
            # Foodlist Data
            query = """INSERT INTO foodList (orderID, foodName)
        VALUES (?, ?);"""
            cur.execute(query, (singleOrder, singleFood))

            query = "SELECT price FROM food WHERE foodName = ?;"
            cur.execute(query, (singleFood,))
            records = cur.fetchone()

            totalPrice += float(records[0])

        query = "UPDATE orders SET orderPrice = ? WHERE orderID = ?;"
        cur.execute(query, (round(totalPrice, 2), singleOrder))
        conn.commit()

        


        




# Discount Data
discounts = [10, 25, 50, 75]

for discount in discounts:
    query = """INSERT INTO discounts (discountValue)
VALUES (?);"""
    cur.execute(query, (discount,))

# DiscountList Data
discountIDs = [1,2,3,4,5,6]

for discount in range(500):
    query = """INSERT INTO discountList (orderID, discountID)
VALUES (?, ?);"""
    cur.execute(query, ( ran.randint(1,1000), ran.choice(discountIDs)))



# # Users Data
# values = ["Luqmaan", "Somalia", "chef", "1", "Jake", "England", "staff", "2", "Serhii", "Ukraine", "admin", "3", "Plamen", "Bulgaria", "manager", "4", "Andre", "Jamaica", "staff", "5"]

# for x in range(0, len(values), 4):
#     query = """INSERT INTO users (employeeCode, password, authorisationLevel, baseRestaurant)
# VALUES (?, ?, ?, ?);"""
#     cur.execute(query, (values[x], sha256_crypt.hash(values[x+1]), values[x+2], values[x+3]))


# # Restaurant Data
# values = ["Bristol", "12", "Cardiff", "17", "Birmingham", "56", "Newcastle", "20", "Manchester", "25", "Liverpool", "99"]

# for x in range(0, len(values), 2):
#     query = """INSERT INTO restaurant (restaurantName, numberOfTables)
# VALUES (?, ?)"""
#     cur.execute(query, (values[x], values[x+1]))
#     print((values[x], values[x+1]))

conn.commit()
conn.close()
