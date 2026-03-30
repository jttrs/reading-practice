"""
Generate TTS audio files using Google Cloud Text-to-Speech API.

Reads src/data/decoding-words.json to collect all unique TTS values,
then generates MP3 audio files for:
- Phoneme sounds (breakdown elements) using SSML <phoneme> tags with IPA
- Whole words using plain text

Output:
  public/audio/phonemes/{tts_value}.mp3
  public/audio/words/{word}.mp3

Prerequisites:
  - Google Cloud project with Text-to-Speech API enabled
  - Application Default Credentials: `gcloud auth application-default login`
  - Python dependency: google-cloud-texttospeech

Usage:
    uv run python scripts/generate_audio.py
    uv run python scripts/generate_audio.py --force   # regenerate all files
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from google.cloud import texttospeech
from phoneme_data import PHONEMES, PHONEME_BY_ID

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATA_PATH = Path("src/data/decoding-words.json")
PHONEME_DIR = Path("public/audio/phonemes")
WORD_DIR = Path("public/audio/words")

# Voice selection — consistent voice for all audio
VOICE = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    name="en-US-Neural2-F",  # Female, high quality, free tier
)

AUDIO_CONFIG = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,
    speaking_rate=0.85,  # Slightly slower for clarity
)

# Slower rate for isolated phoneme sounds
PHONEME_AUDIO_CONFIG = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,
    speaking_rate=0.75,
)

# ---------------------------------------------------------------------------
# TTS value → IPA mapping for phoneme sounds
#
# Maps the TTS pronunciation strings used in breakdowns to their IPA
# transcription, so we can use SSML <phoneme> tags for accurate sound.
# ---------------------------------------------------------------------------

# Build mapping from phoneme data: tts_value → ipa
_TTS_TO_IPA: dict[str, str] = {}
for _p in PHONEMES:
    tts = _p["tts"]
    ipa = _p["ipa"].strip("/")  # Remove surrounding slashes
    if tts not in _TTS_TO_IPA:
        _TTS_TO_IPA[tts] = ipa

# Additional mappings for suffix and special TTS values
_TTS_TO_IPA.update({
    "id": "ɪd",       # -ed suffix after /t/ or /d/
    "ing": "ɪŋ",      # -ing suffix
    "nk": "ŋk",       # nk digraph
    "ng": "ŋ",        # ng digraph
    "ll": "l",         # doubled l
})

# Single vowel letters used in multi-syllable word breakdowns
# These are schwa-like reductions; use short vowel IPA
_VOWEL_LETTER_IPA: dict[str, str] = {
    "a": "ə",   # schwa (unstressed vowel in multi-syllable words)
    "e": "ə",
    "i": "ɪ",
    "o": "ɑ",
    "u": "ʌ",
}


def _get_phoneme_ssml(tts_value: str) -> str:
    """Build SSML input for a phoneme TTS value.

    Uses <phoneme> tag with IPA for accurate isolated sound pronunciation.
    Falls back to plain text if no IPA mapping exists.
    """
    ipa = _TTS_TO_IPA.get(tts_value) or _VOWEL_LETTER_IPA.get(tts_value)
    if ipa:
        # Use a carrier word approach: speak the IPA sound in isolation
        return (
            f'<speak>'
            f'<phoneme alphabet="ipa" ph="{ipa}">{tts_value}</phoneme>'
            f'</speak>'
        )
    # Fallback: just speak the text as-is
    return f"<speak>{tts_value}</speak>"


def _get_word_ssml(word: str) -> str:
    """Build SSML input for a whole word."""
    return f"<speak>{word}</speak>"


# ---------------------------------------------------------------------------
# Audio generation
# ---------------------------------------------------------------------------

def generate_audio(
    client: texttospeech.TextToSpeechClient,
    ssml: str,
    output_path: Path,
    audio_config: texttospeech.AudioConfig,
) -> None:
    """Generate a single audio file via the TTS API."""
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml)
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=VOICE,
        audio_config=audio_config,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(response.audio_content)


def main():
    parser = argparse.ArgumentParser(description="Generate TTS audio files")
    parser.add_argument(
        "--force", action="store_true",
        help="Regenerate all files even if they already exist",
    )
    args = parser.parse_args()

    # Load data
    with open(DATA_PATH) as f:
        data = json.load(f)

    # Collect unique TTS values
    phoneme_values: set[str] = set()
    word_values: set[str] = set()

    for w in data["decodingWords"]:
        for t in w["ttsBreakdown"]:
            phoneme_values.add(t)
        word_values.add(w["ttsWord"])

    for w in data["sightWords"]:
        word_values.add(w["ttsWord"])

    print(f"Audio to generate: {len(phoneme_values)} phoneme sounds, {len(word_values)} words")

    # Initialize client
    client = texttospeech.TextToSpeechClient()

    # Generate phoneme audio
    generated = 0
    skipped = 0

    print(f"\n--- Phoneme sounds ({len(phoneme_values)}) ---")
    for tts_val in sorted(phoneme_values):
        # Sanitize filename (replace special chars)
        filename = tts_val.replace("/", "_")
        output_path = PHONEME_DIR / f"{filename}.mp3"

        if output_path.exists() and not args.force:
            skipped += 1
            continue

        ssml = _get_phoneme_ssml(tts_val)
        try:
            generate_audio(client, ssml, output_path, PHONEME_AUDIO_CONFIG)
            generated += 1
            print(f"  ✓ {tts_val} → {output_path}")
        except Exception as e:
            print(f"  ✗ {tts_val}: {e}")

    # Generate word audio
    print(f"\n--- Whole words ({len(word_values)}) ---")
    for word in sorted(word_values):
        output_path = WORD_DIR / f"{word}.mp3"

        if output_path.exists() and not args.force:
            skipped += 1
            continue

        ssml = _get_word_ssml(word)
        try:
            generate_audio(client, ssml, output_path, AUDIO_CONFIG)
            generated += 1
            print(f"  ✓ {word} → {output_path}")
        except Exception as e:
            print(f"  ✗ {word}: {e}")

    print(f"\nDone: {generated} generated, {skipped} skipped (already exist)")
    print(f"  Phoneme dir: {PHONEME_DIR}")
    print(f"  Word dir:    {WORD_DIR}")


if __name__ == "__main__":
    main()
