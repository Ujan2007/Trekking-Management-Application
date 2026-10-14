import sqlite3
from werkzeug.security import generate_password_hash

def db():
    conn = sqlite3.connect("database.db")
    conn.execute("PRAGMA foreign_keys = ON") #Enabling foreign keys
    cursor = conn.cursor()

    #admin table 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        admin_id INTEGER PRIMARY KEY CHECK (admin_id = 1),
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
""")

    # staff table 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS staff (
        staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        phone TEXT,
        status TEXT NOT NULL DEFAULT 'active'
            CHECK (status IN ('active', 'inactive', 'blacklisted'))
    )
""")

    #users table 

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active'
            CHECK (status IN ('active', 'inactive', 'blacklisted'))
    )
""")

    #trek table 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS treks (
        trek_id INTEGER PRIMARY KEY AUTOINCREMENT,
        trek_name TEXT NOT NULL,
        location TEXT NOT NULL,

        difficulty TEXT NOT NULL
            CHECK (difficulty IN ('Easy', 'Moderate', 'Hard')),

        duration INTEGER NOT NULL
            CHECK (duration > 0),

        total_slots INTEGER NOT NULL
            CHECK (total_slots >= 0),

        available_slots INTEGER NOT NULL
            CHECK (
                available_slots >= 0
                AND available_slots <= total_slots
            ),

        assigned_staff_id INTEGER,

        status TEXT NOT NULL DEFAULT 'Pending'
            CHECK (
                status IN (
                    'Pending',
                    'Approved',
                    'Open',
                    'Closed',
                    'Completed'
                )
            ),

        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,

        CHECK (end_date >= start_date),

        FOREIGN KEY (assigned_staff_id)
            REFERENCES staff(staff_id)
    )
""")

    #bookings table 
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,
            trek_id INTEGER NOT NULL,

            booking_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

            status TEXT NOT NULL DEFAULT 'Booked'
                CHECK (
                    status IN ('Booked', 'Cancelled', 'Completed')
                ),

            FOREIGN KEY (user_id)
                REFERENCES users(user_id),

            FOREIGN KEY (trek_id)
                REFERENCES treks(trek_id)
        )
    """)

    cursor.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS unique_active_booking
    ON bookings(user_id, trek_id)
    WHERE status = 'Booked'
""")

    # Inserting default admin

    admin_email = "admin@gmail.com"
    admin_password = "admin123"  
    hashed_password = generate_password_hash(admin_password) #extraaaaaa security :D

    cursor.execute("""
            INSERT OR IGNORE INTO admin (email, password_hash)
            VALUES (?, ?)
        """, (admin_email, hashed_password))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    db()
    print("Database initialized successfully!")
