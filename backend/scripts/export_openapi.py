import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.main import app  # noqa: E402


def export_openapi_schema(output_path: Path | None = None) -> Path:
    target = output_path or (ROOT_DIR / "openapi.json")
    schema = app.openapi()
    target.write_text(
        json.dumps(schema, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return target


if __name__ == "__main__":
    out = export_openapi_schema()
    print(f"Exported OpenAPI schema to {out}")
