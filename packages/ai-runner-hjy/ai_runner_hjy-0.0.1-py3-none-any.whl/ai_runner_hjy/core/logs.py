from typing import Any, Dict, Optional, Tuple
import json
import mysql.connector


def _safe_json_dump(obj: Any) -> Optional[str]:
    try:
        if obj is None:
            return None
        return json.dumps(obj, ensure_ascii=False)
    except Exception:
        try:
            return str(obj)
        except Exception:
            return None


def insert_log(cursor,
               config_key: str,
               http_status: int,
               duration_ms: int,
               resp: Optional[Dict[str, Any]],
               err: Optional[Tuple[str, str]],
               request_body: Optional[Dict[str, Any]] = None) -> None:
    usage = (resp or {}).get("usage") or {}
    response_id = (resp or {}).get("id")
    try:
        cursor.execute(
            """
            INSERT INTO ai_call_logs
                (config_key, http_status, duration_ms,
                 prompt_tokens, completion_tokens, total_tokens,
                 response_id, error_code, error_message,
                 request_body_json, response_body_json)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                config_key,
                http_status,
                duration_ms,
                usage.get("prompt_tokens"),
                usage.get("completion_tokens"),
                usage.get("total_tokens"),
                response_id,
                err[0] if err else None,
                err[1] if err else None,
                _safe_json_dump(request_body),
                _safe_json_dump(resp),
            ),
        )
        return
    except mysql.connector.Error:
        pass

    cursor.execute(
        """
        INSERT INTO ai_call_logs
            (config_key, http_status, duration_ms, prompt_tokens, completion_tokens, total_tokens, response_id, error_code, error_message)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            config_key,
            http_status,
            duration_ms,
            usage.get("prompt_tokens"),
            usage.get("completion_tokens"),
            usage.get("total_tokens"),
            response_id,
            err[0] if err else None,
            err[1] if err else None,
        ),
    )

