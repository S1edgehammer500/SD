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
            (restaurantName varchar(200) NOT NULL PRIMARY KEY, numberOfTables INTEGER NOT NULL)
            ''')
            conn.commit()
            print("Table 'restaurant' created successfully")

        conn.close()
    except Exception as e:
        print("Error creating/checking 'restaurant' table:", e)
create_restaurant_table()


