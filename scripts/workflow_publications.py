"""Validate and stage the PDF-only snapshot sent by the private application CI."""
import hashlib
import html
import json
from pathlib import Path
import re
import shutil


def stage(source: Path, destination: Path):
    if not source.exists():
        return ''
    expected = {'whitepaper.pdf', 'deck.pdf', 'manifest.json'}
    if {path.name for path in source.iterdir()} != expected or any(path.is_symlink() for path in source.iterdir()):
        raise ValueError('Workflow publication snapshot must contain only two PDFs and its manifest')
    manifest = json.loads((source / 'manifest.json').read_text())
    if set(manifest) != {'source_commit', 'source_run', 'documents'}:
        raise ValueError('Unexpected publication metadata')
    if not re.fullmatch(r'[0-9a-f]{40}', manifest['source_commit']):
        raise ValueError('Invalid source commit')
    if not re.fullmatch(r'https://github.com/newdarwindev/microfreelance/actions/runs/\d+', manifest['source_run']):
        raise ValueError('Invalid source run')
    if len(manifest['documents']) != 2 or {item['file'] for item in manifest['documents']} != expected - {'manifest.json'}:
        raise ValueError('Invalid document inventory')
    for item in manifest['documents']:
        if set(item) != {'file', 'bytes', 'sha256'}:
            raise ValueError('Unexpected document metadata')
        raw = (source / item['file']).read_bytes()
        if not raw.startswith(b'%PDF-') or b'%%EOF' not in raw[-1024:]:
            raise ValueError('Invalid PDF')
        if len(raw) != item['bytes'] or hashlib.sha256(raw).hexdigest() != item['sha256']:
            raise ValueError('PDF checksum mismatch')
    destination.mkdir(parents=True, exist_ok=True)
    for name in expected:
        shutil.copyfile(source / name, destination / name)
    (destination / 'index.html').write_text(f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Microfreelance — Tested workflow publications</title>
<style>body{{font:18px/1.6 system-ui;color:#142d39;background:#f5f3ed;max-width:1000px;margin:60px auto;padding:0 24px}}h1{{font-size:42px;line-height:1.1}}a{{color:#006963}}nav{{display:flex;gap:28px;flex-wrap:wrap;margin:32px 0}}code{{font-size:13px;overflow-wrap:anywhere}}iframe{{width:100%;height:75vh;border:1px solid #b8c8c6;margin:20px 0}}</style>
<h1>Tested workflows and UI preview</h1><p>These exact PDFs were generated and validated by the application CI. Additional product features are UI-only simulations without integrations.</p>
<nav><a href="whitepaper.pdf">Whitepaper PDF</a><a href="deck.pdf">Beamer presentation PDF</a><a href="manifest.json">Checksums and provenance</a></nav>
<p>Source commit: <code>{html.escape(manifest['source_commit'])}</code><br><a href="{html.escape(manifest['source_run'])}">Successful source Actions run</a> (repository access required)</p>
<h2>Whitepaper</h2><iframe title="Workflow whitepaper" src="whitepaper.pdf"></iframe>
<h2>Presentation</h2><iframe title="Workflow presentation" src="deck.pdf"></iframe>
<p><a href="../">Public product proposal</a></p></html>''')
    return '<section><h2>Tested workflow publications</h2><p><a href="workflows/index.html">View the CI-generated workflow whitepaper and presentation</a>. These documents describe tested implementation and the UI-only preview; they are separate from the broader product proposal above.</p></section>'
