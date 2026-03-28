# Extraction Pipeline

Python scripts that extract practice word data from source PDFs and output structured JSON for the web app.

## Usage

```bash
# Run the extraction pipeline
npm run extract
# or directly:
uv run python scripts/extract_decoding_data.py
```

Output: `src/data/decoding-words.json`

## How It Works

The pipeline has three stages:

### 1. Email Parsing
Reads teacher email PDFs from `materials/decoding/sophie-emails/` and extracts:
- **Spelling sound patterns** (e.g., `ai`, `ay`) and their phonemes (e.g., `/a/`)
- **Example words** for each pattern
- **Sight words** (high-frequency words)
- **Associated book name** and email date

### 2. Book Parsing
Reads book PDFs from `materials/decoding/reading-group-books/` and extracts all story text, then tokenizes into unique words.

### 3. Cross-Referencing
For each word in a book:
- Checks if it contains a spelling pattern from the associated email's spelling unit
- Generates a **decoding breakdown** by splitting the word around the matched pattern (e.g., "lake" → `["l", "a_e", "k"]`)
- Only words matching a known spelling pattern are included as decoding words

## Output Format

```json
{
  "spellingUnits": [
    {
      "id": "ai_ay",
      "patterns": ["ai", "ay"],
      "phoneme": "/a/",
      "examples": ["paid", "play"],
      "sourceEmail": "2026-03-13",
      "book": "A Play Day with My Brother Ray"
    }
  ],
  "decodingWords": [
    {
      "word": "lake",
      "spellingUnitId": "a_e",
      "decodingBreakdown": ["l", "a_e", "k"],
      "book": "A Hike by the Lake"
    }
  ],
  "sightWords": [
    {
      "word": "walk",
      "sourceEmail": "2026-03-13",
      "book": "A Play Day with My Brother Ray"
    }
  ]
}
```

## Extending

The script uses a registry pattern. To add a new source type:

1. Write a parser function that returns structured data
2. Add it to the `SOURCE_PARSERS` registry in the script
3. The cross-referencing stage will automatically incorporate new data
