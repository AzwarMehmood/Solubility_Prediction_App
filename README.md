# AquaSol — Solubility Prediction App

A deployment-ready Streamlit application that estimates aqueous solubility directly from a molecular SMILES string. It implements the interpretable four-descriptor ESOL equation published by Delaney and calculates descriptors with RDKit.

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

## Deploy on Streamlit Community Cloud

1. Sign in at [share.streamlit.io](https://share.streamlit.io/) with GitHub.
2. Choose **Create app** and select this repository.
3. Set the branch to `master` (or the merged feature branch) and the entry point to `solubility_app.py`.
4. Deploy. Streamlit installs the packages in `requirements.txt` automatically.

For a memorable URL, open **Manage app → Settings → General** and request
`aquasol.streamlit.app` (subject to availability).

## Deploy on your own server

The repository includes a production Docker Compose setup with Caddy handling HTTPS automatically.

1. Point an `A`/`AAAA` DNS record for `aquasol.azwarai.com` to the server.
2. Copy `.env.example` to `.env` and confirm the domain.
3. Allow inbound TCP ports 80 and 443.
4. Run `docker compose up -d --build`.

See [SELF_HOSTING.md](SELF_HOSTING.md) for setup, verification, updates, logs, and rollback guidance.

## License

MIT — see [LICENSE](LICENSE).
