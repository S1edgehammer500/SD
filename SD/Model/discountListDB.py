from Model.Database import * 
conn, cur = openConnection()
def create_discountList_table():
    try:
        c = conn.cursor()
        ('''SELECT name FROM sqlite_master WHERE type='table' AND name='discountList'
        ''')
        table_exists = c.fetchone()

        if table_exists:
            print("Table 'discountList' already exists")
        else:
            c.execute('''
            CREATE TABLE discountList
            (discountListID INTEGER PRIMARY KEY AUTOINCREMENT, orderID INT NOT NULL, discountID INT NOT NULL,
                      FOREIGN KEY (orderID) REFERENCES orders(orderID) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY (discountID) REFERENCES discounts(discountID) ON DELETE CASCADE ON UPDATE CASCADE)
            ''')
            conn.commit()
            print("Table 'discountList' created successfully")

        conn.close()
    except Exception as e:
        print("Error creating/checking 'discountList' table:", e)
create_discountList_table()
