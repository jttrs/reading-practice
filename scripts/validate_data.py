"""
Validate the generated decoding-words.json against the phoneme reference.

Checks:
1. Breakdown integrity — concatenated elements reconstruct the original word
2. Breakdown granularity — no consonant clusters that should be split
3. Word-phoneme classification — each word contains its assigned grapheme
4. TTS completeness — ttsBreakdown length matches decodingBreakdown
5. TTS values — no raw split-digraph notation (a_e) or empty strings
6. No duplicates — across decodingWords and sightWords
7. No excluded words leaking through
8. Phoneme reference — every phoneme has tts and ipa
9. Sight word TTS — every sight word has ttsWord

Usage:
    uv run python scripts/validate_data.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phoneme_data import PHONEMES, DIGRAPHS, CONSONANT_TTS, VOWEL_GRAPHEMES

DATA_PATH = Path("src/data/decoding-words.json")

# Import EXCLUDE_WORDS from extraction script
from extract_decoding_data import EXCLUDE_WORDS


class ValidationError:
    def __init__(self, check: str, message: str):
        self.check = check
        self.message = message

    def __str__(self) -> str:
        return f"[{self.check}] {self.message}"


def load_data() -> dict:
    with open(DATA_PATH) as f:
        return json.load(f)


def validate_phoneme_reference(data: dict) -> list[ValidationError]:
    """Every phoneme in the JSON must have tts and ipa."""
    errors = []
    for p in data.get("phonemes", []):
        if not p.get("tts"):
            errors.append(ValidationError("phoneme_ref", f"Phoneme '{p['id']}' missing tts"))
        if not p.get("ipa"):
            errors.append(ValidationError("phoneme_ref", f"Phoneme '{p['id']}' missing ipa"))
        if not p.get("spellings"):
            errors.append(ValidationError("phoneme_ref", f"Phoneme '{p['id']}' has no spellings"))
    return errors


def validate_breakdown_integrity(data: dict) -> list[ValidationError]:
    """Concatenating breakdown elements (expanding split digraphs) must reconstruct the word."""
    errors = []
    for w in data["decodingWords"]:
        # Expand split digraphs: "a_e" → "a" + "e" (but 'e' goes at end)
        parts = []
        pending_end = None
        for el in w["decodingBreakdown"]:
            if "_" in el:
                first, last = el.split("_")
                parts.append(first)
                pending_end = last
            else:
                parts.append(el)
        if pending_end:
            parts.append(pending_end)

        reconstructed = "".join(parts)
        if reconstructed != w["word"]:
            errors.append(ValidationError(
                "breakdown_integrity",
                f"'{w['word']}': breakdown {w['decodingBreakdown']} → '{reconstructed}' != '{w['word']}'"
            ))
    return errors


def validate_breakdown_granularity(data: dict) -> list[ValidationError]:
    """No breakdown element should be a consonant cluster that's not a digraph."""
    errors = []
    vowels = set("aeiou")

    for w in data["decodingWords"]:
        for el in w["decodingBreakdown"]:
            # Skip pattern elements (vowel graphemes, split digraphs)
            if "_" in el:
                continue
            if el in VOWEL_GRAPHEMES:
                continue

            # Check if it's a multi-consonant element that's not a digraph
            if len(el) >= 2 and all(c not in vowels for c in el):
                if el not in DIGRAPHS:
                    errors.append(ValidationError(
                        "breakdown_granularity",
                        f"'{w['word']}': element '{el}' is a consonant cluster "
                        f"that should be split (breakdown: {w['decodingBreakdown']})"
                    ))
    return errors


def validate_word_phoneme_classification(data: dict) -> list[ValidationError]:
    """Each decoding word must contain the grapheme from its assigned spelling unit."""
    errors = []
    unit_map = {u["id"]: u for u in data["spellingUnits"]}

    for w in data["decodingWords"]:
        unit = unit_map.get(w["spellingUnitId"])
        if not unit:
            errors.append(ValidationError(
                "word_phoneme",
                f"'{w['word']}': spellingUnitId '{w['spellingUnitId']}' not found"
            ))
            continue

        # Word must contain at least one of the unit's patterns
        word = w["word"]
        has_pattern = False
        for pattern in unit["patterns"]:
            if "_" in pattern:
                # Split digraph: check vowel and final letter are present in correct order
                vowel, final = pattern.split("_")
                idx_v = word.find(vowel)
                if idx_v >= 0 and word.endswith(final) or word.endswith(final + "s"):
                    has_pattern = True
                    break
            elif pattern in word:
                has_pattern = True
                break

        if not has_pattern:
            errors.append(ValidationError(
                "word_phoneme",
                f"'{w['word']}': doesn't contain any pattern from unit '{w['spellingUnitId']}' "
                f"(patterns: {unit['patterns']})"
            ))
    return errors


def validate_tts_completeness(data: dict) -> list[ValidationError]:
    """ttsBreakdown must have same length as decodingBreakdown; ttsWord must exist."""
    errors = []
    for w in data["decodingWords"]:
        if len(w["ttsBreakdown"]) != len(w["decodingBreakdown"]):
            errors.append(ValidationError(
                "tts_completeness",
                f"'{w['word']}': ttsBreakdown length {len(w['ttsBreakdown'])} "
                f"!= decodingBreakdown length {len(w['decodingBreakdown'])}"
            ))
        if not w.get("ttsWord"):
            errors.append(ValidationError(
                "tts_completeness",
                f"'{w['word']}': missing ttsWord"
            ))
    return errors


def validate_tts_values(data: dict) -> list[ValidationError]:
    """TTS values must not contain raw split-digraph notation or empty strings."""
    errors = []
    for w in data["decodingWords"]:
        for i, tts_el in enumerate(w["ttsBreakdown"]):
            if not tts_el:
                errors.append(ValidationError(
                    "tts_values",
                    f"'{w['word']}': empty ttsBreakdown element at index {i}"
                ))
            if "_" in tts_el:
                errors.append(ValidationError(
                    "tts_values",
                    f"'{w['word']}': ttsBreakdown contains raw split-digraph '{tts_el}' at index {i}"
                ))
    return errors


def validate_no_duplicates(data: dict) -> list[ValidationError]:
    """No duplicate words in decodingWords or sightWords."""
    errors = []

    decoding_words = [w["word"] for w in data["decodingWords"]]
    seen = set()
    for word in decoding_words:
        if word in seen:
            errors.append(ValidationError("no_duplicates", f"Duplicate decoding word: '{word}'"))
        seen.add(word)

    sight_words = [s["word"] for s in data["sightWords"]]
    seen_sw = set()
    for word in sight_words:
        if word in seen_sw:
            errors.append(ValidationError("no_duplicates", f"Duplicate sight word: '{word}'"))
        seen_sw.add(word)

    return errors


def validate_no_excluded_words(data: dict) -> list[ValidationError]:
    """No word from EXCLUDE_WORDS should appear in decodingWords."""
    errors = []
    for w in data["decodingWords"]:
        if w["word"] in EXCLUDE_WORDS:
            errors.append(ValidationError(
                "no_excluded",
                f"Excluded word '{w['word']}' found in decodingWords"
            ))
    return errors


def validate_sight_word_tts(data: dict) -> list[ValidationError]:
    """Every sight word must have ttsWord."""
    errors = []
    for s in data["sightWords"]:
        if not s.get("ttsWord"):
            errors.append(ValidationError(
                "sight_tts",
                f"Sight word '{s['word']}' missing ttsWord"
            ))
    return errors


def main():
    data = load_data()

    all_checks = [
        ("Phoneme reference", validate_phoneme_reference),
        ("Breakdown integrity", validate_breakdown_integrity),
        ("Breakdown granularity", validate_breakdown_granularity),
        ("Word-phoneme classification", validate_word_phoneme_classification),
        ("TTS completeness", validate_tts_completeness),
        ("TTS values", validate_tts_values),
        ("No duplicates", validate_no_duplicates),
        ("No excluded words", validate_no_excluded_words),
        ("Sight word TTS", validate_sight_word_tts),
    ]

    total_errors = 0
    for name, check_fn in all_checks:
        errors = check_fn(data)
        if errors:
            print(f"FAIL: {name} ({len(errors)} errors)")
            for e in errors:
                print(f"  {e}")
            total_errors += len(errors)
        else:
            print(f"PASS: {name}")

    print()
    if total_errors:
        print(f"{total_errors} validation error(s) found")
        sys.exit(1)
    else:
        stats = (
            f"{len(data.get('phonemes', []))} phonemes, "
            f"{len(data['spellingUnits'])} spelling units, "
            f"{len(data['decodingWords'])} decoding words, "
            f"{len(data['sightWords'])} sight words"
        )
        print(f"All validations passed ({stats})")


if __name__ == "__main__":
    main()
