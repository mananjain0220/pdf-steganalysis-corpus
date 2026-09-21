# Rebuilding the public export

Python 3.10+; standard library only. Obtain the two original corpus folders
through your own authorized access, then run:

```sh
python3 export_corpus.py --cuing /path/to/cuing_methods_5k \
  --new /path/to/new_methods_5k --out /path/to/new-export
```

The exporter reads local PDFs as bytes; it never opens a viewer or executes
embedded content. It checks method names and manifest fields, keeps failed
attempts, merges repeated references to one output path, recomputes SHA-256
and literal byte features, and writes deterministic gzip CSV files. It does
not use legacy feature arrays, which may omit rows for failed attempts.

The original manifests are the source of historical method and round-trip
labels. Successful extraction is not rerun and original generation code
versions, random seeds, and key choices are not recoverable from the public
tables. The output hashes identify bytes, not proof that a historical label
is correct. Review a matched, locally accessible subset before making strong
claims about detector accuracy.

## Cover source and PDF regeneration status

Project provenance identifies the Digital Corpora
[CC-MAIN-2021-31-PDF-UNTRUNCATED corpus](https://digitalcorpora.org/corpora/file-corpora/cc-main-2021-31-pdf-untruncated/)
and archive IDs `0000` / `0001`. These are source-level provenance notes;
the release does not certify the archive assignment of each row.
Acquire source files from the provider under applicable terms. This release
does not redistribute source or stego PDFs or grant rights to those documents.

This package reproduces the metadata/features export from local outputs.
It does not yet provide a standalone, byte-identical PDF regeneration recipe.
The private generation suite and historical messages are not bundled.
Future regeneration should use explicitly benign text fixtures and a recorded
generator revision, dependency versions, seeds, cover SHA-256 and key policy.
Such regenerated samples would be a new version with new output hashes.

## Validation

```sh
python3 validate_release.py .
```

The validator checks totals, unique row IDs, sample/attempt joins, split
isolation by cover and output hash, numeric feature fields, and checksums.
It does not validate PDF extraction, visual equivalence or copyright status.
