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


def count_by_status(status):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM organizations WHERE status = %s", (status,))
        return cursor.fetchone()[0]
    finally:
        cursor.close()
        connection.close()


def get_by_cnpj(cnpj):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM organizations WHERE cnpj = %s", (cnpj,))
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()


def create_with_api(organization, api):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO organizations "
            "(name, cnpj, email, password_hash, did, sector, role, contact_name, description, website) "
            "VALUES (%(name)s, %(cnpj)s, %(email)s, %(password_hash)s, %(did)s, %(sector)s, "
            "%(role)s, %(contact_name)s, %(description)s, %(website)s)",
            organization,
        )
        if api:
            cursor.execute(
                "INSERT INTO apis "
                "(provider_org_id, name, slug, description, basic_response, premium_response, "
                "policy_purpose, policy_allows_redistribution, policy_retention_days, policy_notes) "
                "VALUES (%(provider_org_id)s, %(name)s, %(slug)s, %(description)s, %(basic_response)s, "
                "%(premium_response)s, %(policy_purpose)s, %(policy_allows_redistribution)s, "
                "%(policy_retention_days)s, %(policy_notes)s)",
                dict(api, provider_org_id=cursor.lastrowid),
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()
