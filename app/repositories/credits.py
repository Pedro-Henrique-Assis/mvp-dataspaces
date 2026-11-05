from app.database import get_connection


def debit(cursor, organization_id, amount):
    cursor.execute(
        "UPDATE organizations SET credit_balance = credit_balance - %s "
        "WHERE id = %s AND credit_balance >= %s",
        (amount, organization_id, amount),
    )
    return cursor.rowcount == 1


def credit(cursor, organization_id, amount):
    cursor.execute(
        "UPDATE organizations SET credit_balance = credit_balance + %s WHERE id = %s",
        (amount, organization_id),
    )


def log(cursor, organization_id, amount, type, description):
    cursor.execute("SELECT credit_balance FROM organizations WHERE id = %s", (organization_id,))
    balance = cursor.fetchone()[0]
    cursor.execute(
        "INSERT INTO credit_transactions "
        "(organization_id, amount, type, description, balance_after) "
        "VALUES (%s, %s, %s, %s, %s)",
        (organization_id, amount, type, description, balance),
    )


def add(organization_id, amount, type, description):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        credit(cursor, organization_id, amount)
        log(cursor, organization_id, amount, type, description)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def get_balance(organization_id):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT credit_balance FROM organizations WHERE id = %s", (organization_id,))
        return cursor.fetchone()[0]
    finally:
        cursor.close()
        connection.close()


def count_for_organization(organization_id):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM credit_transactions WHERE organization_id = %s", (organization_id,))
        return cursor.fetchone()[0]
    finally:
        cursor.close()
        connection.close()


def list_for_organization(organization_id, limit, offset):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM credit_transactions WHERE organization_id = %s "
            "ORDER BY created_at DESC, id DESC LIMIT %s OFFSET %s",
            (organization_id, limit, offset),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def totals_for_organization(organization_id):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT COALESCE(-SUM(CASE WHEN amount < 0 THEN amount END), 0), "
            "COALESCE(SUM(CASE WHEN type = 'earning' THEN amount END), 0) "
            "FROM credit_transactions WHERE organization_id = %s",
            (organization_id,),
        )
        spent, received = cursor.fetchone()
        return {"spent": int(spent), "received": int(received)}
    finally:
        cursor.close()
        connection.close()
