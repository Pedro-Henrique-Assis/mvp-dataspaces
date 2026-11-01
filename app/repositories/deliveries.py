from app.database import get_connection


def list_for_api(api_id, access_level):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        fields = "tracking_code, origin, destination, status"
        if access_level == "premium":
            fields += ", estimated_delivery, route_distance_km"
        cursor.execute(
            f"SELECT {fields} FROM deliveries WHERE api_id = %s ORDER BY id",
            (api_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()