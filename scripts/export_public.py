"""Create a reviewable ZIP from an explicit allowlist, excluding environments and client files."""

from pathlib import Path
import argparse
import zipfile
from validate_repository import main as validate

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_ROOTS = {".github", "src", "scripts", "tests", "docs", "notebooks", "data", "reports", "presentations"}
ALLOWED_FILES = {"README.md", "README.zh-CN.md", "LICENSE", "NOTICE.md", "pyproject.toml",
                 "requirements.txt", "requirements-lock.txt", ".gitignore", ".gitattributes"}


def main(output):
    validate()
    output = Path(output).resolve()
    if output == ROOT or ROOT in output.parents:
        raise ValueError("Put the archive outside the repository")
    output.parent.mkdir(parents=True, exist_ok=True)
    included = []
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(ROOT.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(ROOT)
            if (set(relative.parts) & {"__pycache__", ".ipynb_checkpoints"}
                    or any(part.endswith(".egg-info") for part in relative.parts)):
                continue
            if ((len(relative.parts) == 1 and path.name in ALLOWED_FILES)
                    or (relative.parts[0] in ALLOWED_ROOTS and path.suffix in {
                        ".py", ".md", ".json", ".ipynb", ".png", ".pptx", ".yml"})):
                archive.write(path, Path(ROOT.name)/relative)
                included.append(str(relative))
    print(f"Exported {len(included)} public files to {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    main(parser.parse_args().output)
