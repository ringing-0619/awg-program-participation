"""Check the public deliverable for local paths, client files, broken links, and outputs."""

from pathlib import Path
import ast
import hashlib
import json
import re
from urllib.parse import unquote
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", ".venv", "__pycache__", ".pytest_cache", "build", "dist"}
TEXT = {".md", ".py", ".json", ".ipynb", ".toml", ".yml", ".txt", ".csv"}


def markdown_anchors(text):
    counts, anchors = {}, set()
    for title in re.findall(r"^#{1,6}\s+(.+)$", text, flags=re.M):
        slug = re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")
        occurrence = counts.get(slug, 0)
        anchors.add(slug if occurrence == 0 else f"{slug}-{occurrence}")
        counts[slug] = occurrence + 1
    anchors.update(re.findall(r'<a\s+(?:id|name)=[\"\']([^\"\']+)', text))
    return anchors


def main():
    errors = []
    presentation_manifest = ROOT/"presentations/source_manifest.json"
    presentations = json.loads(presentation_manifest.read_text()) if presentation_manifest.exists() else []
    approved = {f"presentations/{record['file']}": record for record in presentations}
    files = [p for p in ROOT.rglob("*") if p.is_file() and not set(p.relative_to(ROOT).parts) & SKIP
             and not any(part.endswith(".egg-info") for part in p.parts)]
    for file in files:
        relative = str(file.relative_to(ROOT))
        if file.suffix.lower() in {".xlsx", ".xls", ".csv", ".pdf", ".pkl", ".zip"}:
            errors.append(f"Unexpected source/binary client artifact: {file.relative_to(ROOT)}")
        if file.suffix.lower() == ".pptx":
            if relative not in approved:
                errors.append(f"Add approved presentation provenance: {relative}")
            else:
                record = approved[relative]
                if hashlib.sha256(file.read_bytes()).hexdigest() != record['sha256']:
                    errors.append(f"Presentation hash mismatch: {relative}")
                with zipfile.ZipFile(file) as archive:
                    names = archive.namelist()
                    if any('/embeddings/' in name for name in names):
                        errors.append(f"Review embedded data payloads: {relative}")
                    slides = [name for name in names if re.fullmatch(r'ppt/slides/slide\d+\.xml', name)]
                    if len(slides) != record['slides']:
                        errors.append(f"Presentation slide count mismatch: {relative}")
                    for name in names:
                        if name.endswith('.rels'):
                            if any(element.attrib.get('TargetMode') == 'External' for element in ET.fromstring(archive.read(name))):
                                errors.append(f"Review external presentation relationship: {relative}")
        if file.suffix in TEXT:
            text = file.read_text()
            if re.search(r"/(?:Users|home)/[^\s\"']+", text):
                errors.append(f"Absolute personal path: {file.relative_to(ROOT)}")
            if file.suffix == ".md":
                for link in re.findall(r"\]\(([^)]+)\)", text):
                    if link.startswith(("http", "mailto:")):
                        continue
                    target, _, fragment = unquote(link).partition("#")
                    destination = file.parent / target if target else file
                    if not destination.exists():
                        errors.append(f"Broken link in {file.relative_to(ROOT)}: {target}")
                    elif fragment and destination.suffix == '.md':
                        if fragment not in markdown_anchors(destination.read_text()):
                            errors.append(f"Review heading link in {relative}: {link}")
            if file.suffix == '.py':
                try:
                    ast.parse(text, filename=relative)
                except SyntaxError as error:
                    errors.append(f"Python syntax: {relative}: {error}")
            if file.suffix == ".ipynb":
                notebook = json.loads(text)
                for cell in notebook["cells"]:
                    if cell.get("cell_type") == "code" and (cell.get("outputs") or cell.get("execution_count") is not None):
                        errors.append(f"Stored notebook output: {file.relative_to(ROOT)}")
    for name in ["README.md", "README.zh-CN.md", "LICENSE", "docs/case-study.md", "docs/methodology.md",
                 "notebooks/00_wide_to_long_reference.ipynb", "notebooks/01_checkpoint1_data_and_metrics.ipynb",
                 "notebooks/02_checkpoint2_brand_and_division.ipynb", "notebooks/source_manifest.json",
                 "presentations/checkpoint-1-client-presentation.pptx", "presentations/checkpoint-2-client-presentation.pptx",
                 "presentations/source_manifest.json", "docs/notebook-changes.md",
                 "reports/presentation-excerpts/source_manifest.json"]:
        if not (ROOT/name).exists():
            errors.append(f"Missing required output: {name}")
    for record in json.loads((ROOT/"reports/presentation-excerpts/source_manifest.json").read_text()):
        path = ROOT/"reports/presentation-excerpts"/record['file']
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != record['image_sha256']:
            errors.append(f"Original chart provenance: {record['file']}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Public repository checks passed ({len(files)} files).")


if __name__ == "__main__":
    main()
