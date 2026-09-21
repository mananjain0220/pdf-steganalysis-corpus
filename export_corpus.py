#!/usr/bin/env python3
"""Export allowlisted labels and independently measured byte features. Stdlib only."""
import argparse
import csv
import gzip
import hashlib
import json
import re
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

METHODS = {
    'a0_steganography', 'tj_operator', 'xref_steganography', 'xmp_steganography',
    'operator_lsb', 'orphanstream_steganography', 'ws_steganography',
    'hybrid_steganography', 'opsyn_steganography', 'numfmt_steganography',
    'whitetext_steganography',
}
TOKENS = {'obj': b' obj', 'endobj': b'endobj', 'stream': b'stream',
          'endstream': b'endstream', 'xref': b'xref', 'startxref': b'startxref',
          'eof': b'%%EOF', 'objstm': b'/ObjStm', 'javascript': b'/JavaScript'}

def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()

def split_for(cover_id):
    bucket = int(digest('pdf-steganalysis-v1:' + cover_id)[:8], 16) % 100
    return 'train' if bucket < 80 else 'validation' if bucket < 90 else 'test'

def measure(path):
    data = path.read_bytes()
    return {'output_sha256': hashlib.sha256(data).hexdigest(),
            'file_size_bytes': len(data),
            **{'raw_count_' + key: data.count(token) for key, token in TOKENS.items()}}

def write_csv(path, rows, fields):
    with path.open('wb') as raw:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as gz:
            import io
            with io.TextIOWrapper(gz, encoding='utf-8', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cuing', required=True, type=Path)
    ap.add_argument('--new', required=True, type=Path)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--workers', type=int, default=4)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    attempts, artifacts, payloads = [], {}, set()
    counters = defaultdict(Counter)
    for corpus, root in [('cuing_methods_5k', args.cuing), ('new_methods_5k', args.new)]:
        manifests = sorted(root.glob('*/chunk_*/manifest.csv'))
        if not manifests:
            raise ValueError('No manifests for ' + corpus)
        for manifest in manifests:
            method = manifest.parent.parent.name
            if method not in METHODS:
                raise ValueError('Unrecognized method directory')
            with manifest.open(newline='', encoding='utf-8-sig') as f:
                rows = list(csv.DictReader(f))
            for number, row in enumerate(rows, 1):
                assert row['method_key'] == method
                cover = row['original_filename']
                assert re.fullmatch(r'[0-9]+\.pdf', cover), 'Unexpected cover basename'
                payload = row['message_sha256']
                assert re.fullmatch(r'[0-9a-f]{64}', payload)
                payloads.add(payload)
                # Opaque categories, not a claim that hashing low-entropy inputs anonymizes them.
                cover_id = 'cover_' + digest('cover-basename:' + cover)[:24]
                message_id = 'message_' + digest('message-category:' + payload)[:24]
                assert row['success'] in ('True', 'False')
                success = row['success'] == 'True'
                output = row['output_filename']
                if output:
                    assert Path(output).name == output and output.endswith('.pdf')
                path = manifest.parent / 'stego_pdfs' / output if output else None
                exists = bool(path and path.is_file())
                sample_id = ''
                if success and exists:
                    key = str(path.resolve())
                    sample_id = 'sample_' + digest('/'.join([corpus, method, manifest.parent.name, output]))[:24]
                    entry = {'sample_id': sample_id, 'corpus': corpus, 'method': method,
                             'cover_id': cover_id, 'message_id': message_id,
                             'binary_label': 1, 'split': split_for(cover_id),
                             'evaluation_role': 'scarce_class' if method == 'opsyn_steganography' else 'standard',
                             'source_successful_attempts': 0}
                    if key in artifacts:
                        assert artifacts[key][1]['cover_id'] == cover_id
                        assert artifacts[key][1]['message_id'] == message_id, 'Payload ID collision'
                    else:
                        artifacts[key] = (path, entry)
                    artifacts[key][1]['source_successful_attempts'] += 1
                counters[method]['attempts'] += 1
                counters[method]['reported_successes'] += int(success)
                counters[method]['missing_successful_outputs'] += int(success and not exists)
                attempts.append({'attempt_id': 'attempt_' + digest('/'.join([corpus, method, manifest.parent.name, str(number)]))[:24],
                                 'corpus': corpus, 'method': method, 'cover_id': cover_id,
                                 'message_id': message_id, 'split': split_for(cover_id),
                                 'reported_roundtrip_pass': int(success),
                                 'output_present': int(exists), 'sample_id': sample_id})
    print(f'{len(attempts)} attempts; measuring {len(artifacts)} distinct output paths', flush=True)
    samples = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        entries = list(artifacts.values())
        for i, ((path, row), features) in enumerate(zip(entries, pool.map(measure, (p for p, _ in entries))), 1):
            samples.append({**row, **features})
            if i % 2000 == 0:
                print(f'Measured {i}/{len(entries)}', flush=True)
    # Identical bytes must not cross splits, even when cover basenames differ.
    parent = {r['cover_id']: r['cover_id'] for r in samples}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    by_hash = {}
    for r in samples:
        sha, cover = r['output_sha256'], r['cover_id']
        if sha in by_hash:
            a, b = find(cover), find(by_hash[sha])
            parent[max(a, b)] = min(a, b)
        else:
            by_hash[sha] = cover
    for row in samples + attempts:
        row['split'] = split_for(find(row['cover_id']) if row['cover_id'] in parent else row['cover_id'])
    content_groups = Counter(r['output_sha256'] for r in samples)
    for row in samples:
        row['content_duplicate_count'] = content_groups[row['output_sha256']]
        counters[row['method']]['output_paths'] += 1
    summary = {'release': 'v1.0-metadata-features', 'attempts': len(attempts),
               'reported_successful_attempts': sum(r['reported_roundtrip_pass'] for r in attempts),
               'output_paths': len(samples), 'distinct_output_sha256': len(content_groups),
               'cover_basename_groups': len({r['cover_id'] for r in attempts}),
               'message_categories': len(payloads), 'clean_samples': 0,
               'splits': dict(Counter(r['split'] for r in samples)),
               'methods': dict(sorted(counters.items()))}
    for split in ('train', 'validation', 'test'):
        write_csv(args.out / f'samples-{split}.csv.gz', [r for r in samples if r['split'] == split], list(samples[0]))
    write_csv(args.out / 'attempts.csv.gz', attempts, list(attempts[0]))
    (args.out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    main()
