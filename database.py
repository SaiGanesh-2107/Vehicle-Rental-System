import sqlite3


def create_database():

    connection = sqlite3.connect("vehicle_rental.db")

    cursor = connection.cursor()

    # Vehicles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            vehicle_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            status TEXT NOT NULL,
            vehicle_type TEXT NOT NULL,
            extra INTEGER
        )
    """)

    # Customers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rentals (
            rental_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            vehicle_id INTEGER NOT NULL,
            days INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            return_date TEXT NOT NULL,
            status TEXT NOT NULL,
            payment_status TEXT NOT NULL,
            fine REAL DEFAULT 0
        )
    """)

    connection.commit()

    connection.close()

    print("Database Created Successfully")

def add_fine_payment_column():

    connection = sqlite3.connect("vehicle_rental.db")
    cursor = connection.cursor()

    cursor.execute("PRAGMA table_info(rentals)")

    columns = [row[1] for row in cursor.fetchall()]

    if "fine_payment_status" not in columns:

        cursor.execute("""
            ALTER TABLE rentals
            ADD COLUMN fine_payment_status TEXT
            DEFAULT 'Not Applicable'
        """)

    connection.commit()
    connection.close()

def add_actual_return_date_column():

    connection = sqlite3.connect("vehicle_rental.db")
    cursor = connection.cursor()

    cursor.execute("PRAGMA table_info(rentals)")

    columns = [row[1] for row in cursor.fetchall()]

    if "actual_return_date" not in columns:

        cursor.execute("""
            ALTER TABLE rentals
            ADD COLUMN actual_return_date TEXT
        """)

        print("actual_return_date column added")

    else:
        print("actual_return_date column already exists")

    connection.commit()
    connection.close()

def add_payment_method_column():

    connection = sqlite3.connect("vehicle_rental.db")

    cursor = connection.cursor()

    cursor.execute("PRAGMA table_info(rentals)")

    columns = [row[1] for row in cursor.fetchall()]

    if "payment_method" not in columns:

        cursor.execute("""
            ALTER TABLE rentals
            ADD COLUMN payment_method TEXT
        """)

        print("payment_method column added")

    connection.commit()

    connection.close()


create_database()
add_fine_payment_column()
add_actual_return_date_column()
add_payment_method_column()
