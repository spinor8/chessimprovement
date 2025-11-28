
# 📐 JSON Schema for Chess Game Archives

## 1. Motivation

PGN is the de facto exchange format for chess games, but it has critical limitations:

- **Parser divergence**: Different GUIs interpret comments and nesting differently.  
- **Nesting limits**: Deep variation trees often break parsers.  
- **Flat metadata**: PGN tags are simple key–value pairs, unsuitable for structured annotations.  
- **Auditability issues**: PGN is text, but lacks a formal schema for validation.

For an **audit‑grade study workflow**, JSON offers:

- **Unlimited nesting**: Recursive structures handle deep repertoires.  
- **Structured annotations**: Comments, engine evals, and tags stored consistently.  
- **Schema validation**: Enforce integrity with JSON Schema + CI pipelines.  
- **Diff‑friendly**: Git shows exactly what changed in annotations or variations.  

PGN remains useful for **interoperability** (import/export into GUIs), but JSON should be the **canonical archive**.

---

## 2. Design Principles

- **Recursive move tree**: Each move can contain nested variations.  
- **Annotations object**: Flexible container for comments, evals, tags.  
- **Metadata block**: Mirrors PGN tags but extensible.  
- **Validation**: Schema ensures consistency across commits.  
- **Auditability**: Every change is visible in Git diffs.  

---

## 3. JSON Schema Definition

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Chess Game Schema",
  "description": "Schema for storing chess games with nested variations and annotations",
  "type": "object",
  "properties": {
    "game_id": {
      "type": "string",
      "description": "Unique identifier for the game (filename, UUID, etc.)"
    },
    "metadata": {
      "type": "object",
      "description": "Game metadata similar to PGN tags",
      "properties": {
        "event": { "type": "string" },
        "site": { "type": "string" },
        "date": { "type": "string", "format": "date" },
        "round": { "type": "string" },
        "white": { "type": "string" },
        "black": { "type": "string" },
        "result": { "type": "string", "enum": ["1-0", "0-1", "1/2-1/2", "*"] },
        "time_control": { "type": "string" }
      },
      "required": ["event", "date", "white", "black", "result"]
    },
    "moves": {
      "type": "array",
      "description": "Mainline moves with nested variations",
      "items": { "$ref": "#/$defs/move" }
    },
    "notes": {
      "type": "string",
      "description": "General notes about the game"
    }
  },
  "required": ["game_id", "metadata", "moves"],
  "$defs": {
    "move": {
      "type": "object",
      "properties": {
        "san": {
          "type": "string",
          "description": "Move in Standard Algebraic Notation"
        },
        "move_number": {
          "type": "integer",
          "description": "Move number in the game"
        },
        "annotations": {
          "type": "object",
          "description": "Annotations for the move",
          "properties": {
            "comment": { "type": "string" },
            "eval": { "type": "string" },
            "tags": {
              "type": "array",
              "items": { "type": "string" }
            }
          }
        },
        "variations": {
          "type": "array",
          "description": "Alternative lines branching from this move",
          "items": {
            "type": "object",
            "properties": {
              "label": { "type": "string" },
              "line": {
                "type": "array",
                "items": { "$ref": "#/$defs/move" }
              }
            },
            "required": ["line"]
          }
        }
      },
      "required": ["san", "move_number"]
    }
  }
}
```

---

## 4. Example Instance

```json
{
  "game_id": "benoni_training_2025_11_28",
  "metadata": {
    "event": "Training vs Engine",
    "site": "En Croissant",
    "date": "2025-11-28",
    "round": "1",
    "white": "SP",
    "black": "Engine",
    "result": "1-0",
    "time_control": "15+0"
  },
  "moves": [
    {
      "san": "d4",
      "move_number": 1,
      "annotations": {
        "comment": "Main line",
        "eval": "+0.20",
        "tags": ["opening", "Benoni"]
      },
      "variations": [
        {
          "label": "Alternative line",
          "line": [
            {
              "san": "Nf6",
              "move_number": 1,
              "annotations": {
                "comment": "Standard reply",
                "eval": "+0.15"
              },
              "variations": []
            }
          ]
        }
      ]
    },
    {
      "san": "c4",
      "move_number": 2,
      "annotations": {},
      "variations": []
    }
  ],
  "notes": "Modern Benoni training game"
}
```

---

## 5. Workflow Integration

- **Canonical archive**: Store JSON files in Git.  
- **Validation**: Run `ajv` or similar validator in GitHub Actions to enforce schema.  
- **Interoperability**: Convert JSON ↔ PGN for GUI use.  
- **Analytics**: Build SQLite from JSON for fast queries.  

---

✅ With this schema, you can **preserve annotations**, **handle unlimited nesting**, and **validate every commit**. PGN remains your interchange format, but JSON becomes your **source of truth**.
