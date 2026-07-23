"""Interactive Streamlit interface for the ESOL predictor."""

from __future__ import annotations

import io

import pandas as pd
import streamlit as st
from rdkit.Chem import Draw

from solubility_model import SolubilityPrediction, predict_solubility


st.set_page_config(
    page_title="AquaSol | Molecular Solubility",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp {background: linear-gradient(145deg, #f7fbff 0%, #eef8f5 100%);}
    .hero {padding: 2rem 2.2rem; border-radius: 24px; color: white;
      background: linear-gradient(120deg, #073b4c, #087e8b 55%, #3bb6a3);
      box-shadow: 0 16px 45px rgba(7,59,76,.18); margin-bottom: 1.4rem;}
    .hero h1 {font-size: 2.65rem; margin: 0; letter-spacing: -.04em;}
    .hero p {font-size: 1.05rem; max-width: 720px; opacity: .9; margin-bottom: 0;}
    .result-card {background: white; border: 1px solid #dceae8; border-radius: 18px;
      padding: 1.3rem; box-shadow: 0 8px 24px rgba(7,59,76,.07);}
    div[data-testid="stMetric"] {background: rgba(255,255,255,.82); border: 1px solid #dceae8;
      padding: 1rem; border-radius: 15px;}
    </style>
    """,
    unsafe_allow_html=True,
)


EXAMPLES = {
    "Caffeine": "Cn1c(=O)c2c(ncn2C)n(C)c1=O",
    "Aspirin": "CC(=O)Oc1ccccc1C(=O)O",
    "Acetaminophen": "CC(=O)NC1=CC=C(C=C1)O",
    "Ibuprofen": "CC(C)Cc1ccc(cc1)[C@@H](C)C(=O)O",
    "Benzene": "c1ccccc1",
    "Ethanol": "CCO",
}


def result_panel(prediction: SolubilityPrediction) -> None:
    """Render one prediction and its molecular descriptors."""
    left, right = st.columns([0.9, 1.5], gap="large")
    with left:
        st.image(Draw.MolToImage(prediction.molecule, size=(440, 340)), use_container_width=True)
        st.caption(f"Canonical SMILES: `{prediction.canonical_smiles}`")

    with right:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.subheader(f"{prediction.classification.emoji} {prediction.classification.label}")
        c1, c2 = st.columns(2)
        c1.metric("Predicted logS", f"{prediction.log_s:.2f}", help="Base-10 log of molar solubility")
        c2.metric("Estimated molarity", prediction.formatted_molarity)
        st.progress(prediction.classification.score, text=prediction.classification.description)
        st.markdown("#### Molecular descriptors")
        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Molecular weight", f"{prediction.molecular_weight:.1f} Da")
        d2.metric("cLogP", f"{prediction.log_p:.2f}")
        d3.metric("Rotatable bonds", str(prediction.rotatable_bonds))
        d4.metric("Aromatic proportion", f"{prediction.aromatic_proportion:.2f}")
        st.markdown("</div>", unsafe_allow_html=True)


with st.sidebar:
    st.markdown("## 💧 AquaSol")
    st.caption("Fast, structure-only aqueous solubility estimates")
    st.divider()
    page = st.radio("Workspace", ["Single molecule", "Batch prediction", "About the model"])
    st.divider()
    st.info(
        "This is a screening estimate, not an experimental measurement. "
        "Do not use it as the sole basis for clinical, safety, or formulation decisions."
    )

st.markdown(
    """
    <div class="hero">
      <h1>AquaSol</h1>
      <p>Turn a molecular structure into an interpretable aqueous-solubility estimate in seconds.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if page == "Single molecule":
    st.subheader("Predict a molecule")
    example_name = st.selectbox("Start with an example", ["Custom SMILES", *EXAMPLES])
    default_smiles = "" if example_name == "Custom SMILES" else EXAMPLES[example_name]
    with st.form("single_prediction"):
        smiles = st.text_input(
            "SMILES string",
            value=default_smiles,
            placeholder="For example: CCO or CC(=O)Oc1ccccc1C(=O)O",
            help="Enter a valid SMILES molecular representation.",
        )
        submitted = st.form_submit_button("Predict solubility", type="primary", use_container_width=True)

    if submitted:
        try:
            result_panel(predict_solubility(smiles))
        except ValueError as exc:
            st.error(str(exc))

elif page == "Batch prediction":
    st.subheader("Batch prediction")
    st.write("Upload a CSV containing a `smiles` column. A `name` column is optional.")
    template = pd.DataFrame({"name": list(EXAMPLES)[:3], "smiles": list(EXAMPLES.values())[:3]})
    st.download_button(
        "Download CSV template",
        data=template.to_csv(index=False),
        file_name="solubility_template.csv",
        mime="text/csv",
    )
    uploaded = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded is not None:
        try:
            frame = pd.read_csv(uploaded)
            if "smiles" not in frame.columns:
                raise ValueError("The CSV must include a column named 'smiles'.")
            if len(frame) > 500:
                raise ValueError("Please upload no more than 500 molecules at a time.")

            rows = []
            for _, source in frame.iterrows():
                try:
                    prediction = predict_solubility(str(source["smiles"]))
                    rows.append({
                        **source.to_dict(),
                        "canonical_smiles": prediction.canonical_smiles,
                        "predicted_logS": round(prediction.log_s, 3),
                        "solubility_class": prediction.classification.label,
                        "estimated_molarity_M": prediction.molarity,
                        "molecular_weight_Da": round(prediction.molecular_weight, 2),
                        "cLogP": round(prediction.log_p, 3),
                        "rotatable_bonds": prediction.rotatable_bonds,
                        "aromatic_proportion": round(prediction.aromatic_proportion, 3),
                        "error": "",
                    })
                except ValueError as exc:
                    rows.append({**source.to_dict(), "error": str(exc)})

            results = pd.DataFrame(rows)
            valid_count = int(results["error"].fillna("").eq("").sum())
            st.success(f"Processed {len(results)} rows; {valid_count} valid prediction(s).")
            st.dataframe(results, use_container_width=True, hide_index=True)
            output = io.StringIO()
            results.to_csv(output, index=False)
            st.download_button(
                "Download predictions",
                data=output.getvalue(),
                file_name="solubility_predictions.csv",
                mime="text/csv",
                type="primary",
            )
        except (ValueError, pd.errors.ParserError) as exc:
            st.error(str(exc))

else:
    st.subheader("About the model")
    st.markdown(
        """
        AquaSol implements the four-descriptor **ESOL** equation published by John S. Delaney (2004):

        `logS = 0.16 − 0.63(cLogP) − 0.0062(MW) + 0.066(RB) − 0.74(AP)`

        - **logS** is the base-10 logarithm of solubility in moles per litre.
        - **MW** is molecular weight, **RB** is rotatable-bond count, and **AP** is the fraction of heavy atoms that are aromatic.
        - RDKit calculates the structure and descriptors from the supplied SMILES.

        The original paper reported a standard error near 0.97 log units. Predictions can differ from measured
        values because of pH, ionisation, salt form, temperature, polymorphism, and descriptor implementation.

        **Reference:** Delaney, J. S. *J. Chem. Inf. Comput. Sci.* **2004**, 44, 1000–1005.
        [DOI: 10.1021/ci034243x](https://doi.org/10.1021/ci034243x)
        """
    )

st.caption("Built with Streamlit · Molecular descriptors powered by RDKit")
