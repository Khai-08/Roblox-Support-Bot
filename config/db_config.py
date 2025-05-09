import mysql.connector

def get_db_connection(settings):
    db_config = settings["database"]

    return mysql.connector.connect(
        host=db_config["host"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"]
    )