from Model.Database import * 
conn, cur = openConnection()
def create_inventory_table():
    try:
        c = conn.cursor()
        ('''SELECT name FROM sqlite_master WHERE type='table' AND name='inventory'
        ''')
        table_exists = c.fetchone()

        if table_exists:
            print("Table 'inventory' already exists")
        else:
            c.execute('''
            CREATE TABLE inventory
            (inventoryID INTEGER PRIMARY KEY AUTOINCREMENT, restaurantName varchar(200) NOT NULL UNIQUE, itemName varchar(200) NOT NULL,
           FOREIGN KEY (restaurantName) REFERENCES restaurant(restaurantName) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY (itemName) REFERENCES item(itemName) ON DELETE CASCADE ON UPDATE CASCADE)
            ''')
            conn.commit()
            print("Table 'inventory' created successfully")

        conn.close()
    except Exception as e:
        print("Error creating/checking 'inventory' table:", e)
create_inventory_table()
