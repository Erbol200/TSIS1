import psycopg2
import csv

conn = psycopg2.connect(
    host="localhost",
    database="phonebook_db",
    user="postgres",
    password="12341"
)

cur = conn.cursor()

# создаем таблицу
cur.execute("""
CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(20)
)
""")
conn.commit()

print("1. Add contact")
print("2. Show all")
print("3. Update")
print("4. Delete")
print("5. Import CSV")

choice = input("Choose: ")

if choice == "1":
    name = input("Name: ")
    phone = input("Phone: ")
    cur.execute(
        "INSERT INTO contacts (name, phone) VALUES (%s, %s)",
        (name, phone)
    )
    conn.commit()
    print("Added!")

elif choice == "2":
    cur.execute("SELECT * FROM contacts")
    rows = cur.fetchall()
    for row in rows:
        print(row)

elif choice == "3":
    name = input("Enter name to update: ")
    new_phone = input("New phone: ")
    cur.execute(
        "UPDATE contacts SET phone=%s WHERE name=%s",
        (new_phone, name)
    )
    conn.commit()
    print("Updated!")

elif choice == "4":
    name = input("Enter name to delete: ")
    cur.execute(
        "DELETE FROM contacts WHERE name=%s",
        (name,)
    )
    conn.commit()
    print("Deleted!")

elif choice == "5":
    with open("contacts.csv", "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            cur.execute(
                "INSERT INTO contacts (name, phone) VALUES (%s, %s)",
                (row[0], row[1])
            )
    conn.commit()
    print("CSV imported!")

cur.close()
conn.close()