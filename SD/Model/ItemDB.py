# 22013740 Luqmaan Abdullahi
# 22025153 Andre Barnett
# 22018158 Jake Tovey
# 22016129 Plamen Tyufekchiev
# 22062013 Serhii Mistota
from Model.Database import * 
conn, cur = openConnection()
def create_item_table():
    try:
        c = conn.cursor()
        ('''SELECT name FROM sqlite_master WHERE type='table' AND name='item'
        ''')
        table_exists = c.fetchone()

        if table_exists:
            print("Table 'item' already exists")
        else:
            c.execute('''
            CREATE TABLE item
            (itemID INTEGER PRIMARY KEY AUTOINCREMENT, quantity INT NOT NULL, name varchar(200) NOT NULL,
           stockLimit INT NOT NULL)         
            ''')
            conn.commit()
            print("Table 'item' created successfully")

        conn.close()
    except Exception as e:
        print("Error creating/checking 'item' table:", e)
create_item_table()


