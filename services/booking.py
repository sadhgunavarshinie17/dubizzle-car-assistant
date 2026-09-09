from datetime import datetime
from services.memory import get_connection
from services.inventory import load_inventory

def initialize_bookings():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            listing_id INTEGER NOT NULL,
            booking_date TEXT NOT NULL,
            booking_time TEXT NOT NULL,
            name TEXT,
            contact TEXT,
            status TEXT DEFAULT 'confirmed',

            UNIQUE(booking_date, booking_time)
        )
    """)

    connection.commit()
    connection.close()


def validate_slot(booking_date, booking_time):
    try:
        date = datetime.strptime(booking_date, "%Y-%m-%d")
        time = datetime.strptime(booking_time, "%H:%M").time()

    except ValueError:
        return False, "Invalid date or time format."

    #Monday = 0, Sunday = 6
    if date.weekday() == 6:
        return False, "Viewings are only available Monday to Saturday."

    if time.hour < 8 or time.hour > 20:
        return False, "Viewings are available between 8:00 AM and 8:00 PM."

    if time.minute not in [0, 30]:
        return False, "Viewing times must be on the hour or half-hour."

    return True, None


def listing_exists(listing_id):
    df = load_inventory()
    return listing_id in df["Listing_ID"].values


def book_viewing(user_id, listing_id, booking_date, booking_time, name=None, contact=None):
    #Validate listing
    if not listing_exists(listing_id):
        return {"success": False, "message": f"Listing ID {listing_id} does not exist."}

    # Validate date/time
    valid, error = validate_slot(booking_date, booking_time)

    if not valid:
        return {"success": False, "message": error}

    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO bookings
            (
                user_id,
                listing_id,
                booking_date,
                booking_time,
                name,
                contact
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                listing_id,
                booking_date,
                booking_time,
                name,
                contact
            )
        )

        connection.commit()

        return {
            "succes": True,
            "message": "Viewing booked successfully",
            "booking": {
                "listing_id": listing_id,
                "date": booking_date,
                "time": booking_time,
                "name": name,
                "contact": contact
            }


        }

    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            return {
                "success": False,
                "message": "That viewing slot is already booked."
            }

        return {
            "success": False,
            "message": "Unable to creat the booking."
        }
    
    finally:
        connection.close()

def get_bookings(user_id=None):
    connection = get_connection()

    if user_id:
        rows = connection.execute(
            """
            SELECT
                id,
                user_id,
                listing_id,
                booking_date,
                booking_time,
                name,
                contact,
                status
            FROM bookings
            WHERE user_id = ?
            ORDER BY booking_date, booking_time
            """,
            (user_id,)
        ).fetchall()

    else:
        rows = connection.execute(
            """
            SELECT
                id,
                user_id,
                listing_id,
                booking_date,
                booking_time,
                name,
                contact,
                status
            FROM bookings
            ORDER BY booking_date, booking_time
            """
        ).fetchall()

    connection.close()

    return rows