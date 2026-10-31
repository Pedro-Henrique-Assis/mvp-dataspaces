from app.database import get_connection


def find_active(consumer_org_id, api_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT s.*, p.code AS plan_code, p.name AS plan_name, "
            "p.subscription_price_usd, p.request_price_usd, p.max_access_level "
            "FROM subscriptions s JOIN plans p ON p.id = s.plan_id "
            "WHERE s.consumer_org_id = %s AND s.api_id = %s "
            "AND s.status = 'active'",
            (consumer_org_id, api_id),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()


def list_for_consumer(consumer_org_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT s.*, a.name AS api_name, p.name AS plan_name, "
            "p.subscription_price_usd, p.request_price_usd "
            "FROM subscriptions s JOIN apis a ON a.id = s.api_id "
            "JOIN plans p ON p.id = s.plan_id "
            "WHERE s.consumer_org_id = %s AND s.status = 'active' "
            "ORDER BY s.started_at DESC",
            (consumer_org_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def create(consumer_org_id, api_id, plan_id):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO subscriptions (consumer_org_id, api_id, plan_id) "
            "VALUES (%s, %s, %s)",
            (consumer_org_id, api_id, plan_id),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        connection.close()