import pytest
import tempfile
import os
from chesstools.pgn2json_converter import convert_pgn_to_json, convert_json_to_pgn
import chess.pgn

def test_round_trip_conversion():
    """Test that PGN -> JSON -> PGN produces equivalent games."""
    pgn_content = """[Event "Training"]
[Site "EC"]
[Date "2025.11.29"]
[Round "?"]
[White "Stockfish"]
[Black "SPN"]
[Result "1-0"]
[TimeControl "180+2"]

1. d4 {[%eval +0.25] } Nf6 2. c4 c5 3. d5 e6 4. Nc3 exd5 {[%eval +0.87] } 5. cxd5 {[%eval +0.79] } d6 {[%eval +0.91] At this point, it's already +1.0 according to StockFish and +0.9 according to Leela.} 6. e4 {[%eval +0.86] } g6 {[%eval +0.94] } 7. f4 {[%eval +0.91] } Bg7 8. Bb5+ {[%eval +0.88] } Nbd7  (8... Nfd7 {[%eval +0.92] }  9. a4 {[%eval +0.89] } Na6 10. Nf3 Nb4 {[%eval +0.93] }) 9. e5 dxe5 10. fxe5 Nxd5 11. Qxd5 O-O 12. Bxd7 Bxd7 13. Nf3 Bc6 14. Qxd8 Raxd8 15. Bg5 1-0"""

    with tempfile.TemporaryDirectory() as tmpdir:
        pgn_file = os.path.join(tmpdir, "test.pgn")
        json_file = os.path.join(tmpdir, "test.json")
        pgn_out_file = os.path.join(tmpdir, "test_converted.pgn")

        # Write original PGN
        with open(pgn_file, "w", encoding="utf-8") as f:
            f.write(pgn_content)

        # Convert PGN to JSON
        convert_pgn_to_json(pgn_file, json_file)

        # Convert JSON back to PGN
        convert_json_to_pgn(json_file, pgn_out_file)

        # Parse both games and compare their exports (to check equivalence)
        with open(pgn_file, "r", encoding="utf-8") as f:
            game_orig = chess.pgn.read_game(f)
        with open(pgn_out_file, "r", encoding="utf-8") as f:
            game_out = chess.pgn.read_game(f)

        # Use StringExporter to get the PGN strings
        from chess.pgn import StringExporter
        exporter_orig = StringExporter(headers=True, variations=True, comments=True)
        game_orig.accept(exporter_orig)
        orig_str = str(exporter_orig)

        exporter_out = StringExporter(headers=True, variations=True, comments=True)
        game_out.accept(exporter_out)
        out_str = str(exporter_out)

        # Assert that the exported PGN strings are identical (round-trip success)
        assert orig_str == out_str