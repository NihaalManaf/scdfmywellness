import sqlite3
from Main import NRICparser

conn = sqlite3.connect('Userbase.db')
cursor = conn.cursor()

# #create table for users

# cursor.execute("""
               
#                CREATE TABLE user_accounts (
#                user_ic CHAR(4),
#                enlist_date DATE,
#                tele_id VARCHAR(15),
#                login_status BOOLEAN DEFAULT false,
#                password VARCHAR(20),
#                intake VARCHAR(7)
#                )
               
#                """)

# cursor.execute("""
               
#                CREATE TABLE pass (
#                password VARCHAR(20)
#                )
               
#                """)

# cursor.execute(f"""
#                     INSERT INTO pass (password) VALUES ('SCDF2413');
#                 """)

# cursor.execute("""
               
#                CREATE TABLE eoc (
#                date DATE,
#                intake VARCHAR(7),
#                query VARCHAR(100),
#                response VARCHAR(100)
#                )
               
#                """)





print("Printing user accounts")

cursor.execute("""
    SELECT * FROM user_accounts
""")

results = cursor.fetchall()
for row in results:
    print(row)


print("Printing default password")

cursor.execute("""
    SELECT * FROM pass;
""")

results = cursor.fetchall()
for row in results:
    print(row)

print("printing eoc db")
cursor.execute("""
    SELECT * FROM eoc;
""")

results = cursor.fetchall()
for row in results:
    print(row)



conn.commit()
conn.close()