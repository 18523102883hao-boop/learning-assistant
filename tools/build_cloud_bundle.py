"""Deterministic, account-targeted distribution. Never installs or reads child data."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

TARGETS = {'learning-partner': 'student-a', 'learning-partner-yiyi': 'student-b'}
MANIFEST = 'CLOUD-RELEASE.json'


def collect(source):
    original = Path(source)
    if original.is_symlink() or not original.is_dir():
        raise ValueError('Select one valid expert directory')
    source = original.resolve()
    manifest = json.loads((source / '.codebuddy-plugin/plugin.json').read_text(encoding='utf-8'))
    if manifest.get('dependencies') or (source / '.mcp.json').exists():
        raise ValueError('Cloud-native release must not require a local or unverified MCP')
    files = {}
    for path in sorted(source.rglob('*')):
        if path.is_symlink():
            raise ValueError('No symlinks in a cloud release')
        if not path.is_file() or '__pycache__' in path.parts:
            continue
        relative = path.relative_to(source).as_posix()
        if relative == MANIFEST:
            continue  # The manifest hashes every other file, not itself.
        if path.suffix not in {'.md', '.json', '.png'}:
            raise ValueError('Unexpected runtime, executable or private asset: ' + relative)
        files[relative] = path.read_bytes()
    required = ['cloud/云端项目指令.md', 'cloud/云端资料合辑.md', 'cloud/伙伴档案-空白模板.md',
                'cloud/update-policy.json', 'CLOUD-SYNC.md', 'CHANGELOG.md', 'DESIGN-SOURCES.md',
                *[p.removeprefix('./') for p in manifest['agents']],
                *[p.removeprefix('./') + '/SKILL.md' for p in manifest['skills']], manifest['avatar']]
    if not all(path in files for path in required):
        raise ValueError('Missing cloud onboarding, policy, agent, skill or avatar asset')
    policy = json.loads(files['cloud/update-policy.json'])
    slot = TARGETS.get(manifest['name'])
    if not slot or (policy.get('target_package'), policy.get('target_owner_slot'), policy.get('target_version')) != (manifest['name'], slot, manifest['version']):
        raise ValueError('Account target, package or version mismatch')
    if not policy.get('create_profile_only_if_absent') or policy.get('reimport_initial_memory_on_upgrade') is not False:
        raise ValueError('Upgrade must preserve the existing private profile and initial-memory state')
    refs = source / 'skills/companion-knowledge/references'
    course = json.loads((refs / 'course-source-index.json').read_text(encoding='utf-8'))
    books = json.loads((source / 'skills/reading-companion/references/catalog.v3.json').read_text(encoding='utf-8'))
    guides = json.loads((refs / 'verified-book-guides.json').read_text(encoding='utf-8'))
    methods = json.loads((refs / 'methods.json').read_text(encoding='utf-8'))
    cards = json.loads(files['skills/homework-help/references/support-cards.json'])
    release = {'schema_version': 2, 'package_name': manifest['name'], 'owner_slot': slot,
               'version': manifest['version'], 'mode': 'cloud_native',
               'release_status': 'ready_for_adult_cloud_trial', 'cloud_account_verified': False,
               'library_count': len(books['records']), 'course_source_count': len(course['files']),
               'verified_book_overview_count': len(guides['records']), 'method_count': len(methods['cards']),
               'original_math_support_card_count': len(cards['cards']),
               'previous_source_commit': policy['previous_source_commit'],
               'sha256': {name: hashlib.sha256(content).hexdigest() for name, content in files.items()},
               'limits': 'Package completeness and integrity only. Actual cloud installation, retrieval, durable profile updates and native memory require separate account tests.'}
    return files, release


def write_manifest(source):
    _, release = collect(source)
    (Path(source) / MANIFEST).write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def build(source, output):
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise ValueError('Use a new archive path; never overwrite')
    files, release = collect(source)
    existing = Path(source) / MANIFEST
    if existing.exists() and json.loads(existing.read_text(encoding='utf-8')) != release:
        raise ValueError('Stale or modified source manifest; review changes and regenerate explicitly')
    files[MANIFEST] = (json.dumps(release, ensure_ascii=False, indent=2) + '\n').encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('xb') as stream:
        with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name, content in sorted(files.items()):
                info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100600 << 16
                archive.writestr(info, content)
    return release


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prepare one cloud expert package; never installs or uploads private data')
    parser.add_argument('--source', required=True)
    parser.add_argument('--output')
    parser.add_argument('--write-manifest', action='store_true', help='Explicitly regenerate source integrity manifest after review')
    args = parser.parse_args()
    if not args.write_manifest and not args.output:
        parser.error('Provide --output and/or --write-manifest')
    release = write_manifest(args.source) if args.write_manifest else None
    if args.output:
        release = build(args.source, args.output)
    print(json.dumps({k: v for k, v in release.items() if k != 'sha256'}, ensure_ascii=False, indent=2))
