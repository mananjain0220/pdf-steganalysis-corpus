# Source and dependency provenance

New release scripts are authored for PDF Steganalysis Corpus v2 (MIT).
Data, documentation and original synthetic PDF content are CC BY 4.0.
Existing project embedding modules are staged separately: public redistribution
is gated on the maintainer's confirmation of ownership/permission. No license
is inferred merely because a file exists in the workspace.

The source bundle contains an explicit file allowlist and SHA-256 provenance
manifest; it excludes historical payload files, configuration/key files,
PDFs, private logs and unrelated lab materials. Existing project headers and
notices are retained. Any statement in implementation comments about high
security or undetectability is a legacy description, not a guarantee of this
release. The constructions are research implementations, not vetted encryption.

Dependencies are installed from their upstream distributions, not bundled as
executables or relicensed under MIT. Their license files are collected from
the tested installed distributions in `third_party_licenses/` in the source
bundle. In particular, PyMuPDF/MuPDF uses AGPL/commercial licensing; pikepdf
uses MPL-2.0 and includes dependencies with their own notices. NumPy, pandas,
scikit-learn, SciPy and ReportLab have BSD-style terms; PyArrow/Arrow uses
Apache-2.0; Pillow uses its upstream permissive license; cryptography has its
upstream Apache/BSD terms. Consult the included notices and upstream projects
for the exact versions/terms. This document is a provenance inventory, not a
legal determination about a downstream combined distribution.

Synthetic assets: all prose, tables, numeric data, vector drawings and raster
art are generated originally by `demo.py`. No external images or copied
documents are used. Covers reference standard PDF Helvetica fonts; no font
program is embedded or redistributed by the cover generator. Dependency
rendering/font resources retain their own upstream licenses.

Digital Corpora archive covers and their historical derivatives are not
included. The data license grants no rights in those third-party documents.
See the official collection and its linked terms before obtaining or reusing
source material. Malformed or encrypted PDFs should be handled in an isolated
research environment; "clean" only means pre-embedding.
