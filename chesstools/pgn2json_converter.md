
# 📐 JSON Schema for Chess Game Archives

## 1. Motivation

PGN is the de facto exchange format for chess games, but it has critical limitations:

- **Parser divergence**: Different GUIs interpret comments and nesting differently.  
- **Nesting limits**: Deep variation trees often break parsers.  
- **Flat metadata**: PGN tags are simple key–value pairs, unsuitable for structured annotations.  
- **Auditability issues**: PGN is text, but lacks a formal schema for validation.

For an **audit‑grade study workflow**, JSON offers:

- **Unlimited nesting**: Recursive structures handle deep repertoires.  
- **Structured annotations**: Comments, engine evals, and tags stored consistently.  
- **Schema validation**: Enforce integrity with JSON Schema + CI pipelines.  
- **Diff‑friendly**: Git shows exactly what changed in annotations or variations.  

PGN remains useful for **interoperability** (import/export into GUIs), but JSON should be the **canonical archive**.

---

## 2. Design Principles

- **Recursive move tree**: Each move can contain nested variations.  
- **Annotations object**: Flexible container for comments, evals, tags.  
- **Metadata block**: Mirrors PGN tags but extensible.  
- **Validation**: Schema ensures consistency across commits.  
- **Auditability**: Every change is visible in Git diffs.  

---

## 3. JSON Schema Definition

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Chess Game Schema",
  "description": "Schema for storing chess games with nested variations and annotations",
  "type": "object",
  "properties": {
    "game_id": {
      "type": "string",
      "description": "Unique identifier for the game (filename, UUID, etc.)"
    },
    "metadata": {
      "type": "object",
      "description": "Game metadata similar to PGN tags",
      "properties": {
        "event": { "type": "string" },
        "site": { "type": "string" },
        "date": { "type": "string", "format": "date" },
        "round": { "type": "string" },
        "white": { "type": "string" },
        "black": { "type": "string" },
        "result": { "type": "string", "enum": ["1-0", "0-1", "1/2-1/2", "*"] },
        "time_control": { "type": "string" }
      },
      "required": ["event", "date", "white", "black", "result"]
    },
    "moves": {
      "type": "array",
      "description": "Mainline moves with nested variations",
      "items": { "$ref": "#/$defs/move" }
    },
    "notes": {
      "type": "string",
      "description": "General notes about the game"
    }
  },
  "required": ["game_id", "metadata", "moves"],
  "$defs": {
    "move": {
      "type": "object",
      "properties": {
        "san": {
          "type": "string",
          "description": "Move in Standard Algebraic Notation"
        },
        "move_number": {
          "type": "integer",
          "description": "Move number in the game"
        },
        "color": {
          "type": "string",
          "description": "Color of the player making the move",
          "enum": ["w", "b"]
        },
        "fen": {
          "type": "string",
          "description": "FEN representation of the board position after this move (optional)"
        },
        "annotations": {
          "type": "object",
          "description": "Annotations for the move",
          "properties": {
            "comment": { "type": "string" },
            "eval": { "type": "string" },
            "tags": {
              "type": "array",
              "items": { "type": "string" }
            }
          }
        },
        "variations": {
          "type": "array",
          "description": "Alternative lines branching from this move",
          "items": {
            "type": "object",
            "properties": {
              "label": { "type": "string" },
              "line": {
                "type": "array",
                "items": { "$ref": "#/$defs/move" }
              }
            },
            "required": ["line"]
          }
        }
      },
      "required": ["san", "move_number"]
    }
  }
}
```

---

## 4. Example Instance

```json
{
  "game_id": "benoni_training_2025_11_28",
  "metadata": {
    "event": "Training vs Engine",
    "site": "En Croissant",
    "date": "2025-11-28",
    "round": "1",
    "white": "SP",
    "black": "Engine",
    "result": "1-0",
    "time_control": "15+0"
  },
  "moves": [
    {
      "san": "d4",
      "move_number": 1,
      "color": "w",
      "fen": "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 1",
      "annotations": {
        "comment": "Main line",
        "eval": "+0.20",
        "tags": ["opening", "Benoni"]
      },
      "variations": [
        {
          "label": "Alternative line",
          "line": [
            {
              "san": "Nf6",
              "move_number": 1,
              "color": "b",
              "annotations": {
                "comment": "Standard reply",
                "eval": "+0.15"
              },
              "variations": []
            }
          ]
        }
      ]
    },
    {
      "san": "c4",
      "move_number": 2,
      "color": "w",
      "annotations": {},
      "variations": []
    }
  ],
  "notes": "Modern Benoni training game"
}
```

---

## 5. Workflow Integration

- **Canonical archive**: Store JSON files in Git.  
- **Validation**: Run `ajv` or similar validator in GitHub Actions to enforce schema.  
- **Interoperability**: Convert JSON ↔ PGN for GUI use.  
- **Analytics**: Build SQLite from JSON for fast queries.  

---

✅ With this schema, you can **preserve annotations**, **handle unlimited nesting**, and **validate every commit**. PGN remains your interchange format, but JSON becomes your **source of truth**.

---

## 6. Converter Tool

The `pgn2json_converter.py` script provides bidirectional conversion between PGN and JSON formats, implementing the schema above.

### 6.1 Core Functions

#### `serialize_game(game, include_fen=False)`
Converts a chess.pgn.Game object to the JSON schema format.
- **Input**: `chess.pgn.Game` object, optional `include_fen` boolean
- **Output**: Dictionary with `game_id`, `metadata`, `moves`, and `notes`
- **Process**:
  - Extracts PGN headers into `metadata`, mapping "TimeControl" to "time_control"
  - Generates `game_id` from event and date
  - Calls `serialize_moves()` to build the move tree
  - If `include_fen=True`, adds FEN strings to each move

#### `serialize_moves(node, include_fen=False)`
Recursively serializes the move tree from a PGN game node.
- **Input**: `chess.pgn.GameNode` object, optional `include_fen` boolean
- **Output**: List of move dictionaries
- **Features**:
  - Handles mainline moves and variations
  - Extracts comments and parses engine evaluations (`[%eval ...]`)
  - Assigns move numbers and colors ("w" or "b")
  - Recursively processes nested variations
  - If `include_fen=True`, generates FEN after each move

#### `convert_pgn_to_json(input_file, output_file, include_fen=False)`
Converts a PGN file to JSON format.
- **Input**: Path to PGN file, optional `include_fen` boolean
- **Output**: Path to JSON file
- **Process**:
  - Parses all games in the PGN file using `chess.pgn.read_game()`
  - Serializes each game using `serialize_game()` with FEN option
  - Writes formatted JSON with 2-space indentation

#### `build_pgn_moves(moves_list)`
Reconstructs PGN move text from the JSON move structure.
- **Input**: List of move dictionaries from JSON
- **Output**: String of PGN-formatted moves
- **Features**:
  - Adds move numbers only for white moves (standard PGN format)
  - Includes comments in curly braces `{}`
  - Handles nested variations in parentheses `()`

#### `convert_json_to_pgn(input_file, output_file)`
Converts a JSON file back to PGN format.
- **Input**: Path to JSON file
- **Output**: Path to PGN file
- **Process**:
  - Reads and parses JSON data
  - Reconstructs PGN headers with proper capitalization
  - Uses `build_pgn_moves()` to generate move text
  - Handles multiple games in a single file

#### `convert(file_path)`
Convenience function for single-file conversion.
- **Input**: File path (`.pgn` or `.json`)
- **Output**: Automatically determines output path and calls appropriate converter
- **Usage**: `convert("game.pgn")` → creates `game.json`

### 6.2 Batch Processing

#### `main(base_dir, mode, include_fen)`
Processes all files in a directory tree.
- **Modes**:
  - `"pgn2json"`: Converts all `.pgn` files to `.json` (default)
  - `"json2pgn"`: Converts all `.json` files to `_converted.pgn`
- **Features**:
  - Recursively walks directory structure
  - Skips already processed files (containing "_formatted" or "_converted")
  - Outputs progress messages
  - If `include_fen=True`, adds FEN positions to JSON output

### 6.3 Usage Examples

#### Convert single PGN file to JSON:
```python
from pgn2json_converter import convert
convert("path/to/game.pgn")  # Creates game.json
```

#### Convert single JSON file to PGN:
```python
convert("path/to/game.json")  # Creates game_converted.pgn
```

#### Convert PGN to JSON with FEN positions:
```python
from pgn2json_converter import convert_pgn_to_json
convert_pgn_to_json("game.pgn", "game.json", include_fen=True)
```

#### Batch convert all PGN files in directory:
```bash
python pgn2json_converter.py  # Runs in pgn2json mode by default
```

#### Batch convert with FEN positions included:
```bash
python pgn2json_converter.py --include-fen
```

#### Batch convert all JSON files to PGN:
```bash
python pgn2json_converter.py json2pgn
```

### 6.4 Dependencies

- `chess` library for PGN parsing and manipulation
- Standard library: `os`, `json`

### 6.5 File Structure

```
chesstools/
├── pgn2json_converter.py    # Main converter script
├── json2pgn_converter.py    # Batch JSON→PGN converter
├── test_pgn2json_converter.py  # Unit tests
└── pgn2json_converter.md    # This documentation
```

### 6.6 Round-trip Fidelity

The converter maintains high fidelity for:
- ✅ Move sequences and variations
- ✅ Comments and annotations
- ✅ Game metadata and headers
- ✅ Engine evaluations
- ⚠️ Some advanced PGN features may need extension

### 6.7 Testing

The tool includes comprehensive tests to ensure conversion accuracy.

#### Running Tests

```bash
# Install pytest in your Python environment
pip install pytest

# If using conda, activate your environment first
conda activate your_env_name
pip install pytest

# Run all tests
pytest chesstools/test_pgn2json_converter.py

# Run with verbose output
pytest chesstools/test_pgn2json_converter.py -v

# Run from the project root directory (parent of chesstools/)
pytest chesstools/test_pgn2json_converter.py

# Run with verbose output
pytest chesstools/test_pgn_json_converter.py -v

# Alternative: use python -m pytest
python -m pytest test_pgn2json_converter.py
```

#### Test Coverage

The test suite (`test_pgn2json_converter.py`) verifies:
- **Round-trip conversion**: PGN → JSON → PGN produces equivalent games
- **Move accuracy**: All moves, variations, and annotations preserved
- **Header integrity**: Metadata correctly mapped and restored
- **Parser compatibility**: Output compatible with `chess.pgn` library
- **FEN inclusion**: Optional FEN position tracking works correctly
- **FEN validation**: Generated FEN strings are valid chess positions

#### Test Functions

`test_round_trip_conversion()`:
- Creates a sample PGN string with comments, variations, and evaluations
- Converts PGN to JSON, then JSON back to PGN
- Parses both versions and compares using `chess.pgn.StringExporter`
- Ensures structural equivalence and annotation preservation

`test_fen_inclusion()`:
- Tests FEN field generation when `include_fen=True`
- Validates FEN strings represent correct board positions
- Verifies FEN fields are absent when `include_fen=False`
- Ensures FEN positions match actual game state after each move

Run tests after any code changes to maintain conversion fidelity.
