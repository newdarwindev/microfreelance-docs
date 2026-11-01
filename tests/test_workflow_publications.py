import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('workflow_publications', Path(__file__).parents[1] / 'scripts/workflow_publications.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class WorkflowPublicationTest(unittest.TestCase):
    def fixture(self, root):
        source = root / 'input'
        source.mkdir()
        raw = b'%PDF-1.5\nsynthetic fixture\n%%EOF'
        documents = []
        for name in ['whitepaper.pdf', 'deck.pdf']:
            (source / name).write_bytes(raw)
            documents.append({'file': name, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
        (source / 'manifest.json').write_text(json.dumps({'source_commit': 'a' * 40,
            'source_run': 'https://github.com/newdarwindev/microfreelance/actions/runs/123', 'documents': documents}))
        return source

    def test_only_valid_pdfs_and_metadata_are_staged(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.fixture(root)
            self.assertIn('workflows/index.html', module.stage(source, root / 'out'))
            self.assertEqual({'index.html', 'whitepaper.pdf', 'deck.pdf', 'manifest.json'}, {p.name for p in (root / 'out').iterdir()})

    def test_extra_private_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.fixture(root)
            (source / 'server.log').write_text('must never publish')
            with self.assertRaises(ValueError):
                module.stage(source, root / 'out')
            self.assertFalse((root / 'out').exists())

    def test_changed_pdf_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.fixture(root)
            (source / 'deck.pdf').write_bytes(b'%PDF-1.5\nmodified\n%%EOF')
            with self.assertRaisesRegex(ValueError, 'checksum'):
                module.stage(source, root / 'out')
