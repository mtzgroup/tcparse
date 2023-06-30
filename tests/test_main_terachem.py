import pytest
from qcio import SinglePointCalcType as SPCalcType
from qcio import SinglePointFailure, SinglePointResult

from qcparse import parse


@pytest.mark.skip
@pytest.mark.parametrize(
    "filename,return_type,calctype",
    (
        ("water.energy.out", SinglePointResult, SPCalcType.energy.value),
        ("water.gradient.out", SinglePointResult, SPCalcType.gradient.value),
        (
            "water.frequencies.out",
            SinglePointResult,
            SPCalcType.hessian.value,
        ),
        (
            "caffeine.gradient.out",
            SinglePointResult,
            SPCalcType.gradient.value,
        ),
        (
            "caffeine.frequencies.out",
            SinglePointResult,
            SPCalcType.hessian.value,
        ),
        ("failure.basis.out", SinglePointFailure, SPCalcType.gradient.value),
        ("failure.nocuda.out", SinglePointFailure, SPCalcType.gradient.value),
    ),
)
def test_parse(test_data_dir, filename, return_type, calctype, data_collector):
    """Test that the parser returns the correct type of output object"""

    data_collector = parse(test_data_dir / filename, "terachem", "stdout")
    assert isinstance(data_collector, return_type)

    assert data_collector.input_data.calctype == calctype

    if isinstance(data_collector, SinglePointFailure):
        # Guarantee stdout included
        assert isinstance(data_collector.error.extras["stdout"], str)


@pytest.mark.skip
@pytest.mark.parametrize(
    "filename,driver",
    (
        ("water.gradient.out", "gradient"),
        ("water.frequencies.out", "hessian"),
        ("water.molecule_moved.out", "energy"),
    ),
)
def test_parse_ignore_xyz(test_data_dir, filename, driver):
    # This tests that qcel still does correct validation on the gradient and
    output = parse(test_data_dir / filename, ignore_xyz=True)
    assert isinstance(output, SinglePointResult)
    assert output.driver == driver
    # Using a hydrogen atoms as dummy
    assert output.molecule.symbols[0] == "H"


@pytest.mark.skip
def test_parse_moved_molecule(test_data_dir):
    with pytest.raises(FileNotFoundError):
        parse(test_data_dir / "water.molecule_moved.out", "terachem")
