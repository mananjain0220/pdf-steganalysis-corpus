#!/usr/bin/env python3
"""Independent public-artifact consistency checks, including ZIP bytes."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
import pandas as pd

def check(args):
    root=args.data
    hist=pd.concat([pd.read_parquet(root/f'historical-{s}.parquet') for s in ('train','validation','test')])
    syn=pd.concat([pd.read_parquet(root/f'synthetic-{s}.parquet') for s in ('train','validation','test')])
    audit=pd.read_parquet(root/'historical-audit.parquet'); tasks=pd.read_parquet(root/'task-index.parquet')
    summary=json.loads((root/'summary-v2.json').read_text())
    assert pd.concat([hist,syn]).groupby('file_sha256').split.nunique().max()==1
    for frame in (hist,syn):
        assert frame.sample_id.is_unique
        assert frame.groupby('cover_id').split.nunique().max()==1
        assert frame.groupby('file_sha256').split.nunique().max()==1
        assert set(frame.binary_label.unique())=={0,1}
        assert frame[frame.binary_label==0].method.eq('clean').all()
        assert not frame[frame.binary_label==1].method.eq('clean').any()
        assert all(x.startswith('feature_') for x in summary['feature_names'])
        assert set(summary['feature_names'])<=set(frame.columns)
        assert not any(any(t in c for t in ('password','payload_text','original_filename','source_path')) for c in frame.columns)
    assert len(audit)==summary['historical_v1_samples']==32456
    assert set(audit[audit.eligible].sample_id)==set(hist[hist.binary_label==1].sample_id)
    assert audit[audit.eligible].parse_status.eq('pass').all()
    assert audit[audit.eligible].extraction_status.eq('pass').all()
    assert audit[audit.eligible].provenance_status.eq('legacy_md5_match').all()
    assert audit[audit.eligible].hash_match.eq(True).all()
    assert audit[audit.eligible].source_unchanged.eq(True).all()
    assert audit[audit.eligible].stego_page_count.eq(audit[audit.eligible].clean_page_count).all()
    assert len(hist[hist.binary_label==1])==summary['eligible_stego']
    assert len(hist[hist.binary_label==0])==summary['clean_samples']
    assert set(tasks.sample_id)<=set(hist.sample_id)
    for name,frame in tasks.groupby('task'):
        assert frame.sample_id.is_unique
        if name.startswith('binary_'):
            counts=frame.groupby(['split','target']).size().unstack(fill_value=0)
            assert counts['0'].equals(counts['1'])
    for label,filename in [(0,'synthetic-clean.zip'),(1,'synthetic-stego.zip')]:
        rows=syn[syn.binary_label==label]
        with zipfile.ZipFile(root/filename) as z:
            assert set(z.namelist())==set(rows.pdf_member)
            assert z.testzip() is None
            for _,r in rows.iterrows():
                assert hashlib.sha256(z.read(r.pdf_member)).hexdigest()==r.file_sha256
    attempts=pd.read_parquet(root/'synthetic-attempts.parquet')
    assert len(attempts)==3960 and len(syn[syn.binary_label==0])==120
    assert len(set(attempts.method))==11
    assert set(attempts[attempts.accepted].sample_id)==set(syn[syn.binary_label==1].sample_id)
    for status in ('parse_status','render_status','extraction_status'):
        assert attempts[attempts.accepted][status].eq('pass').all()
    assert attempts[attempts.accepted].message_sha256.eq(attempts[attempts.accepted].recovered_message_sha256).all()
    assert attempts[~attempts.accepted].failure_reason.notna().all()
    assert attempts.source_unchanged.all()
    for r in json.loads((root/'baseline-results.json').read_text())['results']:
        if r['status']=='pass':
            assert set(r['predictor_columns'])<=set(summary['feature_names'])
            assert r['seed']==20260921
    if (root/'SHA256SUMS-v2').exists():
        for line in (root/'SHA256SUMS-v2').read_text().splitlines():
            expected,name=line.split('  ',1)
            assert Path(name).name==name
            assert hashlib.sha256((root/name).read_bytes()).hexdigest()==expected,name
    checksum_status='pass' if (root/'SHA256SUMS-v2').exists() else 'not_present'
    print(json.dumps({'status':'PASS','historical_rows':len(hist),'synthetic_rows':len(syn),
                      'historical_audit_rows':len(audit),'synthetic_attempts':len(attempts),
                      'checksum_status':checksum_status,
                      'checks':['split isolation','labels','pair joins','balanced binary tracks','PDF archive hashes','feature allowlist']},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);check(p.parse_args())
