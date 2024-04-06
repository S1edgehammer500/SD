# 22013740 Luqmaan Abdullahi
# 22025153 Andre Barnett
# 22018158 Jake Tovey
# 22016129 Plamen Tyufekchiev
# 22062013 Serhii Mistota
from Model.Database import * 
conn, cur = openConnection()
def create_restaurant_table():
    try:
        c = conn.cursor()
        ('''SELECT name FROM sqlite_master WHERE type='table' AND name='restaurant'
        ''')
        table_exists = c.fetchone()

        if table_exists:
            print("Table 'restaurant' already exists")
        else:
            c.execute('''
            CREATE TABLE restaurant
            (restaurantID INTEGER PRIMARY KEY AUTOINCREMENT, restaurantName varchar(200) NOT NULL, numberOfTables INTEGER NOT NULL)
            ''')
            conn.commit()
            print("Table 'restaurant' created successfully")

        conn.close()
    except Exception as e:
        print("Error creating/checking 'restaurant' table:", e)
create_restaurant_table()


