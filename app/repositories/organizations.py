from app.database import get_connection
from app.repositories import credits


def list_catalog():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT o.id, o.name, o.sector, o.role, o.description, COUNT(a.id) AS api_count "
            "FROM organizations o LEFT JOIN apis a ON a.provider_org_id = o.id "
            "WHERE o.status = 'active' GROUP BY o.id ORDER BY o.name"
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


def list_by_status(status):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM organizations WHERE status = %s ORDER BY created_at, id",
            (status,),
        )
        organizations = cursor.fetchall()
        for organization in organizations:
            cursor.execute(
                "SELECT * FROM apis WHERE provider_org_id = %s ORDER BY id",
                (organization["id"],),
            )
            organization["apis"] = cursor.fetchall()
        return organizations
    finally:
        cursor.close()
        connection.close()


def activate(organization_id, credential, welcome_credits):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "UPDATE organizations SET status = 'active' "
            "WHERE id = %s AND status = 'pending'",
            (organization_id,),
        )
        if cursor.rowcount == 0:
            connection.rollback()
            return False
        cursor.execute(
            "INSERT INTO verifiable_credentials "
            "(organization_id, issuer_did, subject_did, role_provider, role_consumer, issued_at, expires_at) "
            "VALUES (%(organization_id)s, %(issuer_did)s, %(subject_did)s, %(role_provider)s, "
            "%(role_consumer)s, %(issued_at)s, %(expires_at)s)",
            dict(credential, organization_id=organization_id),
        )
        credits.credit(cursor, organization_id, welcome_credits)
        credits.log(cursor, organization_id, welcome_credits, "bonus", "Créditos de boas-vindas")
        connection.commit()
        return True
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def reject(organization_id, reason):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "UPDATE organizations SET status = 'rejected', rejection_reason = %s "
            "WHERE id = %s AND status = 'pending'",
            (reason, organization_id),
        )
        connection.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        connection.close()
