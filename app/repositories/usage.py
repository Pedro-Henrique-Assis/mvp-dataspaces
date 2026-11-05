from app.database import get_connection


def register_request(subscription_id, access_level, endpoint, credits, success=True, error_message=None):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO api_requests "
            "(subscription_id, access_level, endpoint, credits, success, error_message) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (subscription_id, access_level, endpoint, credits, success, error_message),
        )
        connection.commit()
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