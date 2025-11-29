# Chess Improvement Tools

A comprehensive toolkit for chess analysis and improvement, featuring advanced JSON-based game storage with full position tracking.

## 🛠️ Tools Overview

### Core Components

- **`chesstools/pgn2json_converter.py`** - Bidirectional PGN ↔ JSON conversion
- **`chesstools/chess-game.schema.json`** - JSON Schema for validation
- **`chesstools/test_pgn2json_converter.py`** - Comprehensive test suite
- **`chesstools/pgn2json_converter.md`** - Complete documentation

### Key Features

✅ **Unlimited Variation Nesting** - Handle complex analysis trees with infinite depth
✅ **FEN Position Tracking** - Optional board state storage for instant navigation
✅ **Engine Evaluation Storage** - Preserve Stockfish/ Lc0 analysis data
✅ **Schema Validation** - Ensure data integrity with JSON Schema
✅ **Round-trip Fidelity** - Perfect PGN ↔ JSON conversion
✅ **Git-friendly** - Track annotation changes with diff visibility

## 🚀 Quick Start

### Convert PGN to JSON with FEN positions
```bash
python chesstools/pgn2json_converter.py --include-fen
```

### Convert single file
```python
from chesstools.pgn2json_converter import convert_pgn_to_json
convert_pgn_to_json("game.pgn", "game.json", include_fen=True)
```

### Run tests
```bash
python -m pytest chesstools/test_pgn2json_converter.py -v
```

## 📊 JSON Schema Features

### Move Object Structure
```json
{
  "san": "e4",
  "move_number": 1,
  "color": "w",
  "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
  "annotations": {
    "comment": "Opening move",
    "eval": "+0.25"
  },
  "variations": [...]
}
```

### Benefits Over PGN
- **Structured data** - Easy parsing and manipulation
- **Infinite nesting** - No depth limits on variations
- **Position tracking** - Instant board setup at any move
- **Validation** - Schema ensures data consistency
- **Extensible** - Add custom fields as needed

## 🧪 Testing

All functionality is thoroughly tested:
- ✅ Round-trip conversion accuracy
- ✅ FEN position validation
- ✅ Schema compliance
- ✅ Variation tree integrity

## 📚 Documentation

- **[Complete API Reference](chesstools/pgn2json_converter.md)** - Detailed function documentation
- **[JSON Schema](chesstools/chess-game.schema.json)** - Validation specification
- **[GitHub Actions Setup](chesstools/github-validation.md)** - CI/CD integration

## 🎯 Use Cases

- **Opening Analysis** - Store complex variation trees with engine analysis
- **Game Archives** - Maintain annotated game collections with full fidelity
- **Training Data** - Build datasets for chess improvement applications
- **Viewer Development** - Foundation for custom chess analysis tools

## 🔄 Workflow Integration

1. **Convert** PGN games to JSON format
2. **Analyze** with engines, adding evaluations and comments
3. **Validate** against schema to ensure integrity
4. **Store** in Git for version-controlled annotation history
5. **Build** custom viewers or analysis tools on the JSON foundation

---

*Built for serious chess improvement with modern data practices.*</content>
<parameter name="filePath">e:\Lab\Research\Chess\ChessImprovement\README.md