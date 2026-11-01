from app.database import get_connection


def register_request(subscription_id, access_level, endpoint, amount_usd, success=True, error_message=None):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO api_requests "
            "(subscription_id, access_level, endpoint, amount_usd, success, error_message) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (subscription_id, access_level, endpoint, amount_usd, success, error_message),
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()