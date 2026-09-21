# Measured v2 results

Historical: 13,637 verified stego + 1,939 clean documents. All 32,456 v1 samples remain in the audit.

| Method | v1 records | Eligible historical | Train | Validation | Test | Accepted synthetic / 360 |
|---|---:|---:|---:|---:|---:|---:|
| a0_steganography | 2664 | 2602 | 2105 | 265 | 232 | 0 |
| tj_operator | 1973 | 1935 | 1539 | 214 | 182 | 0 |
| xref_steganography | 3984 | 3876 | 3100 | 372 | 404 | 360 |
| xmp_steganography | 3524 | 64 | 60 | 0 | 4 | 360 |
| operator_lsb | 2083 | 2024 | 1645 | 193 | 186 | 0 |
| orphanstream_steganography | 3984 | 0 | 0 | 0 | 0 | 340 |
| ws_steganography | 3581 | 0 | 0 | 0 | 0 | 300 |
| hybrid_steganography | 3597 | 0 | 0 | 0 | 0 | 300 |
| opsyn_steganography | 873 | 0 | 0 | 0 | 0 | 40 |
| numfmt_steganography | 3001 | 0 | 0 | 0 | 0 | 224 |
| whitetext_steganography | 3192 | 3136 | 2484 | 304 | 348 | 360 |

## Exclusions

18,819 distinct historical samples are excluded. The following counts overlap:

| Reason | Samples |
|---|---:|
| clean_unverified | 784 |
| extraction_missing_key | 15,036 |
| extraction_not_completed | 19 |
| extraction_not_run | 3,460 |
| missing_legacy_hash | 564 |
| source_integrity_unverified | 19 |
| stego_parse_failed | 3,460 |
| stego_parse_not_completed | 19 |
| timeout | 19 |
| v1_hash_unverified | 19 |

All five keyed methods require explicit local keys. None was supplied for historical validation; no default-key results are included. Opsyn is retained with actual audit/demo support, not discarded as a class.

Historical XMP: 3460 strict-parser failures; 64 eligible examples. The earlier byte-splicing writer changed stream lengths/cross-reference offsets and could mutate input PDFs. The already-corrected working-tree object-model writer is used for new synthetic generation, never to repair old corpus bytes.

The source-integrity report checks all 32,456 historical output hashes and 2,000 recovered cover hashes, including outputs whose parser timed out. Worker-level timeout records remain incomplete rather than being retroactively called parsing successes.

## Test-set baselines

Full = 38 allowlisted numeric single-document features. Size-only exposes serialization/size artifacts. Binary tracks are matched and balanced; test documents are never used to fit preprocessing or choose thresholds. No minimum performance was required.

| Task | Features | Model | AUROC | AUPRC | Balanced accuracy | Macro-F1 | Test N |
|---|---|---|---:|---:|---:|---:|---:|
| attribution | size_only | logistic_regression | — | — | 0.1922 | 0.1020 | 1356 |
| attribution | size_only | random_forest | — | — | 0.1557 | 0.1543 | 1356 |
| attribution | full | logistic_regression | — | — | 0.4004 | 0.2586 | 1356 |
| attribution | full | random_forest | — | — | 0.4078 | 0.3944 | 1356 |
| binary_a0_steganography | size_only | logistic_regression | 0.5134 | 0.5156 | 0.5000 | 0.3333 | 128 |
| binary_a0_steganography | size_only | random_forest | 0.5701 | 0.6132 | 0.5312 | 0.4101 | 128 |
| binary_a0_steganography | full | logistic_regression | 0.8245 | 0.8242 | 0.7266 | 0.7045 | 128 |
| binary_a0_steganography | full | random_forest | 0.8982 | 0.8963 | 0.7969 | 0.7964 | 128 |
| binary_operator_lsb | size_only | logistic_regression | 0.5116 | 0.5208 | 0.5000 | 0.3333 | 100 |
| binary_operator_lsb | size_only | random_forest | 0.4952 | 0.5125 | 0.5200 | 0.4907 | 100 |
| binary_operator_lsb | full | logistic_regression | 0.8916 | 0.8572 | 0.8000 | 0.7997 | 100 |
| binary_operator_lsb | full | random_forest | 0.9232 | 0.9253 | 0.8000 | 0.7960 | 100 |
| binary_tj_operator | size_only | logistic_regression | 0.5117 | 0.5178 | 0.5000 | 0.3333 | 102 |
| binary_tj_operator | size_only | random_forest | 0.5909 | 0.5980 | 0.5000 | 0.5000 | 102 |
| binary_tj_operator | full | logistic_regression | 0.8766 | 0.8738 | 0.7647 | 0.7509 | 102 |
| binary_tj_operator | full | random_forest | 0.9270 | 0.9253 | 0.8235 | 0.8179 | 102 |
| binary_whitetext_steganography | size_only | logistic_regression | 0.5057 | 0.5182 | 0.5000 | 0.3333 | 174 |
| binary_whitetext_steganography | size_only | random_forest | 0.4992 | 0.4915 | 0.4885 | 0.3863 | 174 |
| binary_whitetext_steganography | full | logistic_regression | 0.8884 | 0.8894 | 0.7816 | 0.7749 | 174 |
| binary_whitetext_steganography | full | random_forest | 0.9535 | 0.9467 | 0.8563 | 0.8538 | 174 |
| binary_xmp_steganography | — | insufficient_class_support | — | — | — | — | — |
| binary_xref_steganography | size_only | logistic_regression | 0.5080 | 0.5150 | 0.5000 | 0.3333 | 202 |
| binary_xref_steganography | size_only | random_forest | 0.5439 | 0.5446 | 0.5198 | 0.5031 | 202 |
| binary_xref_steganography | full | logistic_regression | 0.8904 | 0.8864 | 0.7822 | 0.7733 | 202 |
| binary_xref_steganography | full | random_forest | 0.9228 | 0.9170 | 0.8416 | 0.8389 | 202 |

Full confusion matrices, class supports and selected validation thresholds are in baseline-results.json. XMP has 60 training, zero validation and four test samples; its binary baseline is explicitly skipped because validation support is absent. Attribution includes all verified methods; the very small XMP test support limits interpretation.

## Synthetic attempt outcomes

120 covers; 3,960 attempts; 2,284 accepted stego outputs. No failed attempt is a clean example.

| Method | Embed pass | Parse pass | Render pass | Round-trip pass | Accepted |
|---|---:|---:|---:|---:|---:|
| a0_steganography | 48 | 48 | 48 | 0 | 0 |
| hybrid_steganography | 300 | 300 | 300 | 300 | 300 |
| numfmt_steganography | 224 | 224 | 224 | 224 | 224 |
| operator_lsb | 0 | 0 | 0 | 0 | 0 |
| opsyn_steganography | 40 | 40 | 40 | 40 | 40 |
| orphanstream_steganography | 340 | 340 | 340 | 340 | 340 |
| tj_operator | 0 | 0 | 0 | 0 | 0 |
| whitetext_steganography | 360 | 360 | 360 | 360 | 360 |
| ws_steganography | 300 | 300 | 300 | 300 | 300 |
| xmp_steganography | 360 | 360 | 360 | 360 | 360 |
| xref_steganography | 360 | 360 | 360 | 360 | 360 |

A0, TJ and operator-LSB have no accepted outputs for this cover/payload grid. Capacity or extraction failures are useful observations, not evidence that those methods never work. Synthetic performance is not reported as real-document generalization.

Near-duplicate screening flagged 131 cover pairs; flags are heuristic and have not been adjudicated. Exact-byte/cover-hash split isolation is checked; near-duplicate leakage and unseen-message generalization remain limitations.
