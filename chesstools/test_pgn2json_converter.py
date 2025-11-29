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

def test_fen_inclusion():
    """Test that FEN positions are correctly included when requested."""
    import json
    import chess

    pgn_content = """[Event "FEN Test"]
[Site "Test"]
[Date "2025.11.29"]
[White "Test"]
[Black "Test"]
[Result "*"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6 8. c3 O-O 9. h3 Nb8 10. d4 Nbd7 11. c4 c6 12. cxb5 axb5 13. Nc3 Bb7 14. Bg5 b4 15. Nb1 h6 16. Bh4 c5 17. dxe5 dxe5 18. Qxd8 Raxd8 19. Nxe5 Nxe5 20. Bxe7 Nfg4 21. Bxd8 Rxd8 22. hxg4 Nxg4 23. f3 Ne5 24. Rad1 Bc6 25. Rd6 Bxe4 26. fxe4 Ng4 27. Rd2 Ne3 28. Re2 Nxg2 29. Kxg2 Rd3 30. Rc1 Rg3+ 31. Kh2 Rf3 32. Rc8+ Kh7 33. Rc7 Rf2+ 34. Rxf2 1/2-1/2"""

    with tempfile.TemporaryDirectory() as tmpdir:
        pgn_file = os.path.join(tmpdir, "fen_test.pgn")
        json_file = os.path.join(tmpdir, "fen_test.json")

        # Write test PGN
        with open(pgn_file, "w", encoding="utf-8") as f:
            f.write(pgn_content)

        # Convert PGN to JSON with FEN
        convert_pgn_to_json(pgn_file, json_file, include_fen=True)

        # Load and verify JSON contains FEN
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 1  # One game
        game = data[0]
        moves = game["moves"]

        # Verify FEN fields exist and are valid
        board = chess.Board()
        for move_obj in moves:
            assert "fen" in move_obj, f"Move {move_obj['san']} missing FEN field"

            # Verify FEN is valid
            try:
                fen_board = chess.Board(move_obj["fen"])
                assert fen_board.is_valid(), f"Invalid FEN: {move_obj['fen']}"
            except ValueError as e:
                pytest.fail(f"Invalid FEN format for move {move_obj['san']}: {e}")

            # Verify FEN matches expected position after move
            move = chess.Move.from_uci(board.parse_san(move_obj["san"]).uci())
            board.push(move)

            # Compare board positions (allowing for different move counters)
            expected_fen_parts = board.fen().split()
            actual_fen_parts = move_obj["fen"].split()

            # Compare the first 4 parts (board, turn, castling, en passant)
            assert expected_fen_parts[:4] == actual_fen_parts[:4], \
                f"FEN mismatch for move {move_obj['san']}: expected {board.fen()}, got {move_obj['fen']}"

        # Test that JSON without FEN option doesn't include FEN
        json_file_no_fen = os.path.join(tmpdir, "fen_test_no_fen.json")
        convert_pgn_to_json(pgn_file, json_file_no_fen, include_fen=False)

        with open(json_file_no_fen, "r", encoding="utf-8") as f:
            data_no_fen = json.load(f)

        moves_no_fen = data_no_fen[0]["moves"]
        for move_obj in moves_no_fen:
            assert "fen" not in move_obj, f"Unexpected FEN field in move {move_obj['san']} when include_fen=False"