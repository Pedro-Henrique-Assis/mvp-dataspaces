from app.database import get_connection


def get_for_organization(organization_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM verifiable_credentials "
            "WHERE organization_id = %s ORDER BY id DESC LIMIT 1",
            (organization_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()