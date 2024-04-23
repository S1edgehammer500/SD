from Database import *
from passlib.hash import sha256_crypt
import random as ran
import datetime as dt

conn, cur = openConnection()


# Restaurant Data
values = ["Bristol", "12", "Cardiff", "17", "Birmingham", "56", "Newcastle", "20", "Manchester", "25", "Liverpool", "99"]

for x in range(0, len(values), 2):
    query = """INSERT INTO restaurant (restaurantName, numberOfTables)
VALUES (?, ?)"""
    cur.execute(query, (values[x], values[x+1]))

# Users Data
values = ["Luqmaan", "Somalia", "chef", "Bristol", "Jake", "England", "admin", "Bristol", "Serhii", "Ukraine", "admin", "Liverpool", "Plamen", "Bulgaria", "manager", "Liverpool", "Andre", "Jamaica", "admin", "Cardiff", "Olanrewaju", "Nigeria", "staff", "Cardiff"]

for x in range(0, len(values), 4):
    query = """INSERT INTO users (employeeCode, password, authorisationLevel, baseRestaurant)
VALUES (?, ?, ?, ?);"""
    cur.execute(query, (values[x], sha256_crypt.hash(values[x+1]), values[x+2], values[x+3]))




# Food Data
food = ["Sushi", "Steak", "Pasta", "Salad", "Tacos", "Sushi Rolls", "Chicken Wings", "Ribs", "Soup", "Sandwiches", "Curry", "Seafood Platter", "Desserts", "Stir-Fry", "Dim Sum", "Nachos", "Pho", "Paella"]

allergyInfo = ["Milk", "Soy", "Shellfish", "Nut", "Eggs", "Wheat"]

for x in range(len(food)):
    query = """INSERT INTO food (foodName, price, allergyInfo)
VALUES (?, ?, ?);"""
    cur.execute(query, (food[x], round(ran.uniform(10,30), 2), ran.choice(allergyInfo)))

# Discount Data
discounts = [10, 25, 50, 75]

for discount in discounts:
    query = """INSERT INTO discounts (discountValue)
VALUES (?);"""
    cur.execute(query, (discount,))

# Orders Data
numOfOrders = 200

def generate_random_dates(start_date, end_date, k):
    random_dates = []
    for _ in range(k):
        random_date = start_date + dt.timedelta(days=ran.randint(0, (end_date - start_date).days),
                                                hours=ran.randint(18, 23),
                                                minutes=ran.randint(0, 59),
                                                seconds=ran.randint(0, 59))
        random_dates.append(random_date)
    return random_dates

def generate_ready_times(order_dates):
    ready_times = [date + dt.timedelta(minutes=ran.randint(15, 60)) for date in order_dates]
    return ready_times

before_start_date = dt.datetime(2024, 1, 1)
before_end_date = dt.datetime(2024, 4, 17)
before_dates = generate_random_dates(before_start_date, before_end_date, numOfOrders)
before_readyTime = generate_ready_times(before_dates)

start_date = dt.datetime.strptime(dt.datetime.strftime(dt.datetime.today().date(), "%Y-%m-%d  %H:%M:%S"), "%Y-%m-%d  %H:%M:%S")
end_date = start_date + dt.timedelta(days=1)
now_dates = generate_random_dates(start_date, end_date, 10)
readyTime = generate_ready_times(now_dates)


before_statuses = ['Delivered']
statuses = ['Order Created','Cooking', 'Ready', 'Delivered']



def generate_orders(start, numOfOrders, dates, readyTime, statuses, food, discounts):
    for restaurant in ["Bristol"]:
        for x in range(start, numOfOrders):
            singleOrder = x + start
            totalPrice = 0.0
            totalDiscount = 0
            dateToPick = ran.randint(0, len(dates) - 1)

            #print(singleOrder, restaurant, ran.choice(statuses), totalPrice, ran.randint(1,12), random_dates[x], readyTime[x])


            query = """INSERT INTO orders (orderID, restaurantName, status, orderPrice, tableNumber, startTime, readyTime)
        VALUES (?, ?, ?, ?, ?, ?, ?);"""
            cur.execute(query, (singleOrder, restaurant, ran.choice(statuses), totalPrice, ran.randint(1,12), dates[dateToPick], readyTime[dateToPick]))

            #print(dates[ran.randint(0, len(dates) - 1)], readyTime[ran.randint(0, len(readyTime) -1 )])

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


            for z in range(ran.randint(1,2)):
                if totalDiscount < 50:
                    singleDiscount = ran.choice(discounts)

                    query = "SELECT discountID FROM discounts WHERE discountValue = ?;"
                    cur.execute(query, (singleDiscount,))
                    records = cur.fetchone()

                    totalDiscount += singleDiscount

                    # Foodlist Data
                    query = """INSERT INTO discountList (orderID, discountID)
                VALUES (?, ?);"""
                    cur.execute(query, (singleOrder, records[0]))

                    

            totalPrice = totalPrice - (totalPrice * (totalDiscount / 100))

            query = "UPDATE orders SET orderPrice = ? WHERE orderID = ?;"
            cur.execute(query, (round(totalPrice, 2), singleOrder))
            


generate_orders(2, numOfOrders, before_dates, before_readyTime, before_statuses, food, discounts)
generate_orders(numOfOrders + 1, numOfOrders + 10, now_dates, readyTime, statuses, food, discounts)


conn.commit()
conn.close()
