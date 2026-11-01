"""Publication checks: TeX diagnostics, PDF integrity and deployment allowlist."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for stem in ("whitepaper", "presentation"):
    log = (ROOT / "build" / f"{stem}.log").read_text(errors="replace")
    errors = re.findall(r"(?:Overfull \\[hv]box[^\n]*|LaTeX Warning: (?:Reference|Citation)[^\n]*|LaTeX Warning: There were undefined references[^\n]*|Missing character[^\n]*|! .*)", log)
    if errors:
        raise SystemExit(f"{stem}: " + "\n".join(errors))
    pdf = (ROOT / "dist" / f"{stem}.pdf").read_bytes()
    if not pdf.startswith(b"%PDF-") or b"%%EOF" not in pdf[-1024:]:
        raise SystemExit(f"Invalid PDF: {stem}")
expected = {"index.html", "whitepaper.pdf", "presentation.pdf", "manifest.json", ".nojekyll"}
if (ROOT / "dist/workflows").exists():
    expected.add("workflows")
    assert {p.name for p in (ROOT / "dist/workflows").iterdir()} == {"index.html", "whitepaper.pdf", "deck.pdf", "manifest.json"}
assert {f.name for f in (ROOT / "dist").iterdir()} == expected, "Unexpected public output"
page = (ROOT / "dist/index.html").read_text()
assert "{{" not in page, "Unexpanded site placeholder"
for link in re.findall(r'href="([^"#]+)"', page):
    if not link.startswith(("https://", "http://")):
        assert (ROOT / "dist" / link).is_file(), f"Missing local link {link}"
manifest=json.loads((ROOT / "dist/manifest.json").read_text())
assert len(manifest["documents"]) == 2
print("Publication checks passed: TeX diagnostics, PDF structure, links and output allowlist")
