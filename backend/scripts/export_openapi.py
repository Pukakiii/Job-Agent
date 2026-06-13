"""Export the FastAPI OpenAPI schema to a static file.

The spec FastAPI serves at /openapi.json is generated from the route + Pydantic
definitions at import time. This script dumps that same schema to a checked-in
artifact so it can be diffed in review, fed to client codegen, or imported into
Postman/Swagger without booting the app.

Usage (from backend/):
    ./venv/Scripts/python.exe scripts/export_openapi.py            # -> openapi.json
    ./venv/Scripts/python.exe scripts/export_openapi.py openapi.yaml
"""
import json
import sys
from pathlib import Path

# Ensure the backend root (which holds the `app` package) is importable no matter
# what the current working directory is when the script is invoked.
BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app  # noqa: E402  (import after sys.path is set)

DEFAULT_OUT = BACKEND_ROOT / "openapi.json"


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    spec = app.openapi()

    if out.suffix in {".yaml", ".yml"}:
        import yaml

        text = yaml.safe_dump(spec, sort_keys=False, allow_unicode=True)
    else:
        text = json.dumps(spec, indent=2, ensure_ascii=False) + "\n"

    out.write_text(text, encoding="utf-8")
    print(f"Wrote {out} ({len(spec['paths'])} paths, OpenAPI {spec['openapi']})")


if __name__ == "__main__":
    main()
