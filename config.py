import os
from dotenv import load_dotenv

load_dotenv()
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1118',
    'database': 'inventory_system',
    'charset': 'utf8mb4',
    'cursorclass': 'pymysql.cursors.DictCursor'
}

SECRET_KEY = '1118'
