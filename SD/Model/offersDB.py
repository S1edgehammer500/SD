from Model.Database import * 
conn, cur = openConnection()
def create_offer_table():
    try:
        c = conn.cursor()
        ('''SELECT name FROM sqlite_master WHERE type='table' AND name='offer'
        ''')
        table_exists = c.fetchone()

        if table_exists:
            print("Table 'offer' already exists")
        else:
            c.execute('''
            CREATE TABLE offer
            (offerID INTEGER PRIMARY KEY AUTOINCREMENT, offerDescription varchar(200) NOT NULL)
            ''')
            conn.commit()
            print("Table 'offer' created successfully")

        conn.close()
    except Exception as e:
        print("Error creating/checking 'offer' table:", e)
create_offer_table()
