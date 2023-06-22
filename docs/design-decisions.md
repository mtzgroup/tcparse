# Design Decisions

## Other parse packages to look at

- [iodata](https://github.com/theochem/iodata) and [cclib](https://cclib.github.io/contents.html) are recommended by [this](https://mattermodeling.stackexchange.com/questions/6532/whats-the-best-quantum-chemistry-output-parser-for-the-command-line) StackOverflow post. `iodata` was [published](https://onlinelibrary.wiley.com/doi/abs/10.1002/jcc.26468?casa_token=iQFOBtKf0qAAAAAA:pAv_vxn6Nfis_DhQENlqGpeIZoawNhJYCg17fdobB3ftuyEbHSOAyHbsjKTeU_AdVS48EiqqQDzUHKNf) in 2020 so I'd consider it the more modern alternative. It's still a mess to use.

## Basic Architectural Overview and Program Flow

1. Top level `parse` function is called passing a `filepath`, the `program` that generated the output, and the `filetype` (e.g., `stdout` or `wavefunction` or whatever filetypes a particular program emits for which parsers have been written).
2. `parse` instantiates an `ImmutableNamespace` object that acts as a proxy for the `SinglePointResult` object but offers two advantages:
   - The `SinglePointResult` object has multiple required data fields, but parsers only return a single data value per parser. The `ImmutableNamespace` object gets passed to parsers and they can add their parsed value to the objects just as if it were a mutable `SinglePointResult` object. This makes it easy for each parser to both specify exactly what data they parse and where that data will live on the final structured object.
   - The `ImmutableNamespace` object only allows setting a particular data attribute once. If a second attempt is made it raises an `AttributeError`. This provides a sanity check that multiple parsers aren't trying to write to the same field and overwriting each other.
3. `parse` looks up the parsers for the `program` in the `parser_registry`. Parsers are registered by wrapping them with the `@parser` decorator found in `qcparse.parsers.decorators`. The `@parser` decorator registers a parser with the registry under the program name of the module in which it is found, verifying that the `filetype` for which it is registered is supported by the `program` by checking `SupportedFileTypes` in the parser's module. It also registers whether a parser `must_succeed` which means an exception will be raised if this value is not found when attempting to parse a file. In order for parsers to properly register they must be imported, so make sure they are hoisted into the `qcparse.parsers.__init__` file.
4. `parse` executes all parsers for the given `filetype` and converts the `ImmutableNamespace` object passed to all the parsers into a final `SinglePointOutput` object, optionally containing the `input_data` too if this argument was passed to `parse`. In order to parse input values more parsers must be written to fully specify a `SinglePointInput` object including a `Molecule`, `Model` (method and basis strings), and a `driver` (`energy`, `gradient`, `hessian`).