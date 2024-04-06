# 22013740 Luqmaan Abdullahi
# 22025153 Andre Barnett
# 22018158 Jake Tovey
# 22016129 Plamen Tyufekchiev
# 22062013 Serhii Mistota

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
                      FOREIGN KEY (orderID) REFERENCES orders(orderID) ON DELETE CASCADE, FOREIGN KEY (discountID) REFERENCES discounts(discountID) ON DELETE CASCADE)
            ''')
            conn.commit()
            print("Table 'discountList' created successfully")

        conn.close()
    except Exception as e:
        print("Error creating/checking 'discountList' table:", e)
create_discountList_table()
