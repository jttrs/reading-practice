"""
Datamuse API client for phoneme lookup.

Looks up real ARPAbet phonemes for words via the Datamuse API (CMU
Pronouncing Dictionary). Results are cached locally to avoid repeat API calls.

Usage:
    from datamuse import get_word_phonemes, map_breakdown_to_audio

    arpabet = get_word_phonemes("today")       # ["T", "AH", "D", "EY"]
    audio_ids = map_breakdown_to_audio(
        ["t", "o", "d", "ay"], arpabet
    )                                           # ["tuh", "uh", "duh", "ay"]
"""

from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

from phoneme_data import ARPABET_TO_AUDIO

CACHE_PATH = Path(__file__).resolve().parent / "datamuse_cache.json"
API_URL = "https://api.datamuse.com/words?sp={word}&qe=sp&md=r&max=1"


def _load_cache() -> dict[str, list[str]]:
    """Load the local cache of word → ARPAbet phonemes."""
    if CACHE_PATH.exists():
        with open(CACHE_PATH) as f:
            return json.load(f)
    return {}


def _save_cache(cache: dict[str, list[str]]) -> None:
    """Save the cache to disk."""
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2, sort_keys=True)


def _strip_stress(phoneme: str) -> str:
    """Remove stress markers (0, 1, 2) from an ARPAbet phoneme."""
    return re.sub(r"[0-9]", "", phoneme)


def _fetch_from_api(word: str) -> list[str] | None:
    """Fetch ARPAbet phonemes for a word from the Datamuse API."""
    url = API_URL.format(word=urllib.request.quote(word))
    resp = urllib.request.urlopen(url, timeout=10)
    data = json.loads(resp.read())
    if not data:
        return None
    for tag in data[0].get("tags", []):
        if tag.startswith("pron:"):
            raw = tag.replace("pron:", "").strip().split()
            return [_strip_stress(p) for p in raw]
    return None


def get_word_phonemes(word: str, cache: dict[str, list[str]] | None = None) -> list[str]:
    """Get ARPAbet phonemes for a word, using cache when available.

    Args:
        word: The word to look up.
        cache: Optional pre-loaded cache dict. If None, loads from disk.

    Returns:
        List of ARPAbet phonemes with stress markers stripped.

    Raises:
        ValueError: If the word is not found in Datamuse.
    """
    if cache is None:
        cache = _load_cache()

    if word in cache:
        return cache[word]

    phonemes = _fetch_from_api(word)
    if phonemes is None:
        raise ValueError(f"Word not found in Datamuse: {word!r}")

    cache[word] = phonemes
    _save_cache(cache)
    return phonemes


def map_breakdown_to_audio(breakdown: list[str], arpabet: list[str], word: str) -> list[str]:
    """Map a grapheme breakdown to audio IDs using ARPAbet phonemes.

    Aligns the breakdown with ARPAbet phonemes, handling graphemes that
    map to multiple phonemes (r-controlled vowels, "all", suffixes)
    and silent letters.

    Args:
        breakdown: Grapheme breakdown (e.g., ["t", "o", "d", "ay"])
        arpabet: ARPAbet phonemes (e.g., ["T", "AH", "D", "EY"])
        word: The word (for error messages)

    Returns:
        List of audio IDs (e.g., ["tuh", "uh", "duh", "ay"])

    Raises:
        ValueError: If alignment fails or an ARPAbet phoneme is unknown.
    """
    audio_ids: list[str] = []
    a_idx = 0  # position in arpabet

    for b_idx, grapheme in enumerate(breakdown):
        # --- Multi-phoneme graphemes (consume 2+ ARPAbet phonemes) ---
        multi = _MULTI_PHONEME_GRAPHEMES.get(grapheme)
        if multi:
            for phonemes, audio_id in multi:
                n = len(phonemes)
                if a_idx + n <= len(arpabet) and tuple(arpabet[a_idx:a_idx + n]) == phonemes:
                    audio_ids.append(audio_id)
                    a_idx += n
                    break
            else:
                raise ValueError(
                    f"Grapheme {grapheme!r} in {word!r} didn't match expected "
                    f"phonemes at position {a_idx} (remaining: {arpabet[a_idx:]})"
                )
            continue

        # --- Silent letters (no remaining phonemes to consume) ---
        if a_idx >= len(arpabet):
            # Silent trailing letter (e.g. silent 'e' in "ooze")
            audio_ids.append("")
            continue

        # --- Silent vowel in compound words ---
        # A single vowel grapheme aligned with a consonant phoneme is silent
        # (e.g. 'e' in "baseball" = base+ball, 'e' in "dodgeball" = dodge+ball)
        if len(grapheme) == 1 and grapheme in "aeiou" and arpabet[a_idx] in _ARPABET_CONSONANTS:
            audio_ids.append("")
            continue

        # --- Pedagogical override for R-modified vowels ---
        # CMU uses different phonemes before R (e.g. IH+R for "deer", AO+R
        # for "roar"), but for teaching, the vowel grapheme should sound like
        # its normal long-vowel sound, not the R-colored variant.
        phoneme = arpabet[a_idx]
        override = _R_VOWEL_OVERRIDES.get(grapheme)
        if override and phoneme in override and a_idx + 1 < len(arpabet) and arpabet[a_idx + 1] == "R":
            audio_ids.append(override[phoneme])
            a_idx += 1
            continue

        # --- Standard 1:1 mapping ---
        entry = ARPABET_TO_AUDIO.get(phoneme)
        if entry is None:
            raise ValueError(
                f"Unknown ARPAbet phoneme {phoneme!r} "
                f"(grapheme={grapheme!r}) in word {word!r}"
            )
        audio_ids.append(entry["audio_id"])
        a_idx += 1

    if a_idx != len(arpabet):
        raise ValueError(
            f"Alignment incomplete for {word!r}: consumed {a_idx}/{len(arpabet)} "
            f"phonemes (breakdown={breakdown}, arpabet={arpabet})"
        )

    return audio_ids


# ARPAbet consonant phonemes (for silent vowel detection)
_ARPABET_CONSONANTS = {
    "B", "CH", "D", "DH", "F", "G", "HH", "JH", "K", "L", "M", "N",
    "NG", "P", "R", "S", "SH", "T", "TH", "V", "W", "Y", "Z", "ZH",
}

# Pedagogical overrides for R-modified vowels.
# CMU uses different phonemes before R (IH for NEAR, AO for FORCE), but
# the vowel grapheme should play its normal long-vowel sound when sounding out.
# Format: grapheme → {arpabet_phoneme: audio_id_to_use_instead}
_R_VOWEL_OVERRIDES: dict[str, dict[str, str]] = {
    "ee": {"IH": "ee"},   # "deer": IH+R but 'ee' should sound like /iː/
    "ea": {"IH": "ee"},   # "dear", "clear": same
    "oa": {"AO": "oh"},   # "roar": AO+R but 'oa' should sound like /oʊ/
}

# Graphemes that consume multiple ARPAbet phonemes.
# Each maps to a list of (phoneme_tuple, audio_id) tried in order.
_MULTI_PHONEME_GRAPHEMES: dict[str, list[tuple[tuple[str, ...], str]]] = {
    # R-controlled vowels
    "ar":  [(("AA", "R"), "ar")],
    "or":  [(("AO", "R"), "or")],
    "ear": [(("IH", "R"), "ear"), (("IY", "R"), "ear")],
    "air": [(("EH", "R"), "air")],
    # L-controlled
    "all": [(("AO", "L"), "awl")],
    # Suffixes
    "ed":  [(("IH", "D"), "id"), (("AH", "D"), "id"),  # /ɪd/ after t/d
            (("D",), "duh"), (("T",), "tuh")],          # single phoneme
    "ing": [(("IH", "NG"), "ing"), (("AH", "NG"), "ing"),
            (("NG",), "ng")],
}


def prefetch_all(words: list[str]) -> dict[str, list[str]]:
    """Fetch and cache phonemes for all words at once.

    Returns the cache dict for reuse.
    """
    cache = _load_cache()
    missing = [w for w in words if w not in cache]

    if missing:
        print(f"Fetching phonemes from Datamuse for {len(missing)} words...")
        for w in missing:
            phonemes = _fetch_from_api(w)
            if phonemes is None:
                print(f"  WARNING: {w!r} not found in Datamuse")
            else:
                cache[w] = phonemes
        _save_cache(cache)
        print(f"  Cached {len(missing)} new entries ({len(cache)} total)")
    else:
        print(f"All {len(words)} words found in cache")

    return cache
