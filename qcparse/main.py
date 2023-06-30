"""Top level functions for the tcparse library"""

from importlib import import_module
from pathlib import Path
from typing import List, Optional, Union

from qcio import (
    SinglePointComputedProps,
    SinglePointFailure,
    SinglePointInput,
    SinglePointResult,
)

from .exceptions import MatchNotFoundError
from .models import single_point_data_collector
from .parsers import *  # noqa: F403 Ensure all parsers get registered
from .registry import ParserSpec, registry
from .utils import get_file_content

__all__ = ["parse", "parse_computed_props", "registry"]


def parse_computed_props(
    data_or_path: Union[str, bytes, Path],
    program: str,
    filetype: str = "stdout",
) -> SinglePointComputedProps:
    """Parse a file using the parsers registered for the given program.

    Args:
        data_or_path: File contents (str or bytes) or path to the file to parse.
        program: The QC program that generated the output file.
            To see the available programs run:
            >>> from qcparse import registry
            >>> registry.supported_programs()
        filetype: The type of file to parse (e.g. 'stdout' for the log output).
            To see the available filetypes for a given program run
            >>> from qcparse import registry
            >>> registry.supported_filetypes('program_name')

    Returns:
        A SinglePointComputedProps object containing the parsed data.

    Raises:
        MatchNotFoundError: If a required parser fails to parse its data.
    """
    file_content, _ = get_file_content(data_or_path)

    # Create a data collector object to store the parsed data
    data_collector = single_point_data_collector(collect_inputs=False)

    # Get the calculation type if filetype is 'stdout'
    if filetype == "stdout":
        parse_calctype = import_module(f"qcparse.parsers.{program}").parse_calctype
        calctype = parse_calctype(file_content)

    else:
        calctype = None

    # Get all the parsers for the program and filetype
    parsers: List[ParserSpec] = registry.get_parsers(
        program,
        filetype=filetype,
        collect_inputs=False,
        calctype=calctype,
    )

    # Apply parsers to the file content.
    for parser_info in parsers:
        try:
            # This will raise a MatchNotFound error if the parser can't find its data
            parser_info.parser(file_content, data_collector)
        except MatchNotFoundError:
            if parser_info.required:
                raise
            else:
                # Parser didn't find anything, but it wasn't required
                pass

    # Remove scratch data
    del data_collector.scratch

    return SinglePointComputedProps(**data_collector.computed.dict())


# TODO: Finish out this function for parsing full inputs, outputs, and failures
# for now going to skip failing tests and just focus on simpler parse_computed_props
# function.
def parse(
    data_or_path: Union[str, bytes, Path],
    program: str,
    filetype: str = "stdout",
    input_data: Optional[SinglePointInput] = None,
) -> Union[SinglePointResult, SinglePointFailure]:
    """Parse a file using the parsers registered for the given program.

    Args:
        data_or_path: File contents (str or bytes) or path to the file to parse.
        program: The QC program that generated the output file.
            To see the available programs run:
            >>> from qcparse import registry
            >>> registry.supported_programs()
        filetype: The type of file to parse (e.g. 'stdout' for the log output).
            To see the available filetypes for a given program run
            >>> from qcparse import registry
            >>> registry.supported_filetypes('program_name')
        input_data: An optional SinglePointInput object containing the input data
            for the calculation. This will be added to the SinglePointOutput object
            returned by this function and no input data will be parsed from the file.


    Returns:
        SinglePointOutput or SinglePointFailure object encapsulating the parsed data.
    """
    raise NotImplementedError("This function needs work before it is ready to use.")
    # file_content, filepath = get_file_content(data_or_path)

    # # Create a data collector object to store the parsed data
    # # Don't collect inputs if input_data is passed
    # collect_inputs = input_data is None
    # # TODO: Handle failed calculations
    # data_collector = single_point_data_collector(collect_inputs)

    # # Get the calculation type if filetype is 'stdout'
    # if filetype == "stdout":
    #     parse_calctype = import_module(f"qcparse.parsers.{program}").parse_calctype
    #     calctype = parse_calctype(file_content)
    #     data_collector.input_data.calctype = calctype

    #     # Determine if calculation succeeded
    #     parse_calculation_succeeded = import_module(
    #         f"qcparse.parsers.{program}"
    #     ).calculation_succeeded
    #     if not parse_calculation_succeeded(file_content):
    #         # TODO: Handle failed calculations
    #         pass

    #     data_collector.stdout = file_content
    # else:
    #     calctype = None

    # # Get all the parsers for the program and filetype
    # parsers: List[ParserSpec] = registry.get_parsers(
    #     program,
    #     filetype=filetype,
    #     collect_inputs=collect_inputs,
    #     calctype=calctype,
    # )

    # # Apply parsers to the file content.
    # for parser_info in parsers:
    #     try:
    #         # This will raise a MatchNotFound error if the parser can't find its data
    #         parser_info.parser(file_content, data_collector)
    #     except MatchNotFoundError:
    #         if parser_info.required:
    #             raise
    #         else:
    #             # Parser didn't find anything, but it wasn't required
    #             pass

    # data_collector.provenance.program = program

    # if input_data:
    #     # Add the input data to the results object
    #     data_collector.input_data = input_data

    # # Call any post-processing function for the program
    # post_process = getattr(
    #     import_module(f"qcparse.parsers.{program}"), "post_process", None
    # )
    # if post_process:
    #     post_process(data_collector, file_content, filetype, filepath, input_data)

    # # Remove scratch data
    # del data_collector.scratch

    # return SinglePointResult(**data_collector.dict())


if __name__ == "__main__":
    # output = parse("./tests/data/water.gradient.out", "terachem", "stdout")
    props, prov = parse_computed_props(
        "./tests/data/water.gradient.out", "terachem", "stdout"
    )
    print(props)
