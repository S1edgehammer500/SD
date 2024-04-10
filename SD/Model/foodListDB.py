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
                      FOREIGN KEY (orderID) REFERENCES orders(orderID) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY (foodID) REFERENCES food(foodID) ON DELETE CASCADE ON UPDATE CASCADE)
            ''')
            conn.commit()
            print("Table 'foodList' created successfully")

        conn.close()
    except Exception as e:
        print("Error creating/checking 'foodList' table:", e)
create_foodList_table()
