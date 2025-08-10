import os
import mysql.connector
from typing import Optional


def get_db_connection(database: Optional[str] = None):
    cfg_db = database or os.getenv("MYSQL_AI_DATABASE") or os.getenv("MYSQL_DATABASE")
    if not cfg_db:
        raise RuntimeError("MYSQL_AI_DATABASE or MYSQL_DATABASE must be set")
    return mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST"),
        port=int(os.environ.get("MYSQL_PORT", "3306")),
        user=os.environ.get("MYSQL_USER"),
        password=os.environ.get("MYSQL_PASSWORD"),
        database=cfg_db,
        autocommit=True,
        ssl_disabled=False,
    )

