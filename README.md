# PDF Steganalysis Corpus v2

Benchmark companion for PDF steganalysis research. The dataset and original synthetic demonstration PDFs are hosted on [Hugging Face](https://huggingface.co/datasets/manj0220/pdf-steganalysis-corpus); this repository contains metadata, documentation, validation tools, and baseline results—not the PDF collection.

## Included

- Historical and synthetic sample metadata, audit records, and feature schemas
- Logistic-regression and random-forest baseline results
- Release validators and reproducibility scripts

## Reproduce the checks and baselines

Download the v2 release files from Hugging Face into `data/`. Extract `benchmark-details.zip` there and leave the PDF archives zipped.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python verify_release.py --data data
.venv/bin/python baselines.py --data data --out recomputed-results
```

See [RESULTS-v2.md](RESULTS-v2.md) for results and exclusions and [SCHEMA-v2.md](SCHEMA-v2.md) for table definitions. Use the exact dataset revision when reproducing or citing experiments.

## Important limitations

This release supports archive/table verification and baseline reproduction. It does not include embedding or extraction modules. “Clean” means before embedding, not malware-free; treat unfamiliar PDFs as untrusted and use isolated tooling. Do not train on identifiers, hashes, statuses, layout, payload size, split labels, or paired-only information.

## License and citation

Scripts are [MIT licensed](LICENSE-CODE). Documentation, results, and original synthetic content are [CC BY 4.0](LICENSE-DATA-v2.md). Dependency notices are in [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md) and `dependency-notices.zip`.

Please cite [CITATION.cff](CITATION.cff) and the exact dataset revision. Questions and corrections: [GitHub Issues](https://github.com/mananjain0220/pdf-steganalysis-corpus/issues).
