# 22013740 Luqmaan Abdullahi
# 22025153 Andre Barnett
# 22018158 Jake Tovey
# 22016129 Plamen Tyufekchiev
# 22062013 Serhii Mistota
from Model.Database import * 
conn, cur = openConnection()
def create_menu_table():
    try:
        c = conn.cursor()
        ('''SELECT name FROM sqlite_master WHERE type='table' AND name='menu'
        ''')
        table_exists = c.fetchone()

        if table_exists:
            print("Table 'menu' already exists")
        else:
            c.execute('''
            CREATE TABLE menu
            (menuID INTEGER PRIMARY KEY AUTOINCREMENT, restaurantID INT NOT NULL UNIQUE, foodID INT NOT NULL UNIQUE,
           FOREIGN KEY (restaurantID) REFERENCES restaurant(restaurantID) ON DELETE CASCADE, FOREIGN KEY (foodID) REFERENCES food(foodID) ON DELETE CASCADE)
            ''')
            conn.commit()
            print("Table 'menu' created successfully")

        conn.close()
    except Exception as e:
        print("Error creating/checking 'menu' table:", e)
create_menu_table()



