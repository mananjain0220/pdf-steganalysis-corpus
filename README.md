---
pretty_name: PDF Steganalysis Corpus
license: cc-by-4.0
size_categories:
  - 10K<n<100K
tags:
  - pdf
  - steganalysis
  - steganography
  - method-attribution
  - security-research
  - tabular
configs:
  - config_name: samples
    default: true
    data_files:
      - split: train
        path: samples-train.csv.gz
      - split: validation
        path: samples-validation.csv.gz
      - split: test
        path: samples-test.csv.gz
  - config_name: attempts
    data_files:
      - split: audit
        path: attempts.csv.gz
---

# PDF Steganalysis Corpus

**32,456 stego sample records across 11 methods, with output hashes and ten
freshly measured byte-level features.** The accompanying audit table preserves
74,400 embedding attempts from `cuing_methods_5k` and `new_methods_5k`.

This is a metadata/features release for PDF steganalysis research. It contains
no PDFs, raw payloads, passwords, keys, document text or original filenames.

- Canonical dataset: [Hugging Face](https://huggingface.co/datasets/manj0220/pdf-steganalysis-corpus)
- Companion code and mirrored tables: [GitHub](https://github.com/mananjain0220/pdf-steganalysis-corpus)
- Version: `v1.0-metadata-features`, 21 September 2026
- Maintainer: Manan Jain; contact via [GitHub issues](https://github.com/mananjain0220/pdf-steganalysis-corpus/issues)

## What this release supports

Method-attribution experiments, simple byte-feature baselines, analysis of
method-specific generation success, and reproducible export of public tables
from the original local corpus folders.

**There are no clean controls in v1.** All sample `binary_label` values are 1.
Failed embedding attempts are not negative examples. Binary stego-vs-clean
evaluation requires separately verified, matched clean controls. Normalization,
rendering, robustness, and independent extraction experiments require PDFs
obtained separately. No accuracy results or malware-ground-truth labels are
claimed by this release.

## Inventory

| Method | Attempts | Reported successful attempts | Distinct released samples |
|---|---:|---:|---:|
| a0_steganography | 10,800 | 4,036 | 2,664 |
| hybrid_steganography | 6,000 | 5,402 | 3,597 |
| numfmt_steganography | 6,000 | 4,520 | 3,001 |
| operator_lsb | 6,000 | 3,149 | 2,083 |
| opsyn_steganography | 6,000 | 1,328 | 873 |
| orphanstream_steganography | 6,000 | 5,976 | 3,984 |
| tj_operator | 10,800 | 3,001 | 1,973 |
| whitetext_steganography | 4,800 | 4,788 | 3,192 |
| ws_steganography | 6,000 | 5,376 | 3,581 |
| xmp_steganography | 6,000 | 5,286 | 3,524 |
| xref_steganography | 6,000 | 5,976 | 3,984 |
| **Total** | **74,400** | **48,838** | **32,456** |

The `5k` folder suffix is a generation target, not a per-class count.
Repeated payload fixtures produced multiple attempts referencing the same
output path. There are four distinct message categories and 2,000 cover
basename groups. All 32,456 current output SHA-256 values are distinct.
Every reported-success row resolves to an existing output in this snapshot.
These are observed counts, not extrapolations from chunk targets.

## Files and loading

| File | Contents |
|---|---|
| samples-train.csv.gz | 25,842 sample records and features |
| samples-validation.csv.gz | 3,113 sample records and features |
| samples-test.csv.gz | 3,501 sample records and features |
| attempts.csv.gz | 74,400 audit rows, including failed/repeated attempts |
| summary.json | Machine-readable counts |
| SCHEMA.md | Fields, feature definitions and split algorithm |
| REPRODUCIBILITY.md | Local export recipe and its limits |
| export_corpus.py | Standalone standard-library exporter |
| validate_release.py | Table and checksum validation |
| SHA256SUMS | SHA-256 of release files |

```python
from datasets import load_dataset

samples = load_dataset("manj0220/pdf-steganalysis-corpus", "samples")
attempts = load_dataset("manj0220/pdf-steganalysis-corpus", "attempts")
predictors = [c for c in samples["train"].column_names
              if c == "file_size_bytes" or c.startswith("raw_count_")]
# Method attribution target: samples["train"]["method"]
# Pin revision="<commit SHA>" for a reproducible experiment.
```

The CSV files can also be read with Python's `gzip` and `csv`, without an
external dataset library. Features are size plus nine literal substring
counts recomputed from current output bytes. They are not parsed PDF object
counts, rendered-image features, or a complete steganalysis feature set.

## Splits and evaluation

The approximately 80/10/10 split groups cover basenames across both corpus
families. Any groups sharing identical output bytes are merged before split
assignment. See [SCHEMA.md](SCHEMA.md) for the exact deterministic algorithm.
No cover ID or output SHA-256 crosses sample splits in this release.

Message categories are shared across partitions; unseen-message performance
is not measured by this split. Cover hashes and near-duplicate auditing are
still needed to strengthen leakage controls. Do not train on identifiers,
hashes, corpus names, historical success flags or duplicate counts. Keep
opsyn's 873 samples as a visibly scarce class and report per-class support.
There is no default class balancing, hidden test set or leaderboard.

## Provenance and validation

The corpus families correspond to four CUING methods and seven new-method
implementations. Project provenance identifies the Digital Corpora
[CC-MAIN-2021-31-PDF-UNTRUNCATED collection](https://digitalcorpora.org/corpora/file-corpora/cc-main-2021-31-pdf-untruncated/)
and archive IDs `0000` / `0001`. Per-row archive membership and source-cover
hashes have not been independently verified in this export.

Historical `success=True` is the generator's reported embed/extract round-trip
pass. This release verifies output existence and recomputes file hashes and
features, but does not rerun extraction. Later attempts may overwrite a path.
The legacy feature arrays have inconsistent row lengths and are not used.
Fresh export scripts are provided; a standalone exact PDF regeneration recipe
and historical generator revision/seed record are not yet available.

## Limitations and intended use

This is an imbalanced, implementation-specific research corpus with only four
message categories. A detector can learn implementation, document-source or
serialization artifacts. Generalization to unseen covers, embedders, payloads,
normalization tools and real deployments is unestablished. Steganographic
content does not by itself establish that a document is malicious.

The historical fixtures included synthetic command-shaped strings. Their text
and original names are omitted. The public tables contain opaque categories
instead. This release is intended for defensive research and reproducibility;
it is not a malware collection. Metadata identifiers are not guarantees of
anonymity. Please report label, provenance or release-content concerns to the
maintainer through the linked issue tracker.

## License and citation

Data and documentation: [CC BY 4.0](LICENSE-DATA.md).
Release scripts: [MIT](LICENSE-CODE). These licenses do not cover third-party
source PDFs, which are not included. Research is the intended use, not an
extra restriction on the open licenses.

Use [CITATION.cff](CITATION.cff), and record the exact dataset commit used:

> Jain, Manan (2026). PDF Steganalysis Corpus, v1.0-metadata-features.
> https://huggingface.co/datasets/manj0220/pdf-steganalysis-corpus

No paper DOI or publication status is asserted in this card. Paper-specific
citations can be added once the corresponding bibliographic records are verified.
