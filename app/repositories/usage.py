from app.database import get_connection
from app.repositories import credits


def register_paid_request(subscription, consumer_org_id, provider_org_id, access_level, endpoint, price, descriptions):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        if not credits.debit(cursor, consumer_org_id, price):
            connection.rollback()
            return False
        credits.credit(cursor, provider_org_id, price)
        cursor.execute(
            "INSERT INTO api_requests "
            "(subscription_id, access_level, endpoint, credits, success) "
            "VALUES (%s, %s, %s, %s, TRUE)",
            (subscription["id"], access_level, endpoint, price),
        )
        credits.log(cursor, consumer_org_id, -price, "request", descriptions["consumer"])
        credits.log(cursor, provider_org_id, price, "earning", descriptions["provider"])
        connection.commit()
        return True
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def summary_for_consumer(consumer_org_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT a.name AS api_name, p.name AS plan_name, "
            "p.subscription_price_credits, COUNT(r.id) AS request_count, "
            "COALESCE(SUM(r.credits), 0) AS request_total "
            "FROM subscriptions s "
            "JOIN apis a ON a.id = s.api_id "
            "JOIN plans p ON p.id = s.plan_id "
            "LEFT JOIN api_requests r ON r.subscription_id = s.id "
            "WHERE s.consumer_org_id = %s AND s.status = 'active' "
            "GROUP BY s.id, a.name, p.name, p.subscription_price_credits",
            (consumer_org_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()