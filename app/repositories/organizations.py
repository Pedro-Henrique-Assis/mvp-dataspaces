from app.database import get_connection


def list_active():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, name, did FROM organizations "
            "WHERE active = TRUE ORDER BY name"
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def get_by_id(organization_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, name, did, active FROM organizations WHERE id = %s",
            (organization_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()