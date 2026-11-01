import hashlib
import importlib.util
import json
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'workbuddy/experts/learning-partner'


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'tools' / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class CloudIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.builder = module('build_cloud_bundle')
        self.verifier = module('verify_cloud_bundle')
        self.target = json.loads((PACKAGE / '.codebuddy-plugin/plugin.json').read_text())['name']
        self.archive = self.directory / 'cloud.zip'
        self.builder.build(PACKAGE, self.archive)

    def check_archive(self, path, target=None):
        return self.verifier.verify(path, hashlib.sha256(path.read_bytes()).hexdigest(), target or self.target, '1.3.0')

    def mutate(self, name, replacement, extra=None):
        result = self.directory / 'modified.zip'
        with zipfile.ZipFile(self.archive) as source, zipfile.ZipFile(result, 'w') as dest:
            for member in source.infolist():
                dest.writestr(member, replacement if member.filename == name else source.read(member))
            if extra:
                dest.writestr(*extra)
        return result

    def test_verifies_exact_artifact_without_claiming_install(self):
        result = self.check_archive(self.archive)
        self.assertTrue(result['artifact_verified'])
        self.assertFalse(result['cloud_account_verified'])
        self.assertEqual(result['expert_updated'], 'not_verified')

    def test_rejects_wrong_child_and_archive_digest(self):
        other = 'learning-partner' if self.target.endswith('-yiyi') else 'learning-partner-yiyi'
        with self.assertRaisesRegex(ValueError, 'Wrong target'):
            self.check_archive(self.archive, other)
        with self.assertRaisesRegex(ValueError, 'Archive SHA256'):
            self.verifier.verify(self.archive, '0' * 64, self.target, '1.3.0')

    def test_rejects_modified_asset_even_with_new_whole_zip_digest(self):
        changed = self.mutate('cloud/云端项目指令.md', b'changed')
        with self.assertRaisesRegex(ValueError, 'File SHA256'):
            self.check_archive(changed)

    def test_rejects_extra_member_and_path_traversal(self):
        changed = self.mutate('', b'', ('extra.md', b'extra'))
        with self.assertRaisesRegex(ValueError, 'file set'):
            self.check_archive(changed)
        changed = self.mutate('', b'', ('../other-child.md', b'extra'))
        with self.assertRaisesRegex(ValueError, 'Unsafe archive'):
            self.check_archive(changed)

    def test_rejects_stale_source_manifest(self):
        clone = self.directory / 'source'
        shutil.copytree(PACKAGE, clone)
        self.builder.write_manifest(clone)
        (clone / 'CHANGELOG.md').write_text('unreviewed change')
        with self.assertRaisesRegex(ValueError, 'Stale or modified'):
            self.builder.build(clone, self.directory / 'stale.zip')

    def test_rejects_conflicting_account_policy(self):
        clone = self.directory / 'source'
        shutil.copytree(PACKAGE, clone)
        path = clone / 'cloud/update-policy.json'
        policy = json.loads(path.read_text())
        policy['target_owner_slot'] = 'student-a' if policy['target_owner_slot'] == 'student-b' else 'student-b'
        path.write_text(json.dumps(policy))
        with self.assertRaisesRegex(ValueError, 'Account target'):
            self.builder.build(clone, self.directory / 'wrong.zip')


if __name__ == '__main__':
    unittest.main()
