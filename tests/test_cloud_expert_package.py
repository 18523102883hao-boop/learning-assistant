import hashlib
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'workbuddy/experts/learning-partner'

class CloudExpertTests(unittest.TestCase):
    def test_cloud_release_has_no_local_mcp_requirement(self):
        manifest = json.loads((PACKAGE / '.codebuddy-plugin/plugin.json').read_text())
        self.assertEqual(manifest['version'], '1.2.0')
        self.assertNotIn('dependencies', manifest)
        self.assertFalse((PACKAGE / '.mcp.json').exists())
        self.assertIn('./skills/companion-knowledge', manifest['skills'])
        self.assertEqual(manifest['defaultInitPrompt'], manifest['quickPrompts'][0])

    def test_materials_are_present_with_traceable_release_limits(self):
        refs = PACKAGE / 'skills/companion-knowledge/references'
        course = json.loads((refs / 'course-source-index.json').read_text())
        self.assertEqual(len(course['files']), 113)
        self.assertEqual(len({r['source_id'] for r in course['files']}), 113)
        self.assertEqual(sum(r['chars'] for r in course['files']), 651139)
        self.assertTrue(all(len(r['sha256']) == 64 and 'source_directory' not in r for r in course['files']))
        books = json.loads((PACKAGE / 'skills/reading-companion/references/catalog.v3.json').read_text())
        guides = json.loads((refs / 'verified-book-guides.json').read_text())
        ids = {r['book_ref'] for r in books['records']}
        self.assertEqual(len(ids), 147)
        self.assertEqual(len(guides['records']), 3)
        for row in guides['records']:
            self.assertIn(row['book_ref'], ids)
            self.assertTrue(row['source_url'].startswith('https://'))
            self.assertFalse(row['edition_verified'])
        combined = (PACKAGE / 'cloud/云端资料合辑.md').read_text()
        for row in books['records']:
            self.assertIn(row['book_ref'], combined)
        for row in course['files']:
            self.assertIn(row['source_id'], combined)

    def test_personal_profile_is_blank_and_separate_from_readonly_materials(self):
        profile = (PACKAGE / 'cloud/伙伴档案-空白模板.md').read_text()
        manifest = json.loads((PACKAGE / '.codebuddy-plugin/plugin.json').read_text())
        slot = 'student-b' if manifest['name'].endswith('-yiyi') else 'student-a'
        self.assertIn('owner_slot: ' + slot, profile)
        self.assertIn('revision: 0', profile)
        for heading in ('兴趣与交流偏好', '正在做的作品', '阅读位置', '生活事件', '学习接续', '更正、忘记'):
            self.assertIn(heading, profile)
        self.assertIn('不能用空白模板覆盖', profile)
        self.assertNotIn('蓝星号', profile)

    def test_clean_archive_is_complete_reproducible_and_has_no_private_data(self):
        spec = importlib.util.spec_from_file_location('cloud_builder', ROOT / 'tools/build_cloud_bundle.py')
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        with tempfile.TemporaryDirectory() as temporary:
            first = Path(temporary) / 'first.zip'
            second = Path(temporary) / 'second.zip'
            result = builder.build(PACKAGE, first)
            builder.build(PACKAGE, second)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertFalse(result['cloud_account_verified'])
            with zipfile.ZipFile(first) as archive:
                for name, digest in result['sha256'].items():
                    self.assertEqual(hashlib.sha256(archive.read(name)).hexdigest(), digest)
                self.assertFalse(any(n.endswith(('.sqlite3', '.pyc', '.py')) or n.startswith('/') for n in archive.namelist()))
                self.assertIn('cloud/云端资料合辑.md', archive.namelist())
            with self.assertRaises(ValueError):
                builder.build(PACKAGE, first)
