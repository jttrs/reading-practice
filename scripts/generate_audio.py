"""
Generate TTS audio files using Google Cloud Text-to-Speech API.

Generates MP3 audio files for:
- All phoneme reference sounds (44-phoneme system) using SSML <phoneme> tags with IPA
- Breakdown elements from word data (suffixes, special sounds)
- Whole words using plain text

Skips files that already exist unless --force is used.

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
from phoneme_data import PHONEMES, PHONEME_BY_ID, ARPABET_TO_AUDIO

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
# Audio ID → IPA mapping for phoneme sounds
#
# Built from the ARPABET_TO_AUDIO manifest: audio_id → IPA.
# Multiple ARPAbet phonemes may share an audio_id (e.g., DH and TH → "thh").
# ---------------------------------------------------------------------------

_AUDIO_ID_TO_IPA: dict[str, str] = {}
for _entry in ARPABET_TO_AUDIO.values():
    aid = _entry["audio_id"]
    if aid not in _AUDIO_ID_TO_IPA:
        _AUDIO_ID_TO_IPA[aid] = _entry["ipa"]


def _get_phoneme_ssml(audio_id: str) -> str:
    """Build SSML input for a phoneme audio ID.

    Uses <phoneme> tag with IPA for accurate isolated sound pronunciation.
    Falls back to plain text if no IPA mapping exists.
    """
    ipa = _AUDIO_ID_TO_IPA.get(audio_id)
    if ipa:
        return (
            f'<speak>'
            f'<phoneme alphabet="ipa" ph="{ipa}">{audio_id}</phoneme>'
            f'</speak>'
        )
    # Fallback: just speak the text as-is
    return f"<speak>{audio_id}</speak>"


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

    # Include all audio IDs from the ARPAbet manifest
    for entry in ARPABET_TO_AUDIO.values():
        phoneme_values.add(entry["audio_id"])

    # Include TTS values from word breakdowns (should all be in manifest)
    for w in data["decodingWords"]:
        for t in w["ttsBreakdown"]:
            if t:  # skip empty strings (silent letters)
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
