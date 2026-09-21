# Release schema

`samples-{train,validation,test}.csv.gz` contains one row per existing PDF output
path referenced by at least one successful manifest attempt. Distinct paths can
contain identical bytes: use `output_sha256` to deduplicate within a split.

| Field | Meaning |
|---|---|
| sample_id | Stable identifier for corpus/method/chunk/output path |
| corpus | Original corpus family |
| method | Registry key, the method-attribution target |
| cover_id | Opaque category derived from the cover basename |
| message_id | Opaque category derived from the full payload digest |
| binary_label | Always 1; this release has no clean examples |
| split | Suggested train, validation, or test partition |
| evaluation_role | `scarce_class` for opsyn; `standard` otherwise |
| source_successful_attempts | Number of successful log rows referring to this path |
| output_sha256 | SHA-256 measured from the current local output bytes |
| file_size_bytes | Size measured from the current local output bytes |
| raw_count_* | Case-sensitive, non-overlapping byte-substring counts; see below |
| content_duplicate_count | Number of released paths with the same SHA-256 |

Feature substrings are ` obj`, `endobj`, `stream`, `endstream`, `xref`,
`startxref`, `%%EOF`, `/ObjStm`, and `/JavaScript`. These are literal counts,
not parsed object counts: `stream` includes occurrences inside `endstream`,
and `xref` includes occurrences inside `startxref`. Compressed content is
not decompressed. These ten numeric features (size plus nine counts) are a
minimal baseline, not a full structural or visual feature representation.

`attempts.csv.gz` contains every input manifest row, including repeated and
failed attempts. Fields are `attempt_id`, `corpus`, `method`, `cover_id`,
`message_id`, `split`, `reported_roundtrip_pass`, `output_present`, and
`sample_id`. An empty `sample_id` means no eligible sample was joined.
Failed attempts are not clean PDFs and must not be labelled as negative examples.
Round-trip pass is a historical log assertion, not a fresh extraction check.
Output files can have been overwritten by later attempts to the same path.

Identifiers are categories, not security guarantees or cryptographic
anonymization. Payload text, original message names, original cover names,
source URLs, local paths, raw errors, keys, and passwords are excluded.
Missing values are empty CSV cells; flags are integers 0 or 1.

## Splits and leakage

All occurrences of a cover basename, across both corpora, share a group.
Groups linked by identical output SHA-256 are merged. The lexicographically
smallest cover ID represents each connected component. SHA-256 of
`pdf-steganalysis-v1:` plus that representative is converted from its first
eight hexadecimal digits to an integer modulo 100: 0–79 train, 80–89
validation, 90–99 test. This is deterministic and approximately 80/10/10,
not a guarantee of balanced classes or exactly those proportions.

Source cover hashes are not available in this release. Equal basenames can
overgroup unrelated covers, and different basenames can hide duplicate covers.
Near-duplicate cover leakage has not been audited. The same message categories
occur across splits: this is a cover-group split, not an unseen-message test.
For a separate message generalization experiment, also hold out a message
category and exclude training covers appearing in its test partition.

Only `file_size_bytes` and `raw_count_*` are baseline predictor columns.
Keep identifiers, hashes, corpus names, generation statuses and duplicate
counts out of predictor inputs. Report per-method scores and class support.
Treat opsyn as a scarce class; it is included, not an established held-out
benchmark. No leaderboard or detector-performance claim is supplied.
