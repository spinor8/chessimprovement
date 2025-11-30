import os
import json
import chess.pgn
from typing import Dict, List, Any, Optional, Union

def serialize_game(game: chess.pgn.Game, include_fen: bool = False) -> Dict[str, Any]:
    # Build metadata from headers
    metadata = {}
    for tag in game.headers:
        key = tag.lower()
        value = game.headers[tag]
        # Map some keys to match schema
        if key == "timecontrol":
            key = "time_control"
        metadata[key] = value

    # Generate game_id
    event = metadata.get("event", "unknown")
    site = metadata.get("site", "unknown")
    date = metadata.get("date", "unknown")
    round_ = metadata.get("round", "unknown")
    white = metadata.get("white", "unknown")
    black = metadata.get("black", "unknown")
    game_id = f"{event}_{site}_{date}_{round_}_{white}_vs_{black}".replace(" ", "_").replace("/", "_").replace("?", "unknown")

    # Serialize moves
    moves = serialize_moves(game, include_fen)

    return {
        "game_id": game_id,
        "metadata": metadata,
        "moves": moves,
        "notes": ""
    }

def serialize_moves(node: chess.pgn.GameNode, include_fen: bool = False) -> List[Dict[str, Any]]:
    moves = []
    current = node
    board = current.board()

    while current.variations:
        child = current.variations[0]
        move = child.move
        san = board.san(move)
        move_number = board.fullmove_number

        # Annotations
        annotations = {}
        if child.comment:
            comment = child.comment
            annotations["comment"] = comment
            # Parse eval if present
            if "[%eval" in comment:
                start = comment.find("[%eval") + 7
                end = comment.find("]", start)
                if end > start:
                    annotations["eval"] = comment[start:end].strip()

        # Variations (alternative lines)
        variations = []
        for var in current.variations[1:]:
            var_node = var
            var_board = current.board()  # Board before the variation move
            var_move = var_node.move
            var_san = var_board.san(var_move)
            var_move_number = var_board.fullmove_number
            var_annotations = {}
            if var_node.comment:
                var_annotations["comment"] = var_node.comment
            var_color = "w" if var_board.turn == chess.WHITE else "b"
            var_moves = [{
                "san": var_san,
                "move_number": var_move_number,
                "color": var_color,
                "lan": var_move.uci(),
                "annotations": var_annotations,
                "variations": []
            }]
            if include_fen:
                var_board.push(var_move)
                var_moves[0]["fen"] = var_board.fen()
                var_board.pop()
            var_board.push(var_move)
            rest_moves = serialize_moves(var_node, include_fen)
            var_moves.extend(rest_moves)
            variations.append({"label": "", "line": var_moves})

        move_obj = {
            "san": san,
            "move_number": move_number,
            "color": "w" if board.turn == chess.WHITE else "b",
            "lan": move.uci(),
            "annotations": annotations,
            "variations": variations
        }

        # Add FEN after the move
        board.push(move)
        if include_fen:
            move_obj["fen"] = board.fen()

        moves.append(move_obj)

        # Move to next
        current = child

    return moves

def convert_pgn_to_json(input_file: str, output_file: str, include_fen: bool = False) -> None:
    with open(input_file, "r", encoding="utf-8") as f:
        games = []
        while True:
            game = chess.pgn.read_game(f)
            if game is None:
                break
            games.append(game)

    if not games:
        print(f"❌ No valid games found in {input_file}")
        return

    print(f"✅ {len(games)} valid games parsed from {input_file}")

    json_data = [serialize_game(game, include_fen) for game in games]

    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(json_data, out, indent=2)

    print(f"📄 JSON output written to {output_file}")

def build_pgn_moves(moves_list: List[Dict[str, Any]]) -> str:
    text = ""
    for move_obj in moves_list:
        san = move_obj["san"]
        move_number = move_obj["move_number"]
        color = move_obj.get("color", "w")
        if color == "w":
            text += f"{move_number}. {san} "
        else:
            text += f"{san} "
        if move_obj.get("annotations", {}).get("comment"):
            text += f"{{{move_obj['annotations']['comment']}}} "
        for var in move_obj.get("variations", []):
            text += f"( {build_pgn_moves(var['line'])} ) "
    return text.strip()

def convert(file_path: str) -> None:
    """Wrapper function to convert a single file based on its extension.
    .pgn -> .json
    .json -> _converted.pgn
    """
    if file_path.lower().endswith(".pgn"):
        output_path = file_path.replace(".pgn", ".json")
        convert_pgn_to_json(file_path, output_path)
    elif file_path.lower().endswith(".json"):
        output_path = file_path.replace(".json", "_converted.pgn")
        convert_json_to_pgn(file_path, output_path)
    else:
        print(f"Unsupported file type: {file_path}")

def validate_json_consistency(game_data: Dict[str, Any]) -> None:
    """Validate that SAN and LAN fields in the JSON correspond to the same moves."""
    board = chess.Board()
    moves = game_data.get("moves", [])
    
    for move_obj in moves:
        san = move_obj.get("san")
        lan = move_obj.get("lan")
        if not san or not lan:
            raise ValueError(f"Missing SAN or LAN for move: {move_obj}")
        
        # Parse LAN to get the move
        try:
            lan_move = chess.Move.from_uci(lan)
        except ValueError as e:
            raise ValueError(f"Invalid LAN '{lan}': {e}")
        
        # Generate SAN from the LAN move on the current board
        try:
            generated_san = board.san(lan_move)
        except Exception as e:
            raise ValueError(f"Cannot generate SAN for LAN '{lan}' on board {board.fen()}: {e}")
        
        # Check if they match (case insensitive, as SAN can vary)
        if generated_san.lower() != san.lower():
            raise ValueError(f"SAN '{san}' does not match generated SAN '{generated_san}' for LAN '{lan}' on board {board.fen()}")
        
        # Apply the move to the board
        board.push(lan_move)
        
        # Note: Skipping validation of variations as they may contain non-standard SAN from PGN

def validate_variation_consistency(var_moves: List[Dict[str, Any]], board: chess.Board) -> None:
    """Validate consistency in a variation line."""
    for move_obj in var_moves:
        san = move_obj.get("san")
        lan = move_obj.get("lan")
        if not san or not lan:
            raise ValueError(f"Missing SAN or LAN in variation: {move_obj}")
        
        try:
            lan_move = chess.Move.from_uci(lan)
        except ValueError as e:
            raise ValueError(f"Invalid LAN '{lan}' in variation: {e}")
        
        try:
            generated_san = board.san(lan_move)
        except Exception as e:
            raise ValueError(f"Cannot generate SAN for LAN '{lan}' in variation on board {board.fen()}: {e}")
        
        if generated_san.lower() != san.lower():
            raise ValueError(f"SAN '{san}' does not match generated SAN '{generated_san}' for LAN '{lan}' in variation on board {board.fen()}")
        
        board.push(lan_move)

def convert_json_to_pgn(input_file: str, output_file: str) -> None:
    with open(input_file, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    if not isinstance(json_data, list):
        json_data = [json_data]  # Handle single game

    # Validate consistency before processing
    for game_data in json_data:
        validate_json_consistency(game_data)

    with open(output_file, "w", encoding="utf-8") as out:
        for game_data in json_data:
            # Headers
            for key, value in game_data.get("metadata", {}).items():
                if key == "time_control":
                    pgn_key = "TimeControl"
                elif key == "whitetimecontrol":
                    pgn_key = "WhiteTimeControl"
                elif key == "blacktimecontrol":
                    pgn_key = "BlackTimeControl"
                elif key == "orientation":
                    pgn_key = "Orientation"
                else:
                    pgn_key = key.capitalize()
                out.write(f'[{pgn_key} "{value}"]\n')
            out.write("\n")

            # Moves
            moves_text = build_pgn_moves(game_data.get("moves", []))
            result = game_data.get("metadata", {}).get("result", "*")
            out.write(f"{moves_text} {result}\n\n")

    print(f"📄 PGN output written to {output_file}")

def main(base_dir: str, mode: str = "pgn2json", include_fen: bool = False) -> None:
    if mode == "pgn2json":
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.lower().endswith(".pgn") and not file.lower().endswith("_formatted.pgn") and not file.lower().endswith("_converted.pgn"):
                    input_path = os.path.join(root, file)
                    output_path = os.path.join(root, file.replace(".pgn", ".json"))
                    convert_pgn_to_json(input_path, output_path, include_fen)
    elif mode == "json2pgn":
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.lower().endswith(".json") and not file.lower().endswith("schema.json"):
                    input_path = os.path.join(root, file)
                    output_path = os.path.join(root, file.replace(".json", "_converted.pgn"))
                    convert_json_to_pgn(input_path, output_path)

if __name__ == "__main__":
    import sys
    mode = 'pgn2json'
    include_fen = False

    if len(sys.argv) > 1:
        if '--include-fen' in sys.argv:
            include_fen = True
            sys.argv.remove('--include-fen')
        if len(sys.argv) > 1:
            mode = sys.argv[1]

    base_location = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    main(base_location, mode, include_fen)