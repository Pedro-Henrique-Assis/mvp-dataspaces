from app.database import get_connection
from app.repositories import credits


def find_active(consumer_org_id, api_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT s.*, p.code AS plan_code, p.name AS plan_name, "
            "p.subscription_price_credits, p.request_price_credits, p.max_access_level "
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
            "p.subscription_price_credits, p.request_price_credits "
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


def create_paid(consumer_org_id, provider_org_id, api_id, plan, descriptions):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        price = plan["subscription_price_credits"]
        if not credits.debit(cursor, consumer_org_id, price):
            connection.rollback()
            return None
        credits.credit(cursor, provider_org_id, price)
        cursor.execute(
            "INSERT INTO subscriptions (consumer_org_id, api_id, plan_id) "
            "VALUES (%s, %s, %s)",
            (consumer_org_id, api_id, plan["id"]),
        )
        subscription_id = cursor.lastrowid
        credits.log(cursor, consumer_org_id, -price, "subscription", descriptions["consumer"])
        credits.log(cursor, provider_org_id, price, "earning", descriptions["provider"])
        connection.commit()
        return subscription_id
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()
