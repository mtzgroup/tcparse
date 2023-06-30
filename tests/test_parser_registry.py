import pytest

from qcparse.exceptions import RegistryError
from qcparse.registry import ParserSpec, registry


def test_get_parsers_program():
    parsers = registry.get_parsers("terachem")
    assert parsers
    for parser in parsers:
        assert isinstance(parser, ParserSpec)

    with pytest.raises(RegistryError):
        registry.get_parsers("not_a_program")


def test_get_parsers_program_filetype():
    parsers = registry.get_parsers("terachem", filetype="stdout")
    assert parsers
    for parser in parsers:
        assert isinstance(parser, ParserSpec)
        assert parser.filetype == "stdout"


def test_get_parsers_program_collect_inputs():
    parsers = registry.get_parsers("terachem", collect_inputs=False)
    assert parsers
    for parser in parsers:
        assert isinstance(parser, ParserSpec)
        assert not parser.input_data


def test_get_parsers_program_calctype():
    parsers = registry.get_parsers("terachem", calctype="gradient")
    assert parsers
    for parser in parsers:
        assert isinstance(parser, ParserSpec)
        assert "gradient" in parser.calctypes


def test_supported_programs():
    programs = registry.supported_programs()
    assert programs
    assert "terachem" in programs


def test_supported_filetypes():
    filetypes = registry.supported_filetypes("terachem")
    assert filetypes
    assert "stdout" in filetypes
