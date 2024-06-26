from Model.Database import * 
conn, cur = openConnection()
def create_reservation_table():
    try:
        c = conn.cursor()
        ('''SELECT name FROM sqlite_master WHERE type='table' AND name='reservation'
        ''')
        table_exists = c.fetchone()

        if table_exists:
            print("Table 'reservation' already exists")
        else:
            c.execute('''
            CREATE TABLE reservation
            (reservationID INTEGER PRIMARY KEY AUTOINCREMENT, restaurantName varchar(200) NOT NULL, tables STRING NOT NULL,
           startTime DATETIME NOT NULL, endTime DATETIME NOT NULL, Name	varchar(200) NOT NULL,
             FOREIGN KEY (restaurantName) REFERENCES restaurant(restaurantName) ON DELETE CASCADE ON UPDATE CASCADE)
            ''')
            conn.commit()
            print("Table 'reservation' created successfully")

        conn.close()
    except Exception as e:
        print("Error creating/checking 'reservation' table:", e)
create_reservation_table()


