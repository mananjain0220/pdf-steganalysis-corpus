# PDF Steganalysis Corpus v2 schema

Data and documentation: CC BY 4.0. This schema concerns v2 only; v1 is unchanged
at the pinned v1 commits in the dataset card.

## Tables and joins

| File | Unit and purpose |
|---|---|
| historical-{train,validation,test}.parquet | One original cover or verified historical stego document; default single-document detector inputs |
| historical-audit.parquet | Every one of the 32,456 v1 samples, including ineligible rows and overlapping exclusion reasons |
| covers.parquet | All 2,000 recovered archive covers, SHA-256, numeric archive basename, archive ID, parse status and split |
| task-index.parquet | Membership and target for each balanced per-method binary task and the attribution task |
| paired-deltas.parquet | Stego minus clean features; requires the original cover, not a default detector input |
| v1-v2-mapping.parquet | Stable historical sample IDs, changed cover IDs/splits and eligibility |
| near-duplicate-candidates.parquet | First-page difference-hash candidates, not asserted duplicate documents |
| synthetic-{train,validation,test}.parquet | Original demonstration covers and accepted stego outputs, with ZIP member paths |
| synthetic-attempts.parquet | All 3,960 attempts, including failures, never negative examples |
| baseline-predictions.parquet | Test predictions, task, model, feature set and true target; never predictor inputs |

Historical samples have `sample_id`, `cover_id`, `file_sha256`, `corpus`, `method`,
`binary_label`, `split` and 38 `feature_*` measurements. Binary label 0 means
the original pre-embedding document, **not malware-free**. Binary label 1
means an eligible embedded document. `method` is the attribution target;
`clean` is not an attribution class. `cover_id` is `cover_` plus the full
source SHA-256. Historical stego IDs are retained from v1.

Synthetic samples also contain `layout`, nullable `payload_bytes` and
`pdf_member`. A ZIP member is a relative path, not an external or private path.
The 120 covers are two pages each, 20 per layout. No historical PDF is in these ZIPs.

Join `historical-audit.sample_id` to sample tables, and `cover_id` to
`covers.cover_id`. `message_sha256` is the expected historical payload digest;
`extraction_status=pass` means freshly decoded UTF-8 bytes matched that digest.
No historical payload or key is published. Digests do not guarantee anonymity
of low-entropy payloads. `hash_match` and `source_unchanged` are nullable
validation evidence; `not_completed`/null is not success. The independent
`source-integrity.json` includes final hashes for documents with parser timeouts.

## Numeric predictor allowlist

Only the exact `feature_names` list in `summary-v2.json` is an approved baseline
predictor set. Exclude every ID, hash, method, label, corpus/layout, payload size,
generation/validation status, split, task target and paired delta.

All features below use the prefix `feature_` in sample tables.

| Measurement | Definition |
|---|---|
| file_size_bytes | Length of the input byte string |
| raw_count_{obj,endobj,stream,endstream,xref,startxref,eof,objstm,javascript} | Literal, case-sensitive non-overlapping counts of ` obj`, `endobj`, `stream`, `endstream`, `xref`, `startxref`, `%%EOF`, `/ObjStm`, `/JavaScript` |
| byte_entropy | Shannon entropy of the 256 byte frequencies, base 2, bits/byte |
| whitespace_fraction | Proportion of space, tab, CR, LF and form-feed bytes |
| ascii_fraction | Proportion of bytes 32 through 126 inclusive |
| numeric_token_count | Raw-byte matches of `(?<![\w.])[+-]?\d+(?:\.\d+)?(?![\w.])` |
| decimal_token_count | Same boundaries, but requires digits on both sides of a decimal point |
| decimal_precision_mean | Mean digit count after the decimal point; defined as 0 when there are no decimal tokens |
| eof_count / startxref_count | Literal counts; intentionally duplicate the corresponding v1-compatible raw counts |
| trailing_bytes | Bytes following the last `%%EOF`; null when absent |
| linearized_present | Raw occurrence of `/Linearized` |
| page_count / object_count | Length of pikepdf pages / indirect-object inventory |
| stream_count | Number of stream objects in the object inventory |
| image_count / font_count | Objects with `/Subtype /Image` or `/Type /Font` |
| annotation_count | Sum of page `/Annots` array lengths |
| form_present / xmp_present | Root contains `/AcroForm` / `/Metadata`, regardless of contents |
| xref_stream_present | Raw `/Type/XRef` or `/Type` followed by whitespace and `/XRef`; a lexical heuristic, not full xref-chain analysis |
| object_stream_present | Raw `/ObjStm` occurrence |
| page_width_mean / page_height_mean | Mean absolute MediaBox dimensions in PDF points, ignoring crop/rotation |
| page_area_std | Population standard deviation of MediaBox area in square points |
| stream_encoded_bytes | Sum of raw stream lengths |
| stream_decoded_bytes | Sum of decoded stream lengths; null if any stream cannot be decoded |
| stream_compression_ratio | Decoded divided by encoded stream bytes; null on decode failure or zero denominator |
| metadata_field_count | Number of DocInfo entries, not XMP fields |
| metadata_character_count | Sum of Python string lengths of DocInfo values; values themselves are discarded |

Raw counts can occur in compressed or non-content bytes; `stream` includes
`endstream`, and `xref` includes `startxref`. They are not semantic object counts.
Structure is measured with pikepdf `attempt_recovery=False`. Measurements that
could not be made are null, not invented zeros. A legitimate empty inventory
has count zero. `partial_stream_decode` explicitly flags undecodable streams.
Sample tables contain no document text or metadata strings.

The legacy static-feature collector was inspected: paired namespaces, broad
fallbacks and placeholder zeros made it unsuitable as a single-document
predictor interface. v2 retains the ten literal v1 byte definitions and
implements a separately versioned, null-aware numeric extractor; it does not
relabel the legacy feature arrays as newly measured data.

## Splits and tasks

Historical groups start from source SHA-256. Groups sharing any exact source
or output bytes are unioned. The smallest SHA-256 represents each component.
Compute SHA-256 of `v2:20260921:` plus the representative, take its first eight
hex digits modulo 100: 0-79 train, 80-89 validation, 90-99 test. All derivatives
stay together. This is approximately 80/10/10, not stratified per method.
Synthetic splitting uses the same formula with synthetic cover ID as group;
exact-byte isolation is independently checked. Do not mix synthetic and
historical configurations in a reported real-document generalization result.

Near-duplicate candidates have a 64-bit first-page difference hash with Hamming
distance <=3 (9x8 grayscale resize, adjacent-column comparisons). They are
flagged, not merged or certified identical; visually related documents may
remain across splits. Message categories are also shared across splits.

Binary task indexes choose the lexicographically smallest eligible sample ID
per (method, cover), then include that document and its original clean cover.
Each binary task therefore has balanced matched cases without repeated clean
rows. The model sees only one document, not both documents or their difference.
Attribution uses all verified stego samples, with natural class imbalance.
Classes lacking evaluation support are reported rather than fabricated.

## Status conventions

Workers: `pass`, `timeout`, `crashed`, `error`; incomplete fields use
`not_completed`. Parsing: `pass`, `failed`, `encrypted`, `not_run`.
Extraction: `pass`, `digest_mismatch`, `failed`, `missing_key`, `not_run`,
`not_applicable`, `not_completed`. Rendering: `pass`, `failed`, `not_requested`.
Synthetic embed errors (including unsupported/capacity-limited inputs) are
excluded; their attempt remains present. `accepted`/`eligible` is the sole gate,
not the existence of an output file. Historical rows may have multiple exclusion
reasons, so exclusion counts must not be summed as independent samples.
