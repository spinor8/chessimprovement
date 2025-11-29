import os
import chess.pgn
import re
from chess.pgn import StringExporter
from typing import Match

def indent_variations(text: str) -> str:
    def indent_match(match: Match[str]) -> str:
        content = match.group(1).strip()
        # Recursively indent nested variations
        content = re.sub(r'\((.*?)\)', indent_match, content, flags=re.DOTALL)
        lines = content.split('\n')
        indented_lines = ['  ' + line for line in lines if line.strip()]
        indented = '\n'.join(indented_lines)
        return f'(\n{indented}\n)'
    return re.sub(r'\((.*?)\)', indent_match, text, flags=re.DOTALL)

def validate_and_reformat_pgn(input_file: str, output_file: str) -> None:
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

    with open(output_file, "w", encoding="utf-8") as out:
        for idx, game in enumerate(games):
            # Write headers
            for tag in game.headers:
                out.write(f'[{tag} "{game.headers[tag]}"]\n')
            out.write("\n")

            # Export moves with variations and comments, then format to one pair per line
            exporter = StringExporter(headers=False, variations=True, comments=True)
            game.accept(exporter)
            exported = str(exporter)
            # Remove black move prefixes to pair moves
            exported = re.sub(r'\s\d+\.\.\.\s', ' ', exported)
            # Attach comments without leading space
            exported = exported.replace(" {", "{")
            formatted = re.sub(r'(\d+\.\s)', r'\n\1', exported.strip()).lstrip('\n')
            # Indent variations
            formatted = indent_variations(formatted)
            # Join split pairs
            formatted = re.sub(r'(\n\d+\. \w+.*?)\n([A-Za-z]\w*.*?)(?=\n)', r'\1 \2', formatted)
            # Move standalone comments to previous line
            formatted = re.sub(r'(\w+.*?)\n(\{.*?\})\n+', r'\1 \2\n', formatted)
            out.write(formatted)
            out.write("\n")

            if idx < len(games) - 1:
                out.write("\n\n")

    print(f"📂 Reformatted PGN written to {output_file}")


def main(base_dir: str) -> None:
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith(".pgn") and not file.lower().endswith("_formatted.pgn"):
                input_path = os.path.join(root, file)
                output_path = os.path.join(root, file.replace(".pgn", "_formatted.pgn"))
                validate_and_reformat_pgn(input_path, output_path)



if __name__ == "__main__":
    base_location = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    main(base_location)
