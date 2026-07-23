"""Core, UI-independent implementation of Delaney's ESOL equation."""

from __future__ import annotations

from dataclasses import dataclass

from rdkit import Chem
from rdkit.Chem import Crippen, Descriptors, Lipinski


@dataclass(frozen=True)
class SolubilityClass:
    label: str
    description: str
    emoji: str
    score: float


@dataclass(frozen=True)
class SolubilityPrediction:
    molecule: Chem.Mol
    canonical_smiles: str
    log_s: float
    molarity: float
    molecular_weight: float
    log_p: float
    rotatable_bonds: int
    aromatic_proportion: float
    classification: SolubilityClass

    @property
    def formatted_molarity(self) -> str:
        if self.molarity >= 0.01:
            return f"{self.molarity:.3g} M"
        if self.molarity >= 1e-6:
            return f"{self.molarity * 1e6:.3g} µM"
        return f"{self.molarity:.2e} M"


def classify_log_s(log_s: float) -> SolubilityClass:
    """Map logS to transparent screening bands."""
    if log_s >= -1:
        return SolubilityClass("Highly soluble", "At least about 0.1 M", "●", 1.0)
    if log_s >= -2:
        return SolubilityClass("Soluble", "About 0.01–0.1 M", "●", 0.8)
    if log_s >= -3:
        return SolubilityClass("Moderately soluble", "About 1–10 mM", "●", 0.6)
    if log_s >= -4:
        return SolubilityClass("Poorly soluble", "About 0.1–1 mM", "●", 0.35)
    return SolubilityClass("Very poorly soluble", "Below about 0.1 mM", "●", 0.12)


def predict_solubility(smiles: str) -> SolubilityPrediction:
    """Predict aqueous logS from a SMILES string using the published ESOL equation."""
    cleaned = (smiles or "").strip()
    if not cleaned:
        raise ValueError("Enter a SMILES string before requesting a prediction.")
    if len(cleaned) > 2000:
        raise ValueError("The SMILES string is too long (maximum 2,000 characters).")

    molecule = Chem.MolFromSmiles(cleaned)
    if molecule is None or molecule.GetNumHeavyAtoms() == 0:
        raise ValueError("That is not a valid molecular SMILES string. Check the notation and try again.")

    molecular_weight = float(Descriptors.MolWt(molecule))
    log_p = float(Crippen.MolLogP(molecule))
    rotatable_bonds = int(Lipinski.NumRotatableBonds(molecule))
    aromatic_atoms = sum(1 for atom in molecule.GetAtoms() if atom.GetIsAromatic())
    aromatic_proportion = aromatic_atoms / molecule.GetNumHeavyAtoms()

    # Delaney, J. Chem. Inf. Comput. Sci. 2004, 44, 1000–1005.
    log_s = (
        0.16
        - 0.63 * log_p
        - 0.0062 * molecular_weight
        + 0.066 * rotatable_bonds
        - 0.74 * aromatic_proportion
    )
    molarity = 10**log_s

    return SolubilityPrediction(
        molecule=molecule,
        canonical_smiles=Chem.MolToSmiles(molecule, canonical=True),
        log_s=log_s,
        molarity=molarity,
        molecular_weight=molecular_weight,
        log_p=log_p,
        rotatable_bonds=rotatable_bonds,
        aromatic_proportion=aromatic_proportion,
        classification=classify_log_s(log_s),
    )
