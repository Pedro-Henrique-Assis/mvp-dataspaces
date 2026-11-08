from app.database import get_connection


def list_public():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT a.*, o.name AS provider_name "
            "FROM apis a JOIN organizations o ON o.id = a.provider_org_id "
            "WHERE o.status = 'active' ORDER BY a.name"
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def get_by_id(api_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT a.*, o.status AS provider_status "
            "FROM apis a JOIN organizations o ON o.id = a.provider_org_id "
            "WHERE a.id = %s",
            (api_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()


def get_by_slug(slug):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT a.*, o.name AS provider_name, o.status AS provider_status "
            "FROM apis a JOIN organizations o ON o.id = a.provider_org_id "
            "WHERE a.slug = %s",
            (slug,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()

def list_for_provider(provider_org_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM apis WHERE provider_org_id = %s ORDER BY name",
            (provider_org_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def list_available_for(consumer_org_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT a.*, o.name AS provider_name "
            "FROM apis a JOIN organizations o ON o.id = a.provider_org_id "
            "WHERE o.status = 'active' AND a.provider_org_id <> %s ORDER BY a.name",
            (consumer_org_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()
