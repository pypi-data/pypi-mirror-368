from __future__ import annotations

import json
from typing import Any, Dict, Optional, Tuple

import mysql.connector

from .db import get_db_connection


ErrorTuple = Tuple[str, str]


def _validation_error(message: str) -> ErrorTuple:
    return ("VALIDATION_ERROR", message)


def _db_error(ex: Exception) -> ErrorTuple:
    return ("DB_ERROR", str(ex))


def add_param_profile_if_absent(
    name: str, params: Dict[str, Any]
) -> Tuple[Optional[Dict[str, Any]], Optional[ErrorTuple]]:
    """Idempotently create a param profile by unique name.

    Returns (result_dict, error_tuple)
    - result_dict: {"id": int, "existed": bool}
    - error_tuple: (code, message) or None
    """
    if not isinstance(name, str) or not name.strip():
        return None, _validation_error("name is required")
    if not isinstance(params, dict):
        return None, _validation_error("params must be a dict")

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id FROM ai_param_profile WHERE name = %s LIMIT 1",
                (name,),
            )
            row = cur.fetchone()
            if row:
                return {"id": int(row[0]), "existed": True}, None

            cur.execute(
                """
                INSERT INTO ai_param_profile (name, params_json, is_active)
                VALUES (%s, %s, 1)
                """,
                (name, json.dumps(params, ensure_ascii=False)),
            )
            new_id = int(cur.lastrowid)
            return {"id": new_id, "existed": False}, None
    except mysql.connector.Error as ex:
        return None, _db_error(ex)
    except Exception as ex:  # safety net
        return None, ("UNEXPECTED_ERROR", str(ex))


def get_param_profile_by_name(name: str) -> Tuple[Optional[Dict[str, Any]], Optional[ErrorTuple]]:
    """Fetch a param profile by name.

    Returns (row_dict, error_tuple) where row_dict contains:
    {"id", "name", "params_json", "is_active", "created_at", "updated_at"}
    """
    if not isinstance(name, str) or not name.strip():
        return None, _validation_error("name is required")

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, name, params_json, is_active, created_at, updated_at
                FROM ai_param_profile
                WHERE name = %s
                LIMIT 1
                """,
                (name,),
            )
            row = cur.fetchone()
            if not row:
                return None, ("NOT_FOUND", f"param_profile '{name}' not found")

            cols = [d[0] for d in cur.description]
            return dict(zip(cols, row)), None
    except mysql.connector.Error as ex:
        return None, _db_error(ex)
    except Exception as ex:  # safety net
        return None, ("UNEXPECTED_ERROR", str(ex))

