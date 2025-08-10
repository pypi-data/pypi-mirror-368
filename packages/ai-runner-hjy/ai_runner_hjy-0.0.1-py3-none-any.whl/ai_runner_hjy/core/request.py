import json
import os
import time
import random
from typing import Any, Dict, Optional, Tuple

import httpx
from loguru import logger


def post_with_retry(url: str, headers: Dict[str, str], body: Dict[str, Any]) -> Tuple[int, Optional[Dict[str, Any]], Optional[Tuple[str, str]]]:
    """POST with exponential backoff retry and error classification.

    Returns (status, resp_json, error_tuple)
    error_tuple: (error_code, error_message) or None
    """
    timeout_s = int(os.environ.get("AI_TIMEOUT", "30") or 30)
    max_retries = int(os.environ.get("AI_MAX_RETRIES", "2") or 2)
    base_ms = int(os.environ.get("AI_RETRY_BASE_MS", "500") or 500)
    jitter_on = (os.environ.get("AI_RETRY_JITTER", "true").lower() == "true")

    def should_retry_status(code: int) -> bool:
        if code == 429:
            return True
        if 500 <= code <= 599:
            return True
        return False

    status: int = 0
    resp_json: Optional[Dict[str, Any]] = None
    error: Optional[Tuple[str, str]] = None

    try:
        with httpx.Client(timeout=timeout_s) as client:
            for attempt in range(max_retries + 1):
                try:
                    r = client.post(url, headers=headers, json=body)
                    status = r.status_code
                    if 200 <= status < 300:
                        resp_json = r.json()
                        error = None
                        break
                    if should_retry_status(status) and attempt < max_retries:
                        delay = (base_ms * (2 ** attempt)) / 1000.0
                        if jitter_on:
                            delay *= (0.8 + 0.4 * random.random())
                        time.sleep(delay)
                        continue
                    try:
                        resp_json = r.json()
                    except Exception:
                        resp_json = None
                    code_name = "HTTP_429_RATE_LIMIT" if status == 429 else ("HTTP_5XX_SERVER_ERROR" if 500 <= status <= 599 else "HTTP_STATUS_ERROR")
                    error = (code_name, f"status={status}")
                    break
                except httpx.TimeoutException as e:
                    if attempt < max_retries:
                        delay = (base_ms * (2 ** attempt)) / 1000.0
                        if jitter_on:
                            delay *= (0.8 + 0.4 * random.random())
                        time.sleep(delay)
                        continue
                    error = ("NETWORK_TIMEOUT", str(e))
                    break
                except httpx.RequestError as e:
                    if attempt < max_retries:
                        delay = (base_ms * (2 ** attempt)) / 1000.0
                        if jitter_on:
                            delay *= (0.8 + 0.4 * random.random())
                        time.sleep(delay)
                        continue
                    error = ("NETWORK_ERROR", str(e))
                    break
    except Exception as e:
        error = ("REQUEST_ERROR", str(e))

    return status, resp_json, error


def enforce_json_content(row: Dict[str, Any], resp_json: Optional[Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], Optional[Tuple[str, str]]]:
    """When response_format requires JSON, try to ensure content is JSON.

    If invalid JSON, attempt corrective retries (3x, 1s apart). Returns (resp_json, error).
    """
    if resp_json is None:
        return None, ("REQUEST_ERROR", "empty response")

    def needs_json_enforce(row_dict: Dict[str, Any]) -> bool:
        try:
            rf = row_dict.get("response_format_json")
            if isinstance(rf, str):
                rf = json.loads(rf)
            params = row_dict.get("params_json")
            if isinstance(params, str):
                params = json.loads(params)
            if rf and isinstance(rf, dict) and rf.get("type") == "json_object":
                return True
            if params and isinstance(params, dict) and params.get("JSON_SCHEMA_ENFORCE"):
                return True
        except Exception:
            pass
        return False

    def extract_content(js: Dict[str, Any]) -> Optional[str]:
        try:
            choice = (js.get("choices") or [])[0]
            if isinstance(choice, dict):
                msg = choice.get("message") or {}
                return msg.get("content")
        except Exception:
            return None
        return None

    if not needs_json_enforce(row):
        return resp_json, None

    content = extract_content(resp_json)
    try:
        if isinstance(content, str):
            json.loads(content)
            return resp_json, None
    except Exception:
        pass

    # corrective retries: fixed 3 attempts, 1s apart, re-POST same body
    # 这里不直接重发 HTTP，由上层 run_once 负责决定是否再次 post（避免重复散落HTTP逻辑）
    return None, ("SCHEMA_INVALID", "model did not return parseable JSON content")

