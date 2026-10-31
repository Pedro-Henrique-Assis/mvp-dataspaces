from app.database import get_connection


def list_all():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM plans ORDER BY subscription_price_usd")
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def get_by_id(plan_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM plans WHERE id = %s", (plan_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()