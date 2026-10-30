import mysql.connector
from flask import current_app


def get_connection():
    """Abre uma conexão usando a configuração da aplicação Flask."""
    return mysql.connector.connect(**current_app.config["MYSQL_CONFIG"])