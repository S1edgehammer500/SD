# 22013740 Luqmaan Abdullahi
# 22025153 Andre Barnett
# 22018158 Jake Tovey
# 22016129 Plamen Tyufekchiev
# 22062013 Serhii Mistota

from Model.Database import *
conn, cur = openConnection()

def create_discounts_table():
    try:
        c = conn.cursor()

        # Check if table exists
        c.execute('''
        SELECT name FROM sqlite_master WHERE type='table' AND name='discounts'
        ''')
        table_exists = c.fetchone()

        if table_exists:
            print("Table 'discounts' already exists")
        else:
            c.execute(''' 
            CREATE TABLE discounts
            (discountID INTEGER PRIMARY KEY AUTOINCREMENT, discountValue INT NOT NULL)
            ''')
            conn.commit()
            print("Table 'discounts' created successfully")

        conn.close()
    except Exception as e:
        print("Error creating/checking table:", e)

create_discounts_table()