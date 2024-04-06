# 22013740 Luqmaan Abdullahi
# 22025153 Andre Barnett
# 22018158 Jake Tovey
# 22016129 Plamen Tyufekchiev
# 22062013 Serhii Mistota
from Model.Database import * 
conn, cur = openConnection()
def create_food_table():
    try:
        c = conn.cursor()
        ('''SELECT name FROM sqlite_master WHERE type='table' AND name='food'
        ''')
        table_exists = c.fetchone()

        if table_exists:
            print("Table 'food' already exists")
        else:
            c.execute('''
            CREATE TABLE food
            (foodID INTEGER PRIMARY KEY AUTOINCREMENT, price FLOAT NOT NULL, name varchar(200) NOT NULL,
            isAvailable BOOL NOT NULL, allergyInfo varchar(1000) NOT NULL)
            ''')
            conn.commit()
            print("Table 'food' created successfully")

        conn.close()
    except Exception as e:
        print("Error creating/checking 'food' table:", e)
create_food_table()
