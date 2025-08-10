import json
import os
import time
from typing import Any, Dict, Optional, Tuple

from loguru import logger

from .core.env import load_envs, validate_envs
from .core.db import get_db_connection
from .core.build import build_request_from_row
from .core.request import post_with_retry, enforce_json_content
from .core.logs import insert_log


def run_once(config_key: Optional[str] = None) -> None:
    load_envs()
    validate_envs()

    with get_db_connection() as conn:
        cur = conn.cursor()
        # fetch_active_config is simple enough to inline here to avoid another module
        if config_key:
            cur.execute(
                """
                SELECT c.base_url, c.api_key_encrypted, m.name AS model_name,
                       pp.params_json, pr.messages_json, pr.response_format_json, pr.variables_json,
                       cfg.config_key
                FROM ai_config cfg
                JOIN ai_model m ON m.id = cfg.model_id
                JOIN ai_connection c ON c.id = m.connection_id
                LEFT JOIN ai_param_profile pp ON pp.id = cfg.param_profile_id
                LEFT JOIN ai_prompt pr ON pr.id = cfg.prompt_id
                WHERE cfg.is_active = 1 AND cfg.config_key = %s
                LIMIT 1
                """,
                (config_key,),
            )
        else:
            cur.execute(
                """
                SELECT c.base_url, c.api_key_encrypted, m.name AS model_name,
                       pp.params_json, pr.messages_json, pr.response_format_json, pr.variables_json,
                       cfg.config_key
                FROM ai_config cfg
                JOIN ai_model m ON m.id = cfg.model_id
                JOIN ai_connection c ON c.id = m.connection_id
                LEFT JOIN ai_param_profile pp ON pp.id = cfg.param_profile_id
                LEFT JOIN ai_prompt pr ON pr.id = cfg.prompt_id
                WHERE cfg.is_active = 1
                ORDER BY cfg.id ASC
                LIMIT 1
                """
            )
        row = cur.fetchone()
        if not row:
            raise RuntimeError("CONFIG_NOT_FOUND")
        cols = [d[0] for d in cur.description]
        row_dict = dict(zip(cols, row))

        url, headers, body = build_request_from_row(row_dict)
        cfg_key = row_dict["config_key"]

        logger.info("Sending request to AI provider: config_key={} model={}", cfg_key, body.get("model"))
        t0 = time.monotonic()

        status, resp_json, error = post_with_retry(url, headers, body)
        if error is None and resp_json is not None:
            # enforce json if requested
            enforced, enforcement_error = enforce_json_content(row_dict, resp_json)
            if enforcement_error is None and enforced is not None:
                resp_json = enforced
            elif enforcement_error is not None:
                error = enforcement_error

        duration_ms = int((time.monotonic() - t0) * 1000)
        insert_log(cur, cfg_key, status, duration_ms, resp_json, error, body)

        if resp_json:
            try:
                choice = (resp_json.get("choices") or [])[0]
                content = None
                if isinstance(choice, dict):
                    msg = choice.get("message") or {}
                    content = msg.get("content")
                logger.info("AI response: {}", content)
            except Exception:
                logger.info("AI raw response keys: {}", list(resp_json.keys()))
        else:
            logger.warning("No response body. Check logs table for error details.")

