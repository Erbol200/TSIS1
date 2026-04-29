from connect import connect

# создать таблицы + процедуры
def init_db():
    conn = connect()
    cur = conn.cursor()

    with open("schema.sql", "r") as f:
        cur.execute(f.read())

    with open("procedures.sql", "r") as f:
        cur.execute(f.read())

    conn.commit()
    cur.close()
    conn.close()
    print("DB READY")


def add_contact():
    conn = connect()
    cur = conn.cursor()

    name = input("Name: ")
    email = input("Email: ")
    birthday = input("Birthday (YYYY-MM-DD): ")
    group = input("Group: ")

    cur.execute("""
        INSERT INTO contacts(name, email, birthday)
        VALUES (%s,%s,%s)
    """, (name, email, birthday))

    conn.commit()
    cur.close()
    conn.close()
    print("Contact added")


def add_phone():
    conn = connect()
    cur = conn.cursor()

    name = input("Name: ")
    phone = input("Phone: ")
    t = input("Type: ")

    cur.execute("CALL add_phone(%s,%s,%s)", (name, phone, t))

    conn.commit()
    cur.close()
    conn.close()
    print("Phone added")


def search():
    conn = connect()
    cur = conn.cursor()

    q = input("Search: ")

    cur.execute("SELECT * FROM search_contacts(%s)", (q,))
    print(cur.fetchall())

    cur.close()
    conn.close()


def menu():
    while True:
        print("""
1 Init DB
2 Add contact
3 Add phone
4 Search
5 Exit
""")

        c = input("Choose: ")

        if c == "1":
            init_db()
        elif c == "2":
            add_contact()
        elif c == "3":
            add_phone()
        elif c == "4":
            search()
        elif c == "5":
            break


menu()