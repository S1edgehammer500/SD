from Model.Database import * 
conn, cur = openConnection()
def create_orders_table():
    try:
        c = conn.cursor()
        ('''SELECT name FROM sqlite_master WHERE type='table' AND name='orders'
        ''')
        table_exists = c.fetchone()

        if table_exists:
            print("Table 'orders' already exists")
        else:
            c.execute('''
                    CREATE TABLE IF NOT EXISTS orders (
            restaurantName varchar(200) NOT NULL,
            orderID INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT NOT NULL,
            orderPrice FLOAT NOT NULL,
            tableNumber INT NOT NULL,
            startTime DATETIME NOT NULL,
            readyTime DATETIME NOT NULL,
            FOREIGN KEY (restaurantName) REFERENCES restaurant(restaurantName) ON DELETE CASCADE ON UPDATE CASCADE)
            ''')
            conn.commit()
            print("Table 'orders' created successfully")

        conn.close()
    except Exception as e:
        print("Error creating/checking 'orders' table:", e)
create_orders_table()








