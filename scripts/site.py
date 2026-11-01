"""Stage only explicitly selected publication files for public deployment."""
import hashlib
import html
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from workflow_publications import stage

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
if DIST.exists():
    shutil.rmtree(DIST)
DIST.mkdir()
try:
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
except subprocess.CalledProcessError:
    commit = "local-preview"
records = []
for name in ("whitepaper.pdf", "presentation.pdf"):
    source = ROOT / "build" / name
    shutil.copyfile(source, DIST / name)
    records.append(dict(file=name, sha256=hashlib.sha256(source.read_bytes()).hexdigest(), bytes=source.stat().st_size))
manifest = dict(version="0.1.0", built_at=datetime.now(timezone.utc).isoformat(), commit=commit, documents=records)
(DIST / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
workflow_links = stage(ROOT / "workflow-publications", DIST / "workflows")
(DIST / "index.html").write_text((ROOT / "site/index.html").read_text().replace("{{COMMIT}}",html.escape(commit)).replace("{{WORKFLOW_PUBLICATIONS}}", workflow_links))
(DIST / ".nojekyll").touch()
