# AquaSol — Solubility Prediction App

A deployment-ready Streamlit application that estimates aqueous solubility directly from a molecular SMILES string. It implements the interpretable four-descriptor ESOL equation published by Delaney and calculates descriptors with RDKit.

## Live demo

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://solubilitypredictionapp-2mwbth3ham8rkic8jpj9f9.streamlit.app/)

## Features

- Single-molecule prediction from SMILES
- Molecular structure rendering and canonical SMILES
- Predicted logS, molarity, and an easy-to-read solubility class
- Interpretable molecular descriptors (MW, cLogP, rotatable bonds, aromatic proportion)
- CSV batch prediction for up to 500 molecules
- Downloadable prediction results
- Input validation, automated tests, and responsive Streamlit UI

## Run locally

Python 3.10–3.12 is recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run solubility_app.py
```

Then open `http://localhost:8501`.

## Input

Enter a valid [SMILES](https://en.wikipedia.org/wiki/Simplified_molecular-input_line-entry_system) string, for example:

| Molecule | SMILES |
|---|---|
| Ethanol | `CCO` |
| Benzene | `c1ccccc1` |
| Aspirin | `CC(=O)Oc1ccccc1C(=O)O` |

For batch mode, upload a CSV with a required `smiles` column and an optional `name` column.

## Model

The application uses:

```text
logS = 0.16 − 0.63(cLogP) − 0.0062(MW) + 0.066(RB) − 0.74(AP)
```

Here, logS is log10 mol/L, MW is molecular weight, RB is rotatable-bond count, and AP is aromatic heavy atoms divided by all heavy atoms.

Reference: Delaney, J. S. “ESOL: Estimating Aqueous Solubility Directly from Molecular Structure.” *J. Chem. Inf. Comput. Sci.* **2004**, 44, 1000–1005. [DOI: 10.1021/ci034243x](https://doi.org/10.1021/ci034243x)

The original model has substantial uncertainty (reported standard error around 0.97 log units). Results are screening estimates and not substitutes for experimental measurements. Solubility may change with pH, temperature, salt form, ionisation, and solid state.

## Tests

```bash
pip install pytest
pytest -q
```

## Deployment

AquaSol is available on Streamlit Community Cloud. The repository also includes an optional Docker Compose and Caddy configuration for self-hosting.

See [SELF_HOSTING.md](SELF_HOSTING.md) for the complete self-hosting guide.

## License

MIT — see [LICENSE](LICENSE).
