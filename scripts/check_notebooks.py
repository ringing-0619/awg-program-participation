"""Validate source archives and execution editions; optionally execute on local client data."""

from pathlib import Path
import argparse
import ast
import hashlib
import json
import os
import nbformat


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--source", type=Path, help="Local project workbook directory")
    parser.add_argument("--normalized", type=Path, help="Local canonical input directory")
    parser.add_argument("--output", type=Path, help="Local validation output directory")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.execute:
        if any(p is None for p in [args.source, args.normalized, args.output]):
            parser.error("Execution requires --source, --normalized and --output")
        output = args.output.resolve()
        if output == root or root in output.parents:
            parser.error("Choose an output directory outside the public repository")
        os.environ["AWG_SOURCE_DIR"] = str(args.source.resolve())
        os.environ["AWG_NORMALIZED_DIR"] = str(args.normalized.resolve())
        os.environ["AWG_OUTPUT_DIR"] = str(output)
        output.mkdir(parents=True, exist_ok=True)
    for path in sorted((root/"notebooks").rglob("*.ipynb")):
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
        active = path.parent.name != "archive"
        for i, cell in enumerate(notebook.cells):
            if cell.cell_type == "code" and (cell.outputs or cell.execution_count is not None):
                raise ValueError(f"Clear saved outputs and execution counts: {path.name}")
            if active and cell.cell_type == "code":
                ast.parse(cell.source, filename=f"{path.name}:cell{i}")
        print(f"Validated {'execution edition' if active else 'source archive'}: {path.name}")
        if args.execute and active:
            from nbclient import NotebookClient
            NotebookClient(notebook, timeout=180, kernel_name="python3",
                           resources={"metadata": {"path": str(root)}}).execute()
            if path.name.startswith("02_"):
                text = "\n".join(str(o.get("text", "")) for c in notebook.cells for o in c.get("outputs", []))
                assert "93108" in text
                assert "0.051" in text and "0.014" in text
            executed = output/"executed-notebooks"
            executed.mkdir(exist_ok=True)
            nbformat.write(notebook, executed/path.name)
            print(f"Executed on local project inputs: {path.name}")
    records = json.loads((root/"notebooks/source_manifest.json").read_text())
    for record in records:
        for key, expected in [(record["public_file"], record["active_code_sha256"]),
                              (record["archived_file"], record["archive_code_sha256"])]:
            n = json.loads((root/"notebooks"/key).read_text())
            source = "\n".join("".join(c["source"]) for c in n["cells"] if c["cell_type"] == "code")
            assert hashlib.sha256(source.encode()).hexdigest() == expected, key


if __name__ == "__main__":
    main()
