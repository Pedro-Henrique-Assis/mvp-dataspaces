from app.database import get_connection
from app.repositories import credits


def expire_overdue(organization_id):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "UPDATE pix_charges SET status = 'expired' "
            "WHERE organization_id = %s AND status = 'pending' AND expires_at < NOW()",
            (organization_id,),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def find_open(organization_id, package):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT code FROM pix_charges "
            "WHERE organization_id = %s AND credits = %s "
            "AND status = 'pending' AND expires_at >= NOW() "
            "ORDER BY id DESC LIMIT 1",
            (organization_id, package),
        )
        row = cursor.fetchone()
        return row[0] if row else None
    finally:
        cursor.close()
        connection.close()


def create(organization_id, code, package, amount_usd, minutes):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO pix_charges (organization_id, code, credits, amount_usd, expires_at) "
            "VALUES (%s, %s, %s, %s, DATE_ADD(NOW(), INTERVAL %s MINUTE))",
            (organization_id, code, package, amount_usd, minutes),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def get_by_code(organization_id, code):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM pix_charges WHERE code = %s AND organization_id = %s",
            (code, organization_id),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()


def confirm(organization_id, code, description):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "UPDATE pix_charges SET status = 'paid', paid_at = NOW() "
            "WHERE code = %s AND organization_id = %s "
            "AND status = 'pending' AND expires_at >= NOW()",
            (code, organization_id),
        )
        if cursor.rowcount == 1:
            cursor.execute("SELECT credits FROM pix_charges WHERE code = %s", (code,))
            amount = cursor.fetchone()[0]
            credits.credit(cursor, organization_id, amount)
            credits.log(cursor, organization_id, amount, "top_up", description)
            connection.commit()
            return "paid"
        connection.rollback()
        cursor.execute(
            "SELECT status FROM pix_charges WHERE code = %s AND organization_id = %s",
            (code, organization_id),
        )
        row = cursor.fetchone()
        if row is None:
            return "not_found"
        if row[0] == "paid":
            return "already_paid"
        cursor.execute(
            "UPDATE pix_charges SET status = 'expired' WHERE code = %s AND status = 'pending'",
            (code,),
        )
        connection.commit()
        return "expired"
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()
