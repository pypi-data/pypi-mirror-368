import os
from dotenv import load_dotenv


def load_envs() -> None:
    """Load split env files from project root without overriding existing envs."""
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    for name in ("basic.env", "mysql.env"):
        path = os.path.join(root, name)
        if os.path.exists(path):
            load_dotenv(path, override=False)


def _require(name: str, missing: list[str]) -> None:
    if not os.environ.get(name):
        missing.append(name)


def validate_envs() -> None:
    missing: list[str] = []
    _require("MYSQL_HOST", missing)
    _require("MYSQL_USER", missing)
    _require("MYSQL_PASSWORD", missing)
    if not (os.environ.get("MYSQL_AI_DATABASE") or os.environ.get("MYSQL_DATABASE")):
        missing.append("MYSQL_AI_DATABASE or MYSQL_DATABASE")
    _require("AI_PEPPER", missing)

    if missing:
        hint = (
            "Missing required env variables: "
            + ", ".join(missing)
            + ". Ensure you have created root-level basic.env/mysql.env and filled values."
        )
        raise RuntimeError(hint)
    # Normalize port
    try:
        int(os.environ.get("MYSQL_PORT", "3306"))
    except ValueError:
        os.environ["MYSQL_PORT"] = "3306"

