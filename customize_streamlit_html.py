"""Apply AquaSol metadata to Streamlit's initial HTML shell."""

from pathlib import Path

import streamlit


index_path = Path(streamlit.__file__).parent / "static" / "index.html"
html = index_path.read_text(encoding="utf-8")

default_title = "<title>Streamlit</title>"
aquasol_metadata = """<title>AquaSol | Molecular Solubility Prediction</title>
    <meta name="description" content="Predict aqueous molecular solubility from a SMILES structure with AquaSol." />
    <link rel="canonical" href="https://aquasol.azwarai.com/" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="https://aquasol.azwarai.com/" />
    <meta property="og:title" content="AquaSol | Molecular Solubility Prediction" />
    <meta property="og:description" content="Predict aqueous molecular solubility from a SMILES structure with AquaSol." />
    <meta property="og:site_name" content="AquaSol" />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="AquaSol | Molecular Solubility Prediction" />
    <meta name="twitter:description" content="Predict aqueous molecular solubility from a SMILES structure with AquaSol." />"""

if default_title not in html:
    raise RuntimeError(f"Expected Streamlit title was not found in {index_path}")

index_path.write_text(html.replace(default_title, aquasol_metadata, 1), encoding="utf-8")

