from pgn2json_converter import main 
import os

if __name__ == "__main__":
    mode = 'json2pgn'
    base_location = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    main(base_location, mode)

    