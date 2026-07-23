import math

import pytest

from solubility_model import classify_log_s, predict_solubility


def test_ethanol_prediction_is_finite_and_canonical():
    result = predict_solubility("CCO")
    assert result.canonical_smiles == "CCO"
    assert math.isfinite(result.log_s)
    assert result.molarity == pytest.approx(10**result.log_s)
    assert result.molecular_weight == pytest.approx(46.069, abs=0.01)
    assert result.aromatic_proportion == 0


def test_benzene_has_fully_aromatic_heavy_atoms():
    result = predict_solubility("c1ccccc1")
    assert result.aromatic_proportion == pytest.approx(1.0)
    assert result.rotatable_bonds == 0


@pytest.mark.parametrize("value", ["", "   ", "not-a-smiles"])
def test_invalid_smiles_raises_helpful_error(value):
    with pytest.raises(ValueError):
        predict_solubility(value)


@pytest.mark.parametrize(
    ("log_s", "expected"),
    [(-0.5, "Highly soluble"), (-1.5, "Soluble"), (-2.5, "Moderately soluble"),
     (-3.5, "Poorly soluble"), (-4.5, "Very poorly soluble")],
)
def test_classification_bands(log_s, expected):
    assert classify_log_s(log_s).label == expected
