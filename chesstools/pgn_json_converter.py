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
            var_moves = serialize_moves(var)
            variations.append({
                "label": "",
                "line": var_moves
            })

        move_obj = {
            "san": san,
            "move_number": move_number,
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

def main(base_dir):
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith(".pgn") and not file.lower().endswith("_formatted.pgn"):
                input_path = os.path.join(root, file)
                output_path = os.path.join(root, file.replace(".pgn", ".json"))
                convert_pgn_to_json(input_path, output_path)

if __name__ == "__main__":
    base_location = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    main(base_location)