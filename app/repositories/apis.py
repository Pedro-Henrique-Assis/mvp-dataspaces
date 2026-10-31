from app.database import get_connection


def list_all():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT a.*, o.name AS provider_name "
            "FROM apis a JOIN organizations o ON o.id = a.provider_org_id "
            "ORDER BY a.name"
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def get_by_id(api_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM apis WHERE id = %s", (api_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()


def get_by_slug(slug):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM apis WHERE slug = %s", (slug,))
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()