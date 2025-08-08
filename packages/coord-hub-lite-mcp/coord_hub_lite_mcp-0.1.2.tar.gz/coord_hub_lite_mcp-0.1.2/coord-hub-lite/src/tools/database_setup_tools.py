"""MCP tools for first-run database initialization and setup."""
from __future__ import annotations

import os
import json
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime, timezone

from fastmcp import Context

from src.tools.security_wrapper import secure_mcp_tool
from src.database.session import (
    build_sqlite_url,
    reconfigure_database,
    get_current_database_url,
)
from src.tools.database_init_tool import DatabaseInitializer
from src.config import get_settings


def _persist_env(database_url: str, db_path: str, project_root: Optional[Path] = None) -> bool:
    """Persist DATABASE_URL and COORD_HUB_DB_PATH into .env in project root.
    Returns True on success, False if persistence failed.
    """
    try:
        root = project_root or Path.cwd()
        env_path = root / ".env"
        backup_path = root / f".env.backup.{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

        existing = {}
        if env_path.exists():
            # Backup existing
            env_path.replace(backup_path)
            # Read old content
            with open(backup_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        existing[k.strip()] = v.strip()

        # Overwrite/merge
        existing["DATABASE_URL"] = database_url
        existing["COORD_HUB_DB_PATH"] = str(Path(db_path).expanduser().resolve())

        with open(env_path, "w", encoding="utf-8") as f:
            for k, v in existing.items():
                f.write(f"{k}={v}\n")
        return True
    except Exception:
        return False


@secure_mcp_tool(permission="database.init", require_auth=True, audit_logging=True)
async def initialize_database_tool(
    location_path: str,
    overwrite_if_exists: bool = False,
    set_as_default: bool = True,
    context: Optional[Context] = None,
) -> Dict[str, Any]:
    """Create a SQLite database at a user-specified path and hot-reload the server to use it.

    - If `location_path` is a directory, the DB will be created as `coord_hub_lite.db` inside it.
    - If it ends with `.db`, that exact path is used.
    - When `set_as_default` is True, the tool writes DATABASE_URL/COORD_HUB_DB_PATH to `.env`.
    - The server switches to the new database at runtime without restart.
    """
    started_at = datetime.now(timezone.utc).isoformat()
    trace_id = f"dbinit-{int(datetime.now(timezone.utc).timestamp())}"

    # Resolve DB file path
    path = Path(location_path).expanduser().resolve()
    if path.suffix.lower() != ".db":
        # Treat as directory
        db_path = path / "coord_hub_lite.db"
    else:
        db_path = path

    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    initializer = DatabaseInitializer(db_path=str(db_path), force=overwrite_if_exists)

    # Create DB if needed
    if db_path.exists() and not overwrite_if_exists:
        created = True
        created_message = "Database already exists; no changes made"
    else:
        created = initializer.create_database()
        created_message = "Database created" if created else "Database creation failed"
        if not created:
            return {
                "success": False,
                "message": created_message,
                "db_path": str(db_path),
                "trace_id": trace_id,
            }

    # Verify
    verification = initializer.verify_database()
    if not verification.get("valid"):
        return {
            "success": False,
            "message": f"Verification failed: {verification.get('error')}",
            "db_path": str(db_path),
            "trace_id": trace_id,
        }

    # Build URL and hot-reload
    database_url = build_sqlite_url(str(db_path))
    await reconfigure_database(database_url)

    # Persist to .env if requested
    persisted = False
    if set_as_default:
        persisted = _persist_env(database_url, str(db_path))

    details = {
        "version": verification.get("version"),
        "tables_count": len(verification.get("tables", [])),
        "size_bytes": verification.get("size"),
        "created_at": started_at,
        "trace_id": trace_id,
    }

    message = f"{created_message}. Runtime reconfigured to new database."
    if set_as_default:
        message += " Settings persisted to .env." if persisted else " Failed to persist settings to .env."

    return {
        "success": True,
        "database_url": database_url,
        "db_path": str(db_path),
        "persisted_to_env": bool(persisted),
        "reloaded_runtime": True,
        "message": message,
        "details": details,
    }


# Registry for potential direct imports
DATABASE_SETUP_TOOLS = {
    "initialize_database_tool": initialize_database_tool,
}


