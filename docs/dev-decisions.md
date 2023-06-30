# Design Decisions

## Other parse packages to look at

- [iodata](https://github.com/theochem/iodata) and [cclib](https://cclib.github.io/contents.html) are recommended by [this](https://mattermodeling.stackexchange.com/questions/6532/whats-the-best-quantum-chemistry-output-parser-for-the-command-line) StackOverflow post. `iodata` was [published](https://onlinelibrary.wiley.com/doi/abs/10.1002/jcc.26468?casa_token=iQFOBtKf0qAAAAAA:pAv_vxn6Nfis_DhQENlqGpeIZoawNhJYCg17fdobB3ftuyEbHSOAyHbsjKTeU_AdVS48EiqqQDzUHKNf) in 2020 so I'd consider it the more modern alternative. It's still a mess to use.

## UPDATE DESIGN DECISION:

- I don't see a strong reason for making this package a standalone package that parses everything required for a `SinglePointSuccessfulResult` object including input data, provenance data, xyz files, etc... While the original idea was to have a cli tool to run on TeraChem files, now that I've build my own data structures and driver program, there's no reason to parse anything but `SinglePointComputedProps` values because we should just be driving the programs with `qcop/qcpilot`. So why waste time parsing a bunch of extra data? I've left the original `parse` function and some basic `cli` functionality in case I change my mind, but perhaps I just strip this down to the bare bones and K.I.S.S? The only downside would be walking in to someone else's old data and wanting to slurp it all in, but perhaps there's no reason to build for that use case now... Just go with SIMPLE and keep the code maintainable. All the logic for parsing inputs and handling failed computations was making the package quite complex (cases where .xyz file not available, or determining if output was a success/failure), this should be the SIMPLEST package of the `qc` suite, yet it was become the most complex and difficult to reason about.

## Basic Architectural Overview and Program Flow

1. Top level `parse` function is called passing a `filepath`, the `program` that generated the output, and the `filetype` (e.g., `stdout` or `wavefunction` or whatever filetypes a particular program emits for which parsers have been written).
2. `parse` instantiates an `ParsedDataCollector` object that acts as a proxy for the `SinglePointResult` object but offers two advantages:
   - The `SinglePointResult` object has multiple required data fields, but parsers only return a single data value per parser. The `ParsedDataCollector` object gets passed to parsers and they can add their parsed value to the objects just as if it were a mutable `SinglePointResult` object. This makes it easy for each parser to both specify exactly what data they parse and where that data will live on the final structured object.
   - The `ParsedDataCollector` object only allows setting a particular data attribute once. If a second attempt is made it raises an `AttributeError`. This provides a sanity check that multiple parsers aren't trying to write to the same field and overwriting each other.
3. `parse` looks up the parsers for the `program` in the `parser_registry`. Parsers are registered by wrapping them with the `@parser` decorator found in `qcparse.parsers.decorators`. The `@parser` decorator registers a parser with the registry under the program name of the module in which it is found, verifying that the `filetype` for which it is registered is supported by the `program` by checking `SupportedFileTypes` in the parser's module. It also registers whether a parser `must_succeed` which means an exception will be raised if this value is not found when attempting to parse a file. In order for parsers to properly register they must be imported, so make sure they are hoisted into the `qcparse.parsers.__init__` file.
4. `parse` executes all parsers for the given `filetype` and converts the `ParsedDataCollector` object passed to all the parsers into a final `SinglePointOutput` object, optionally containing the `input_data` too if this argument was passed to `parse`. In order to parse input values more parsers must be written to fully specify a `SinglePointInput` object including a `Molecule`, `Model` (method and basis strings), and a `driver` (`energy`, `gradient`, `hessian`).

## How to create new parsers

1. Create a file in the `parsers` named after the quantum chemistry program, e.g., `qchem.py`.
2. Create `class FileType(str, Enum)` in the file registering the file types the parsers support.
3. If `stdout` is a file type then create a `def get_calctype(string: str) -> CalcType` function that returns the `CalcType` for the file. One of `CalcType.energy`, `CalcType.gradient`, or `CalcType.hessian`.
4. Create simple parser functions that accept file data and an output object. The parser should parse a single piece of data from the file and set it on the output object at its corresponding location found on the `qcio.SinglePointOutput` object. Register this parser by decorating it with the `@parser` decorator. The decorator must declare `filetype` and can optionally declare `required` (`True` by default), `input_data` (`False` by default), and `only` (`None` by default). See the `qcparse.decorators` for details on what these mean.

```py
@parser(filetype=FileTypes.stdout)
def parse_some_data(string: str, output: ParsedDataCollector):
   """Parse some data from a file."""
    regex = r"Some Data: (-?\d+(?:\.\d+)?)"
    output.computed.some_data = float(regex_search(regex, string).group(1))

```

5. That's it! The developer just has to focus on writing sin

## Publishing Checklist

- Update `CHANGELOG.md`
- Bump version in `pyproject.toml`
- Tag commit with a version and GitHub Actions will publish it to pypi if tag is on `master` branch.
- `git push --tags`
- `git push`
