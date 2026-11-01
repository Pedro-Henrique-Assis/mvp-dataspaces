from app.database import get_connection


def list_for_api(api_id, access_level):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        fields = "vehicle_code, vehicle_type, available"
        if access_level == "premium":
            fields += ", capacity_kg, current_location, next_available_date"
        cursor.execute(
            f"SELECT {fields} FROM vehicles WHERE api_id = %s ORDER BY id",
            (api_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()