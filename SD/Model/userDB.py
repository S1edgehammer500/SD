from Model.Database import * 
conn, cur = openConnection()
def create_user_table():
    try:
        c = conn.cursor()
        ('''SELECT name FROM sqlite_master WHERE type='table' AND name='user'
        ''')
        table_exists = c.fetchone()

        if table_exists:
            print("Table 'user' already exists")
        else:
            c.execute('''
            CREATE TABLE users
            (employeeCode varchar(20) NOT NULL, password varchar(100) NOT NULL, authorisationLevel varchar(20) NOT NULL,
           baseRestaurant varchar(200) NOT NULL, PRIMARY KEY (employeeCode),  FOREIGN KEY (baseRestaurant) REFERENCES restaurant(restaurantName) ON DELETE CASCADE)
            ''')
            conn.commit()
            print("Table 'user' created successfully")

        conn.close()
    except Exception as e:
        print("Error creating/checking 'user' table:", e)
create_user_table()




