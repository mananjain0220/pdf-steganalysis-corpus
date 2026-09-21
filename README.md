# PDF Steganalysis Corpus v2 — benchmark companion

Code, documentation and measured results for PDF steganalysis research.
Download the data and original synthetic demonstration PDFs from the
[Hugging Face dataset](https://huggingface.co/datasets/manj0220/pdf-steganalysis-corpus).
This repository package deliberately contains no PDF collection or feature-table mirror.

## Contents

- Historical benchmark: 13,637 verified stego records across six methods and
  1,939 clean originals, with 38 numeric single-document features.
- All 32,456 historical sample records remain in the downloadable audit.
- Synthetic demonstration: 120 original covers and 2,284 verified stego PDFs;
  all 3,960 attempts are recorded, including failures.
- Logistic regression and random forest baselines, with full-feature and
  size-only controls, training-only preprocessing and validation thresholds.

"Clean" means before embedding, not malware-free. Historical crawl-derived
PDFs, payload text, keys and private configurations are not redistributed.
Five keyed methods lack explicit historical keys and remain outside the
verified historical track. Malformed/unverifiable samples remain in the audit.
Synthetic examples do not establish generalization to real documents.

## Run

Download the compact v2 files from Hugging Face into `data/`. Extract
`benchmark-details.zip` into that same directory; leave the two PDF ZIPs zipped.
The current package is a companion to that data release, not proof that the
maintainer has already uploaded it. No credentials are required for public downloads.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python verify_release.py --data data
.venv/bin/python baselines.py --data data --out recomputed-results
```

Compare results with `baseline-results.json`. The tested environment is
Python 3.14.5, macOS arm64; dependencies are pinned. The baseline and table/ZIP
validator do not require the private embedding suite. `runtime.py` supplies
seed and JSON helpers; its method registry is unused by these two commands.

See [RESULTS-v2.md](RESULTS-v2.md) for scores, counts and exclusions and
[SCHEMA-v2.md](SCHEMA-v2.md) for tables, features, statuses and split definitions.
The exact predictor allowlist is in the downloaded `summary-v2.json`.
Use `task-index.parquet` for balanced per-method binary tasks; attribution
uses verified stego samples. Never train on identifiers, hashes, statuses,
layout, payload size, splits or paired-only information.

## Scope and limitations

Generation/extraction modules are not included because their redistribution
license is awaiting maintainer confirmation. This package therefore supports
baseline reproduction and table/archive verification, not standalone embedding
or independent decoding. Stored validation evidence is available in the data
release, but this validator does not rerun rendering or payload extraction.

Cover hashes group historical splits; exact-byte groups are merged. The 131
near-duplicate candidates are not adjudicated. Shared message categories,
serialization artifacts, class imbalance and scarce XMP support limit results.
No minimum accuracy was required. No normalization or malware-detection claim
is made. Treat unfamiliar PDFs as untrusted and use isolated research tooling.

## Versioning

The v1 source release remains at
[`4401d97e4789bc7e3304b7c0448a62f40e675492`](https://github.com/mananjain0220/pdf-steganalysis-corpus/tree/4401d97e4789bc7e3304b7c0448a62f40e675492).
The v1 dataset remains at
[`183403f2768dfe0eb6a2ef983db1876fb95c55a7`](https://huggingface.co/datasets/manj0220/pdf-steganalysis-corpus/tree/183403f2768dfe0eb6a2ef983db1876fb95c55a7).
This upload package does not duplicate v1 files. Existing repository files are
not automatically removed by uploading this package. Pin revisions when citing
experiments; v2 has changed eligibility and splits.

## Licensing and contact

New scripts: [MIT](LICENSE-CODE). Project documentation/results and original
synthetic content: [CC BY 4.0](LICENSE-DATA-v2.md). Dependencies retain their
own terms; see [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md) and the exact
installed-distribution notices in `dependency-notices.zip`. Licenses do not
grant rights to third-party source PDFs. Research use is an intention, not an
additional license restriction. Steganography is dual-use; this is not an exploit pack.

Use [CITATION.cff](CITATION.cff) and the exact dataset revision. Maintainer:
Manan Jain; contact through [GitHub issues](https://github.com/mananjain0220/pdf-steganalysis-corpus/issues).
No unverified paper DOI or publication status is asserted.
