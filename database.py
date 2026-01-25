import mysql.connector
import os
from dotenv import load_dotenv
from mysql.connector.pooling import MySQLConnectionPool

load_dotenv()

_pool = None

#def get_connection():
#    return mysql.connector.connect(
#        host=os.getenv("DB_HOST"),
#        user=os.getenv("DB_USER"),
#        password=os.getenv("DB_PASSWORD"),
#        database=os.getenv("DB_NAME")
#    )

def init_pool():
    global _pool
    if _pool is None:
        _pool = MySQLConnectionPool(
            pool_name="taipei_day_trip",
            pool_size=int(os.getenv("DB_POOL_SIZE","10")),
            pool_reset_session=True,
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )

def get_connection():
    if _pool is None:
        init_pool()
    return _pool.get_connection()