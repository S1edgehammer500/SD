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
            (itemName varchar(200) NOT NULL PRIMARY KEY, quantity INT NOT NULL,
           stockLimit INT NOT NULL)         
            ''')
            conn.commit()
            print("Table 'item' created successfully")

        conn.close()
    except Exception as e:
        print("Error creating/checking 'item' table:", e)
create_item_table()


