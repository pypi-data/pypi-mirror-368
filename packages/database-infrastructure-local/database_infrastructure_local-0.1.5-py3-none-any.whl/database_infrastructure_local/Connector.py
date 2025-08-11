import mysql.connector
from functools import lru_cache
from python_sdk_remote.utilities import get_sql_hostname, get_sql_username, get_sql_password


# We are using the database directly to avoid cyclic dependency
@lru_cache(maxsize=1)
def get_connection() -> mysql.connector:
    connection = mysql.connector.connect(
        host=get_sql_hostname(),
        user=get_sql_username(),
        password=get_sql_password()
    )
    return connection
