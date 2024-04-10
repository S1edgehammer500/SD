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
