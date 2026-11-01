"""Read-only verification of a pinned cloud ZIP; never extracts, installs or edits data."""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path, PurePosixPath

SLOTS = {'learning-partner': 'student-a', 'learning-partner-yiyi': 'student-b'}


def verify(archive_path, expected_sha256, package_name, version):
    if package_name not in SLOTS or not re.fullmatch(r'[0-9a-f]{64}', expected_sha256):
        raise ValueError('Explicit known package and SHA256 are required')
    archive_path = Path(archive_path)
    if archive_path.is_symlink() or not archive_path.is_file():
        raise ValueError('Archive must be a regular file')
    digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    if digest != expected_sha256:
        raise ValueError('Archive SHA256 mismatch')
    with zipfile.ZipFile(archive_path) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            raise ValueError('Duplicate archive member')
        for info in infos:
            path = PurePosixPath(info.filename)
            if (path.is_absolute() or '..' in path.parts or '\\' in info.filename or
                    ':' in info.filename or path.as_posix() != info.filename or
                    info.is_dir() or (info.external_attr >> 16) & 0o170000 == 0o120000):
                raise ValueError('Unsafe archive member')
            if info.file_size > 10_000_000:
                raise ValueError('Unexpected asset size')
        if sum(i.file_size for i in infos) > 30_000_000:
            raise ValueError('Unexpected total size')
        release = json.loads(archive.read('CLOUD-RELEASE.json'))
        if (release.get('package_name'), release.get('owner_slot'), release.get('version'), release.get('mode')) != (package_name, SLOTS[package_name], version, 'cloud_native'):
            raise ValueError('Wrong target package, slot, version or mode')
        if release.get('schema_version') != 2:
            raise ValueError('Unsupported release manifest schema')
        if release.get('cloud_account_verified') is not False:
            raise ValueError('A distribution cannot certify actual account installation')
        hashes = release.get('sha256')
        if not isinstance(hashes, dict) or set(names) != set(hashes) | {'CLOUD-RELEASE.json'}:
            raise ValueError('Archive file set differs from manifest')
        for name, expected in hashes.items():
            if hashlib.sha256(archive.read(name)).hexdigest() != expected:
                raise ValueError('File SHA256 mismatch: ' + name)
        manifest = json.loads(archive.read('.codebuddy-plugin/plugin.json'))
        policy = json.loads(archive.read('cloud/update-policy.json'))
        if (manifest['name'], manifest['version'], policy['target_package'], policy['target_owner_slot'], policy['target_version']) != (package_name, version, package_name, SLOTS[package_name], version):
            raise ValueError('Conflicting install metadata')
        if manifest.get('dependencies') or '.mcp.json' in names:
            raise ValueError('Unexpected cloud runtime dependency')
        required = [x.removeprefix('./') for x in manifest['agents']] + [x.removeprefix('./') + '/SKILL.md' for x in manifest['skills']] + [manifest['avatar']]
        if len(manifest['skills']) != 6 or not set(required).issubset(hashes):
            raise ValueError('Missing agent, skill or avatar')
        if not policy.get('create_profile_only_if_absent') or policy.get('reimport_initial_memory_on_upgrade') is not False:
            raise ValueError('Unsafe profile upgrade policy')
    return {'artifact_verified': True, 'archive_sha256': digest, 'package_name': package_name,
            'owner_slot': SLOTS[package_name], 'version': version, 'file_count': len(names),
            'expert_updated': 'not_verified', 'cloud_account_verified': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--package', required=True, choices=tuple(SLOTS))
    parser.add_argument('--version', required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.archive, args.sha256, args.package, args.version), ensure_ascii=False, indent=2))
