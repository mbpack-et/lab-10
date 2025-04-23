import psycopg2
import csv

# Подключени к БД
def get_connection():
    return psycopg2.connect(
        dbname="your_db_name",
        user="your_user",
        password="your_password",
        host="localhost",
        port="5432"
    )

# Создание таблицы
def create_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS PhoneBook (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            phone VARCHAR(20)
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# Вставка из CSV
def insert_from_csv(path):
    conn = get_connection()
    cur = conn.cursor()
    with open(path, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            cur.execute("INSERT INTO PhoneBook (name, phone) VALUES (%s, %s)", (row[0], row[1]))
    conn.commit()
    cur.close()
    conn.close()

# Вставка из консоли
def insert_from_console():
    conn = get_connection()
    cur = conn.cursor()
    name = input("Enter name: ")
    phone = input("Enter phone: ")
    cur.execute("INSERT INTO PhoneBook (name, phone) VALUES (%s, %s)", (name, phone))
    conn.commit()
    cur.close()
    conn.close()

# Обновление номера телефона
def update_phone(name, new_phone):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE PhoneBook SET phone = %s WHERE name = %s", (new_phone, name))
    conn.commit()
    cur.close()
    conn.close()

# Поиск по имени
def search_by_name(name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM PhoneBook WHERE name = %s", (name,))
    rows = cur.fetchall()
    for row in rows:
        print(row)
    cur.close()
    conn.close()

# Удаление по имени
def delete_by_name(name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM PhoneBook WHERE name = %s", (name,))
    conn.commit()
    cur.close()
    conn.close()

# Меню
def menu():
    create_table()
    while True:
        print("\nPhoneBook Menu:")
        print("1 - Insert from CSV")
        print("2 - Insert from console")
        print("3 - Update phone")
        print("4 - Search by name")
        print("5 - Delete by name")
        print("0 - Exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            path = input("Enter path to CSV: ")
            insert_from_csv(path)
        elif choice == "2":
            insert_from_console()
        elif choice == "3":
            name = input("Enter name to update: ")
            new_phone = input("Enter new phone: ")
            update_phone(name, new_phone)
        elif choice == "4":
            name = input("Enter name to search: ")
            search_by_name(name)
        elif choice == "5":
            name = input("Enter name to delete: ")
            delete_by_name(name)
        elif choice == "0":
            break
        else:
            print("Invalid choice.")

# Запуск
if __name__ == "__main__":
    menu()