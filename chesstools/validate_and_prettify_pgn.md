# PGN Validation and Prettification Script

## Overview

`validate_and_prettify_pgn.py` is a Python script that processes PGN (Portable Game Notation) files to validate chess games, reformat them for better readability, and handle variations and annotations. It's designed for chess improvement workflows, ensuring PGN files are clean and consistent.

## Features

- **Validation**: Parses PGN files and checks for valid games using the `python-chess` library.
- **Prettification**: Reformats moves to one pair per line (e.g., `1. e4 e5`), preserving variations and comments.
- **Variation Handling**: Indents nested variations recursively for clarity.
- **Comment Processing**: Attaches comments to moves, moves standalone comments to previous lines, and parses evaluations.
- **Batch Processing**: Walks directories to process all `.pgn` files, outputting `_formatted.pgn` files.
- **Error Handling**: Reports invalid games and skips formatted files to avoid overwriting.

## Requirements

- Python 3.6+
- `python-chess` library: Install with `pip install python-chess`

## Usage

### Command Line

Run the script directly:

```bash
python chesstools/validate_and_prettify_pgn.py
```

This processes PGN files in the repository root and subdirectories, generating formatted versions.

### As a Module

Import and use functions:

```python
from chesstools.validate_and_prettify_pgn import validate_and_reformat_pgn, main

# Process a single file
validate_and_reformat_pgn("input.pgn", "output.pgn")

# Process a directory
main("/path/to/pgn/directory")
```

## Output Format

- **Moves**: One pair per line, e.g., `1. d4 Nf6`
- **Variations**: Indented with `(` and `)`, nested levels add more spaces.
- **Comments**: Attached to moves as `{comment}`, evaluations parsed separately.
- **Headers**: Preserved at the top.

Example:

```
[Event "Training"]
[White "Player"]

1. d4{ [%eval +0.25] } Nf6
2. c4 c5
(
  Nf6{alternative}
  9. a4 Na6
)
9. e5 dxe5
...
```

## Configuration

- **Base Directory**: Defaults to the repository root (`..` from script location).
- **File Filtering**: Processes `.pgn` files, skips `_formatted.pgn` to avoid recursion.

## Limitations

- Assumes standard PGN format; complex or malformed files may not parse correctly.
- Variations are indented, but very deep nesting may affect readability.
- Comments are preserved but not deeply analyzed beyond evals.

## Related Tools

- `pgn_json_converter.py`: Converts PGN to JSON for structured storage.
- `chess-with-json.md`: Schema for JSON chess game archives.

## Testing

The tools include automated tests to ensure reliability:

### PGN Prettifier Testing
- Manual testing: Run on sample PGN files and verify output formatting.
- Validation: Ensure parsed games match original structure.

### PGN-JSON Converter Testing
- **Round-trip Test**: Converts PGN → JSON → PGN and verifies identical output using `pytest`.
- **Command**: `cd chesstools && python -m pytest test_pgn_json_converter.py -v`
- **What it tests**: Parses a sample PGN, converts to JSON, converts back, and compares exported strings for equivalence.
- **Dependencies**: `pytest`, `python-chess`.
- **Coverage**: Validates moves, variations, comments, and metadata preservation.

Run tests regularly to catch regressions. For CI, integrate with GitHub Actions.

## Contributing

Modify the script in `chesstools/validate_and_prettify_pgn.py`. Test on sample PGN files and ensure `python-chess` compatibility.