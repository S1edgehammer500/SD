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
            (menuID INTEGER PRIMARY KEY AUTOINCREMENT, restaurantName varchar(200) NOT NULL, foodName varchar(200) NOT NULL, isAvailable BOOL NOT NULL,
           FOREIGN KEY (restaurantName) REFERENCES restaurant(restaurantName) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY (foodName) REFERENCES food(foodName) ON DELETE CASCADE ON UPDATE CASCADE)
            ''')
            conn.commit()
            print("Table 'menu' created successfully")

        conn.close()
    except Exception as e:
        print("Error creating/checking 'menu' table:", e)
create_menu_table()



