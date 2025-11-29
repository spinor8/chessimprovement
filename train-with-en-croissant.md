
# 🥐 Chess Training with En Croissant + JSON Tools

## 1. Launch En Croissant
- Open the **En Croissant** application on your system.
- Make sure you’re on the **Play** tab (where you can start games against the engine).

---

## 2. Set Up the Opening Position
- Search for opening in Lichess, https://lichess.org/opening and copy the PGN.
- In En Croissant, go to the Files tab (not Play).
- Click Create → Repertoire.
- Open the new repertoire file.
- Enter moves copied earlier.

---

## 3. Play the Game
- Click on the eye in repertoire view.
- Go to the position in question by clicking on the move in the right panel.
- In the left panel, there is a archery target. Click on that to play from here.
- Choose the engine and time control. Then start game.

---

## 5. Save the Game
- When one gives up, go to Info and copy the full PGN.
- Edit accordingly into the appropriate PGN file.

---

## 6. Future Analysis & Annotation
- Open saved PGNs in En Croissant or another database tool (ChessBase, SCID, ChessX).
- **Alternative: Convert to JSON format** for advanced analysis:
  ```bash
  python chesstools/pgn2json_converter.py --include-fen
  ```
- Use **annotation tools**:
  - Add comments to moves.
  - Insert variation trees.
  - Highlight critical positions.
- Keep a version‑controlled archive (GitHub or local Git) to ensure annotations are never lost.

---

## ✅ Workflow Summary
1. Launch En Croissant.  
2. Use **Position Setup** to reach Modern Benoni.  
3. Configure engine with **15 min per side**.  
4. Play the game.  
5. Save PGN after each session.  
6. **Convert to JSON** for structured storage: `python chesstools/pgn2json_converter.py --include-fen`
7. Annotate later in your preferred database tool.  

---

## 🔄 JSON Alternative Workflow

For more advanced analysis with unlimited variations and position tracking:

1. **Convert PGN to JSON**: `python chesstools/pgn2json_converter.py --include-fen`
2. **Edit JSON files** with your analysis and engine evaluations
3. **Validate** against schema: JSON files are automatically validated
4. **Store in Git** for version control of annotations
5. **Future**: Build custom viewers that support the full JSON feature set  


