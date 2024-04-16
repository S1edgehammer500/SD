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
            (foodName varchar(200) PRIMARY KEY, price FLOAT NOT NULL, allergyInfo varchar(1000) NOT NULL)
            ''')
            conn.commit()
            print("Table 'food' created successfully")

        conn.close()
    except Exception as e:
        print("Error creating/checking 'food' table:", e)
create_food_table()
