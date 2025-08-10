import argparse
import os
import sys


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m backend.ai_runner_hjy",
        description=(
            "Run one AI call using a config_key from RDS (OpenAI-compatible). "
            "Loads envs from project root automatically."
        ),
    )
    parser.add_argument(
        "-k",
        "--config-key",
        dest="config_key",
        help="ai_config.config_key to use (optional; default: first active config)",
    )
    parser.add_argument(
        "--timeout",
        dest="timeout",
        type=int,
        help="override AI_TIMEOUT seconds (optional)",
    )
    parser.add_argument(
        "--max-retries",
        dest="max_retries",
        type=int,
        help="override AI_MAX_RETRIES (optional)",
    )
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args(sys.argv[1:])

    if args.timeout is not None:
        os.environ["AI_TIMEOUT"] = str(args.timeout)
    if args.max_retries is not None:
        os.environ["AI_MAX_RETRIES"] = str(args.max_retries)

    try:
        # Lazy import to allow -h without full deps
        from .core.env import load_envs, validate_envs
        from .run import run_once

        load_envs()
        validate_envs()
        run_once(args.config_key)
        return 0
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        # Minimal stderr reporting; detailed logs already handled inside run_once
        sys.stderr.write(f"Error: {exc}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

