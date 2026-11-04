from app.database import get_connection


def get_by_email(email):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM admins WHERE email = %s", (email,))
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()


def get_by_id(admin_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM admins WHERE id = %s", (admin_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()
