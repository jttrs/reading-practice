# Scripts

Python scripts that extract practice word data from source PDFs, generate audio, and validate the output.

## Quick Reference

```bash
npm run extract          # Extract words from PDFs → JSON
npm run generate-audio    # Generate TTS audio files
npm run validate          # Run 12 validation checks
npm run test              # Full pipeline: validate + build + e2e tests
```

## Scripts

### extract_decoding_data.py

Main extraction pipeline. Reads teacher email PDFs and book PDFs, cross-references them, and outputs `src/data/decoding-words.json`.

The pipeline has three stages:

1. **Email Parsing** — Reads PDFs from `materials/decoding/sophie-emails/` and extracts spelling patterns, example words, sight words, and book names.
2. **Book Parsing** — Reads PDFs from `materials/decoding/reading-group-books/` and tokenizes into unique words.
3. **Cross-Referencing** — Matches book words to spelling patterns, generates decoding breakdowns, and looks up real phonemes via Datamuse.

### generate_audio.py

Generates MP3 audio files using Google Cloud Text-to-Speech (Neural2-F voice). Produces:
- `public/audio/phonemes/{id}.mp3` — Isolated phoneme sounds using SSML `<phoneme>` IPA tags
- `public/audio/words/{word}.mp3` — Whole-word pronunciations

Requires Google Cloud credentials (`GOOGLE_APPLICATION_CREDENTIALS` or ADC).

### validate_data.py

Runs 12 validation checks against the generated JSON and audio files: breakdown integrity, granularity, word-phoneme classification, TTS completeness, TTS values, TTS manifest, duplicates, excluded words, phoneme reference, sight word TTS, suffix pronunciation, and audio file existence.

### phoneme_data.py

Single source of truth for the 44-phoneme system (Letterland). Contains:
- `PHONEMES` — Full phoneme definitions (IPA, category, spellings, TTS)
- `ARPABET_TO_AUDIO` — Manifest mapping CMU ARPAbet phonemes to audio IDs + IPA
- `VALID_AUDIO_IDS` — Set of all valid audio file identifiers
- Helper functions for suffix pronunciation rules (`-ed`, `-s`)

### datamuse.py

Client for the [Datamuse API](https://www.datamuse.com/api/) (CMU Pronouncing Dictionary). Looks up real ARPAbet phonemes for words and maps them through the manifest to audio IDs. Results are cached in `datamuse_cache.json` to avoid repeat API calls.

Handles multi-phoneme graphemes (r-controlled vowels, "all", suffixes) and silent letters via alignment.

### review_data.py

Utility to pretty-print the generated JSON for manual review.

### check_emails.py

Debugging utility to inspect parsed email data.

## Output Format

The extraction pipeline outputs `src/data/decoding-words.json`:

```json
{
  "phonemes": [
    {
      "id": "b",
      "ipa": "/b/",
      "category": "consonant",
      "tts": "buh",
      "spellings": ["b", "bb"],
      "source": "reference"
    }
  ],
  "spellingUnits": [
    {
      "id": "ai_ay",
      "patterns": ["ai", "ay"],
      "phoneme": "/a/",
      "ipa": "",
      "examples": ["paid", "play"],
      "sourceEmail": "2026-03-13",
      "book": "A Play Day with My Brother Ray"
    }
  ],
  "decodingWords": [
    {
      "word": "away",
      "spellingUnitId": "ai_ay",
      "decodingBreakdown": ["a", "w", "ay"],
      "ttsBreakdown": ["uh", "wuh", "ay"],
      "ttsWord": "away",
      "book": "A Play Day with My Brother Ray"
    }
  ],
  "sightWords": [
    {
      "word": "walk",
      "ttsWord": "walk",
      "sourceEmail": "2026-03-13",
      "book": "A Play Day with My Brother Ray"
    }
  ]
}
```

## Extending

The extraction script uses a registry pattern. To add a new source type:

1. Write a parser function that returns structured data
2. Add it to the `SOURCE_PARSERS` registry in the script
3. The cross-referencing stage will automatically incorporate new data
