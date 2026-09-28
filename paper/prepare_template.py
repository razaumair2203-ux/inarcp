"""Install separately obtained IEEE Access dependencies for the local build.

The repository does not redistribute the class or its font assets. No network
download, class substitution, or modification of dependency bytes occurs here.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-directory", required=True, type=Path)
    parser.add_argument("--verify-pinned", action="store_true",
                        help="Require every dependency to match the recorded build hashes")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    provenance = json.loads((root / "template_provenance.json").read_text())
    source = args.from_directory.resolve()
    destination = root / ".ieee-template"
    if not source.is_dir() or source == destination:
        parser.error("Provide a separate, existing template directory")
    selected = {}
    # Resolve and validate the entire set before writing anything.
    for name, expected in provenance["files"].items():
        matches = [p for p in source.rglob(name) if p.is_file()]
        if len(matches) != 1:
            parser.error(f"Expected one {name}; found {len(matches)}. See TEMPLATE.md")
        path = matches[0]
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if args.verify_pinned and actual != expected:
            parser.error(f"Hash mismatch for {name}; pinned verification failed")
        selected[name] = (path, actual)
    destination.mkdir(exist_ok=True)
    for name, (path, _) in selected.items():
        shutil.copyfile(path, destination / name)
    manifest = {name: digest for name, (_, digest) in selected.items()}
    (destination / "installed_manifest.json").write_text(
        json.dumps({"source_directory": str(source), "files": manifest}, indent=2) + "\n")
    print(f"Installed {len(selected)} unchanged dependencies into {destination}")
    print("Pinned hashes verified" if args.verify_pinned else
          "Installed source differs only if shown by comparing installed_manifest.json with template_provenance.json")


if __name__ == "__main__":
    main()
