"""Write the live OpenAPI schema to docs/openapi.json (run via `make api-docs`)."""

import json
import sys
from pathlib import Path

from app.main import app


def main() -> None:
    target = Path(sys.argv[1] if len(sys.argv) > 1 else "../docs/openapi.json")
    content = json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n"
    target.write_text(content, encoding="utf-8", newline="\n")
    print(f"Wrote {target}")  # noqa: T201 - CLI output


if __name__ == "__main__":
    main()
