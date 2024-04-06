# 22013740 Luqmaan Abdullahi
# 22025153 Andre Barnett
# 22018158 Jake Tovey
# 22016129 Plamen Tyufekchiev
# 22062013 Serhii Mistota
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
            (inventoryID INTEGER PRIMARY KEY AUTOINCREMENT, restaurantID INT NOT NULL UNIQUE, itemID INT NOT NULL UNIQUE,
           FOREIGN KEY (restaurantID) REFERENCES restaurant(restaurantID) ON DELETE CASCADE, FOREIGN KEY (itemID) REFERENCES item(itemID) ON DELETE CASCADE)
            ''')
            conn.commit()
            print("Table 'inventory' created successfully")

        conn.close()
    except Exception as e:
        print("Error creating/checking 'inventory' table:", e)
create_inventory_table()
