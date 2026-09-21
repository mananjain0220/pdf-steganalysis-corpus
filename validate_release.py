#!/usr/bin/env python3
"""Validate published tables without opening any source PDF."""
import csv
import gzip
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

def read(path):
    with gzip.open(path, 'rt', newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
    summary = json.loads((root / 'summary.json').read_text())
    samples, cover_splits, hash_splits = [], {}, {}
    for split in ('train', 'validation', 'test'):
        rows = read(root / f'samples-{split}.csv.gz')
        assert len(rows) == summary['splits'][split]
        for row in rows:
            assert row['split'] == split and row['binary_label'] == '1'
            assert re.fullmatch(r'[0-9a-f]{64}', row['output_sha256'])
            for field in ('cover_id', 'message_id', 'sample_id'):
                assert re.fullmatch(field.replace('_id', '') + r'_[0-9a-f]{24}', row[field])
            for field in row:
                if field.startswith('raw_count_') or field == 'file_size_bytes':
                    assert int(row[field]) >= 0
            for mapping, key in [(cover_splits, row['cover_id']), (hash_splits, row['output_sha256'])]:
                assert mapping.setdefault(key, split) == split
        samples.extend(rows)
    by_id = {r['sample_id']: r for r in samples}
    assert len(samples) == len(by_id) == summary['output_paths']
    assert len(hash_splits) == summary['distinct_output_sha256']
    attempts = read(root / 'attempts.csv.gz')
    assert len(attempts) == len({r['attempt_id'] for r in attempts}) == summary['attempts']
    assert sum(int(r['reported_roundtrip_pass']) for r in attempts) == summary['reported_successful_attempts']
    references = Counter()
    for row in attempts:
        assert cover_splits.setdefault(row['cover_id'], row['split']) == row['split']
        if row['sample_id']:
            sample = by_id[row['sample_id']]
            assert row['reported_roundtrip_pass'] == row['output_present'] == '1'
            assert all(row[k] == sample[k] for k in ('cover_id', 'message_id', 'method', 'corpus', 'split'))
            references[row['sample_id']] += 1
    assert all(references[r['sample_id']] == int(r['source_successful_attempts']) for r in samples)
    duplicates = Counter(r['output_sha256'] for r in samples)
    assert all(duplicates[r['output_sha256']] == int(r['content_duplicate_count']) for r in samples)
    for line in (root / 'SHA256SUMS').read_text().splitlines():
        sha, name = line.split('  ', 1)
        assert Path(name).name == name
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == sha, name
    for path in root.iterdir():
        assert path.suffix.lower() not in ('.pdf', '.zip'), 'Unexpected PDF/ZIP'
    print(f'PASS: {len(attempts):,} attempts; {len(samples):,} samples; consistent joins, splits and checksums.')

if __name__ == '__main__':
    main()
