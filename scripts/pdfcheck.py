"""Check final PDFs with Poppler and render every page for visual review."""
import re
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'build/previews'
out.mkdir(exist_ok=True)
for name, expected in [('whitepaper', 11), ('presentation', 12)]:
    pdf = root / 'dist' / f'{name}.pdf'
    info = subprocess.check_output(['pdfinfo', str(pdf)], text=True)
    pages = int(re.search(r'^Pages:\s+(\d+)', info, re.M)[1])
    if pages != expected:
        raise SystemExit(f'{name}: expected {expected} pages, got {pages}')
    text = subprocess.check_output(['pdftotext', str(pdf), '-'], text=True)
    if len(text.strip()) < 1000 or '\ufffd' in text:
        raise SystemExit(f'{name}: missing or invalid extracted text')
    subprocess.run(['pdftoppm', '-scale-to', '1400', '-png', str(pdf), str(out / name)], check=True)
    print(f'{name}: {pages} pages, text extraction and render passed')
