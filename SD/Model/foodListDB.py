# 22013740 Luqmaan Abdullahi
# 22025153 Andre Barnett
# 22018158 Jake Tovey
# 22016129 Plamen Tyufekchiev
# 22062013 Serhii Mistota
from Model.Database import * 
conn, cur = openConnection()
def create_foodList_table():
    try:
        c = conn.cursor()
        ('''SELECT name FROM sqlite_master WHERE type='table' AND name='foodList'
        ''')
        table_exists = c.fetchone()

        if table_exists:
            print("Table 'foodList' already exists")
        else:
            c.execute('''
            CREATE TABLE foodList
            (foodListID INTEGER PRIMARY KEY AUTOINCREMENT, orderID INT NOT NULL, foodID INT NOT NULL,
                      FOREIGN KEY (orderID) REFERENCES orders(orderID) ON DELETE CASCADE, FOREIGN KEY (foodID) REFERENCES food(foodID) ON DELETE CASCADE)
            ''')
            conn.commit()
            print("Table 'foodList' created successfully")

        conn.close()
    except Exception as e:
        print("Error creating/checking 'foodList' table:", e)
create_foodList_table()
