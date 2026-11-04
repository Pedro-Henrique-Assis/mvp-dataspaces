from app.database import get_connection


def list_active():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, name, did FROM organizations "
            "WHERE status = 'active' ORDER BY name"
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def get_by_id(organization_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM organizations WHERE id = %s", (organization_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()


def get_by_email(email):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM organizations WHERE email = %s", (email,))
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()
