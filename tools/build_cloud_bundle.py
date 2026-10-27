"""Build a deterministic cloud distribution from one reviewed expert package only."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path


def build(source, output):
    original = Path(source)
    if original.is_symlink() or not original.is_dir():
        raise ValueError('Select one valid expert directory')
    source = original.resolve()
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise ValueError('Use a new archive path; never overwrite')
    manifest = json.loads((source / '.codebuddy-plugin/plugin.json').read_text(encoding='utf-8'))
    if manifest.get('dependencies') or (source / '.mcp.json').exists():
        raise ValueError('Cloud-native release must not silently require a local or unverified MCP')
    files = {}
    for path in sorted(source.rglob('*')):
        if path.is_symlink():
            raise ValueError('No symlinks in a cloud release')
        if not path.is_file() or '__pycache__' in path.parts:
            continue
        relative = path.relative_to(source).as_posix()
        if path.suffix not in {'.md', '.json', '.png'}:
            raise ValueError('Unexpected runtime, executable or private asset: ' + relative)
        files[relative] = path.read_bytes()
    required = ['cloud/云端项目指令.md', 'cloud/云端资料合辑.md', 'cloud/伙伴档案-空白模板.md', 'CLOUD-SYNC.md',
                *[p.removeprefix('./') for p in manifest['agents']],
                *[p.removeprefix('./') + '/SKILL.md' for p in manifest['skills']], manifest['avatar']]
    if not all(path in files for path in required):
        raise ValueError('Missing cloud onboarding, agent, skill or avatar asset')
    refs = source / 'skills/companion-knowledge/references'
    course = json.loads((refs / 'course-source-index.json').read_text(encoding='utf-8'))
    books = json.loads((source / 'skills/reading-companion/references/catalog.v3.json').read_text(encoding='utf-8'))
    guides = json.loads((refs / 'verified-book-guides.json').read_text(encoding='utf-8'))
    methods = json.loads((refs / 'methods.json').read_text(encoding='utf-8'))
    release = {'schema_version': 1, 'package_name': manifest['name'], 'version': manifest['version'], 'mode': 'cloud_native',
               'cloud_account_verified': False, 'library_count': len(books['records']), 'course_source_count': len(course['files']),
               'verified_book_overview_count': len(guides['records']), 'method_count': len(methods['cards']),
               'sha256': {name: hashlib.sha256(content).hexdigest() for name, content in files.items()},
               'limits': 'Distribution completeness only. Cloud installation, retrieval, durable profile updates and memory are unverified until account tests pass.'}
    files['CLOUD-RELEASE.json'] = (json.dumps(release, ensure_ascii=False, indent=2) + '\n').encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation protects existing deliverables, including a racing writer.
    with output.open('xb') as stream:
        with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name, content in sorted(files.items()):
                info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100600 << 16
                archive.writestr(info, content)
    return release


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prepare one cloud expert package; does not install or upload private data')
    parser.add_argument('--source', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.source, args.output), ensure_ascii=False, indent=2))
