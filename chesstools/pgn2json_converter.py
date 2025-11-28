import os
import json
import chess.pgn

def serialize_game(game):
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
    date = metadata.get("date", "unknown")
    game_id = f"{event}_{date}".replace(" ", "_").replace("/", "_")

    # Serialize moves
    moves = serialize_moves(game)

    return {
        "game_id": game_id,
        "metadata": metadata,
        "moves": moves,
        "notes": ""
    }

def serialize_moves(node):
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
                "annotations": var_annotations,
                "variations": []
            }]
            var_board.push(var_move)
            rest_moves = serialize_moves(var_node)
            var_moves.extend(rest_moves)
            variations.append({"label": "", "line": var_moves})

        move_obj = {
            "san": san,
            "move_number": move_number,
            "color": "w" if board.turn == chess.WHITE else "b",
            "annotations": annotations,
            "variations": variations
        }
        moves.append(move_obj)

        # Move to next
        board.push(move)
        current = child

    return moves

def convert_pgn_to_json(input_file, output_file):
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

    json_data = [serialize_game(game) for game in games]

    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(json_data, out, indent=2)

    print(f"📄 JSON output written to {output_file}")

def build_pgn_moves(moves_list):
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

def convert(file_path):
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

def convert_json_to_pgn(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    if not isinstance(json_data, list):
        json_data = [json_data]  # Handle single game

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

def main(base_dir, mode="pgn2json"):
    if mode == "pgn2json":
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.lower().endswith(".pgn") and not file.lower().endswith("_formatted.pgn") and not file.lower().endswith("_converted.pgn"):
                    input_path = os.path.join(root, file)
                    output_path = os.path.join(root, file.replace(".pgn", ".json"))
                    convert_pgn_to_json(input_path, output_path)
    elif mode == "json2pgn":
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.lower().endswith(".json"):
                    input_path = os.path.join(root, file)
                    output_path = os.path.join(root, file.replace(".json", "_converted.pgn"))
                    convert_json_to_pgn(input_path, output_path)

if __name__ == "__main__":
    mode = 'pgn2json'
    base_location = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    main(base_location, mode)