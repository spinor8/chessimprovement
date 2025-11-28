# ⚙️ GitHub Actions Pipeline for JSON Schema Validation

```yaml
name: Validate Chess JSON Schema

on:
  push:
    paths:
      - "games/**/*.json"   # only run when JSON game files change
  pull_request:
    paths:
      - "games/**/*.json"

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: Install AJV CLI
        run: npm install -g ajv-cli

      - name: Validate JSON files against schema
        run: |
          for file in $(find games -name "*.json"); do
            echo "Validating $file"
            ajv validate -s schema/chess-game-schema.json -d "$file"
          done
```

---

## 🔍 Explanation

- **Trigger**: Runs on `push` and `pull_request` when any JSON file under `games/` changes.  
- **Environment**: Uses `ubuntu-latest` with Node.js 20.  
- **Validator**: Installs [`ajv-cli`](https://ajv.js.org/) — a JSON Schema validator.  
- **Schema location**: Assumes your schema is stored at `schema/chess-game-schema.json`.  
- **Validation loop**: Iterates through all JSON files in `games/` and validates them against the schema.  

---

## ✅ Workflow Integration

- Place your schema in `schema/chess-game-schema.json`.  
- Store your annotated games in `games/` (e.g., `games/benoni/2025-11-28.json`).  
- Every commit or PR will be blocked if any JSON file fails validation.  
- Git diffs remain clean and audit‑friendly.  

---

This pipeline locks in **auditability**: no malformed JSON, no broken nesting, no missing required fields.  

Would you like me to also add a **second job** that automatically regenerates PGN files from JSON (using `python-chess`) so you always have GUI‑ready files alongside your canonical archive? That would complete the JSON↔PGN workflow.
