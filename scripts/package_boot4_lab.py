"""Publish a verified source snapshot and sanitized run evidence to the static site."""
from pathlib import Path
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "examples/boot4-verification-lab"
GENERATED = LAB / "verification-output/evidence"
PUBLISHED = LAB / "evidence"
record = json.loads((GENERATED / "results.json").read_text())
for relative, digest in record["source_sha256"].items():
    assert hashlib.sha256((LAB / relative).read_bytes()).hexdigest() == digest, relative
for profile in ["boot3", "boot4"]:
    result = record["results"][profile]
    assert [result[k] for k in ["tests", "failures", "errors", "skipped", "exit"]] == [11, 0, 0, 0, 0]
assert record["results"]["discovery"]["exit"] == 1
assert [record["results"]["error-dispatch"][key] for key in ["tests", "failures", "errors", "skipped", "exit"]] == [1, 1, 0, 0, 1]
for path in GENERATED.rglob("*.xml"):
    ET.parse(path)
if PUBLISHED.exists():
    shutil.rmtree(PUBLISHED)
shutil.copytree(GENERATED, PUBLISHED)
for path in PUBLISHED.glob("*.log"):
    path.write_text("\n".join(line.rstrip() for line in path.read_text().split("\n")))
web_evidence = ROOT / "public/examples/boot4-verification"
if web_evidence.exists():
    shutil.rmtree(web_evidence)
shutil.copytree(PUBLISHED, web_evidence)
destination = ROOT / "public/examples/boot4-verification-lab.zip"
with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(LAB.rglob("*")):
        relative = path.relative_to(LAB)
        if path.is_file() and not {"target", "verification-output", "__pycache__"} & set(relative.parts):
            archive.write(path, Path("boot4-verification-lab") / relative)
with zipfile.ZipFile(destination) as archive:
    assert archive.testzip() is None
    assert b"/Users/forever" not in b"".join(archive.read(name) for name in archive.namelist())
print(f"Packaged {destination.name}: {destination.stat().st_size} bytes")
