"""
Canonical phoneme reference based on the Letterland 44-phoneme system.

This module is the single source of truth for:
- All 44 English phonemes with IPA, TTS pronunciation, and spelling variants
- Consonant digraphs (multi-letter graphemes that must not be split in breakdowns)
- Individual consonant sound TTS pronunciations
- Example words per spelling variant

Used by extract_decoding_data.py and validate_data.py.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Consonant digraphs — multi-letter graphemes representing ONE sound.
# These must NEVER be split in decoding breakdowns.
# ---------------------------------------------------------------------------

DIGRAPHS: set[str] = {
    # Core digraphs children encounter
    "ch", "sh", "th", "wh", "ng", "nk", "ck",
    # Less common but standard
    "ph", "gh", "wr", "kn", "mb", "mn", "tch", "dg",
    # Double consonants (single sound)
    "bb", "dd", "ff", "gg", "ll", "mm", "nn", "pp", "rr", "ss", "tt", "zz",
    # Suffixes kept as single breakdown elements
    "ed", "ing",
}

# ---------------------------------------------------------------------------
# Individual consonant letter → TTS pronunciation
# Used for single-letter consonant elements in breakdowns.
# ---------------------------------------------------------------------------

CONSONANT_TTS: dict[str, str] = {
    "b": "buh",
    "c": "kuh",
    "d": "duh",
    "f": "fff",
    "g": "guh",
    "h": "huh",
    "j": "juh",
    "k": "kuh",
    "l": "lll",
    "m": "mmm",
    "n": "nnn",
    "p": "puh",
    "q": "kwuh",
    "r": "rrr",
    "s": "sss",
    "t": "tuh",
    "v": "vvv",
    "w": "wuh",
    "x": "ks",
    "y": "yuh",
    "z": "zzz",
}

# Digraph → TTS pronunciation (for digraph elements in breakdowns)
DIGRAPH_TTS: dict[str, str] = {
    "ch": "chuh",
    "sh": "shh",
    "th": "thh",
    "wh": "whuh",
    "ng": "ng",
    "nk": "nk",
    "ck": "kuh",
    "ph": "fff",
    "gh": "fff",
    "wr": "rrr",
    "kn": "nnn",
    "tch": "chuh",
    "dg": "juh",
    # Suffix elements — context-dependent, handled by get_suffix_ed_tts / get_suffix_s_tts
    "ing": "ing",
}

# ---------------------------------------------------------------------------
# Voiced / voiceless consonant classification
# Used to determine suffix pronunciation (-ed, -s)
# ---------------------------------------------------------------------------

# Voiceless consonant sounds: the -ed suffix is /t/ after these, -s is /s/
VOICELESS_SOUNDS: set[str] = {
    "p", "t", "k", "f", "s", "ch", "sh", "th",  # unvoiced th (θ)
    "pp", "tt", "ck", "ff", "ss", "tch", "ph", "gh",
}

# All other consonants and all vowels are voiced.
# The -ed suffix is /d/ after voiced sounds, -s is /z/.
# Special case: -ed is /ɪd/ after /t/ or /d/ sounds.

# Elements that represent a /t/ or /d/ sound (for -ed → /ɪd/ rule)
TD_SOUNDS: set[str] = {"t", "d", "tt", "dd"}

# ---------------------------------------------------------------------------
# 44 Phonemes — the Letterland spine
#
# Each phoneme dict has:
#   id        — stable identifier (used in JSON, types, settings keys)
#   ipa       — IPA representation
#   category  — "consonant" or "vowel"
#   tts       — TTS-friendly pronunciation of the sound in isolation
#   spellings — ordered list of graphemes (most common first)
#   examples  — dict mapping grapheme → [example words]
#   source    — "teacher" if covered by teacher emails, else "reference"
# ---------------------------------------------------------------------------

PHONEMES: list[dict] = [
    # ===== CONSONANTS =====
    {
        "id": "b",
        "ipa": "/b/",
        "category": "consonant",
        "tts": "buh",
        "spellings": ["b", "bb"],
        "examples": {"b": ["bat", "boy"], "bb": ["hobby"]},
        "source": "reference",
    },
    {
        "id": "k",
        "ipa": "/k/",
        "category": "consonant",
        "tts": "kuh",
        "spellings": ["c", "k", "ck", "ch", "qu", "cc", "lk", "x"],
        "examples": {"c": ["cat", "cool"], "k": ["kit", "kick"], "ck": ["duck"], "ch": ["school"], "qu": ["unique"], "cc": ["accent"], "lk": ["folk"], "x": ["box"]},
        "source": "reference",
    },
    {
        "id": "d",
        "ipa": "/d/",
        "category": "consonant",
        "tts": "duh",
        "spellings": ["d", "dd", "ed"],
        "examples": {"d": ["dog", "day"], "dd": ["muddy"], "ed": ["smiled"]},
        "source": "reference",
    },
    {
        "id": "f",
        "ipa": "/f/",
        "category": "consonant",
        "tts": "fff",
        "spellings": ["f", "ff", "ph", "gh", "lf", "ft"],
        "examples": {"f": ["fan", "food"], "ff": ["puff"], "ph": ["photo"], "gh": ["rough"], "lf": ["half"], "ft": ["often"]},
        "source": "reference",
    },
    {
        "id": "g",
        "ipa": "/g/",
        "category": "consonant",
        "tts": "guh",
        "spellings": ["g", "gg", "gh", "gu", "gue"],
        "examples": {"g": ["go", "good"], "gg": ["egg"], "gh": ["ghost"], "gu": ["guest"], "gue": ["prologue"]},
        "source": "reference",
    },
    {
        "id": "h",
        "ipa": "/h/",
        "category": "consonant",
        "tts": "huh",
        "spellings": ["h", "wh"],
        "examples": {"h": ["hen", "hike"], "wh": ["who"]},
        "source": "reference",
    },
    {
        "id": "j",
        "ipa": "/dʒ/",
        "category": "consonant",
        "tts": "juh",
        "spellings": ["j", "g", "dg"],
        "examples": {"j": ["jet", "jar"], "g": ["giant"], "dg": ["edge"]},
        "source": "reference",
    },
    {
        "id": "l",
        "ipa": "/l/",
        "category": "consonant",
        "tts": "lll",
        "spellings": ["l", "ll", "le"],
        "examples": {"l": ["leg", "lake"], "ll": ["bell", "ball"], "le": ["table"]},
        "source": "reference",
    },
    {
        "id": "m",
        "ipa": "/m/",
        "category": "consonant",
        "tts": "mmm",
        "spellings": ["m", "mm", "mb", "mn", "lm"],
        "examples": {"m": ["map", "more"], "mm": ["summer"], "mb": ["thumb"], "mn": ["autumn"], "lm": ["palm"]},
        "source": "reference",
    },
    {
        "id": "n",
        "ipa": "/n/",
        "category": "consonant",
        "tts": "nnn",
        "spellings": ["n", "nn", "kn", "gn", "pn"],
        "examples": {"n": ["net", "rain"], "nn": ["tennis"], "kn": ["knee"], "gn": ["gnat"], "pn": ["pneumonic"]},
        "source": "reference",
    },
    {
        "id": "p",
        "ipa": "/p/",
        "category": "consonant",
        "tts": "puh",
        "spellings": ["p", "pp"],
        "examples": {"p": ["pen", "play"], "pp": ["happy"]},
        "source": "reference",
    },
    {
        "id": "r",
        "ipa": "/r/",
        "category": "consonant",
        "tts": "rrr",
        "spellings": ["r", "rr", "wr", "rh"],
        "examples": {"r": ["run", "rain"], "rr": ["carry"], "wr": ["write"], "rh": ["rhyme"]},
        "source": "reference",
    },
    {
        "id": "s",
        "ipa": "/s/",
        "category": "consonant",
        "tts": "sss",
        "spellings": ["s", "ss", "c", "sc", "ps", "ce", "se"],
        "examples": {"s": ["sun", "stars"], "ss": ["miss"], "c": ["cell"], "sc": ["scene"], "ps": ["psycho"], "ce": ["pace"], "se": ["course"]},
        "source": "reference",
    },
    {
        "id": "t",
        "ipa": "/t/",
        "category": "consonant",
        "tts": "tuh",
        "spellings": ["t", "tt", "ed"],
        "examples": {"t": ["tap", "train"], "tt": ["sitting"], "ed": ["hoped"]},
        "source": "reference",
    },
    {
        "id": "v",
        "ipa": "/v/",
        "category": "consonant",
        "tts": "vvv",
        "spellings": ["v", "ve"],
        "examples": {"v": ["van"], "ve": ["have"]},
        "source": "reference",
    },
    {
        "id": "w",
        "ipa": "/w/",
        "category": "consonant",
        "tts": "wuh",
        "spellings": ["w", "wh", "o"],
        "examples": {"w": ["wig", "wait"], "wh": ["when"], "o": ["one"]},
        "source": "reference",
    },
    {
        "id": "y_consonant",
        "ipa": "/j/",
        "category": "consonant",
        "tts": "yuh",
        "spellings": ["y"],
        "examples": {"y": ["yes", "yay"]},
        "source": "reference",
    },
    {
        "id": "z",
        "ipa": "/z/",
        "category": "consonant",
        "tts": "zzz",
        "spellings": ["z", "zz", "s", "ss", "x", "ze", "se"],
        "examples": {"z": ["zip"], "zz": ["buzz"], "s": ["is"], "ss": ["scissors"], "x": ["xylophone"], "ze": ["craze"], "se": ["cause"]},
        "source": "reference",
    },
    {
        "id": "ch",
        "ipa": "/tʃ/",
        "category": "consonant",
        "tts": "chuh",
        "spellings": ["ch", "tch", "tu", "te"],
        "examples": {"ch": ["chip", "chirp"], "tch": ["catch"], "tu": ["future"], "te": ["righteous"]},
        "source": "reference",
    },
    {
        "id": "ng",
        "ipa": "/ŋ/",
        "category": "consonant",
        "tts": "ng",
        "spellings": ["ng", "nk"],
        "examples": {"ng": ["ring"], "nk": ["pink"]},
        "source": "reference",
    },
    {
        "id": "sh",
        "ipa": "/ʃ/",
        "category": "consonant",
        "tts": "shh",
        "spellings": ["sh", "t", "ce", "ci", "si", "sci", "ti"],
        "examples": {"sh": ["shop", "shade"], "t": ["attention"], "ce": ["ocean"], "ci": ["special"], "si": ["pension"], "sci": ["conscience"], "ti": ["station"]},
        "source": "reference",
    },
    {
        "id": "th_voiced",
        "ipa": "/ð/",
        "category": "consonant",
        "tts": "thh",
        "spellings": ["th"],
        "examples": {"th": ["then", "the"]},
        "source": "reference",
    },
    {
        "id": "th_unvoiced",
        "ipa": "/θ/",
        "category": "consonant",
        "tts": "thh",
        "spellings": ["th"],
        "examples": {"th": ["thin", "third"]},
        "source": "reference",
    },
    {
        "id": "zh",
        "ipa": "/ʒ/",
        "category": "consonant",
        "tts": "zhuh",
        "spellings": ["s", "si", "z"],
        "examples": {"s": ["treasure"], "si": ["division"], "z": ["azure"]},
        "source": "reference",
    },

    # ===== VOWELS =====
    {
        "id": "short_a",
        "ipa": "/æ/",
        "category": "vowel",
        "tts": "ah",
        "spellings": ["a"],
        "examples": {"a": ["ant", "bat", "cat"]},
        "source": "reference",
    },
    {
        "id": "long_a",
        "ipa": "/eɪ/",
        "category": "vowel",
        "tts": "ay",
        "spellings": ["ai", "ay", "a_e", "ei", "a", "ey"],
        "examples": {
            "ai": ["rain", "paint", "hail", "snail", "train", "wait"],
            "ay": ["say", "play", "day", "gray", "stay", "ray", "yay"],
            "a_e": ["make", "lake", "came", "cave", "gate", "same", "shade", "snake", "take", "wake"],
            "ei": ["eight"],
            "a": ["apron"],
            "ey": ["they"],
        },
        "source": "teacher",
    },
    {
        "id": "air",
        "ipa": "/ɛər/",
        "category": "vowel",
        "tts": "air",
        "spellings": ["air", "are", "ear", "ere"],
        "examples": {"air": ["fair"], "are": ["scare"], "ear": ["bear"], "ere": ["there"]},
        "source": "reference",
    },
    {
        "id": "ar",
        "ipa": "/ɑr/",
        "category": "vowel",
        "tts": "ar",
        "spellings": ["ar", "a", "are"],
        "examples": {
            "ar": ["farm", "car", "art", "dark", "darted", "hard", "jar", "part", "smart", "stars", "starting", "tar"],
            "a": ["father"],
            "are": ["are"],
        },
        "source": "teacher",
    },
    {
        "id": "short_e",
        "ipa": "/ɛ/",
        "category": "vowel",
        "tts": "eh",
        "spellings": ["e", "ea", "ai", "ay"],
        "examples": {"e": ["egg", "red"], "ea": ["head", "read"], "ai": ["said"], "ay": ["says"]},
        "source": "reference",
    },
    {
        "id": "ear",
        "ipa": "/ɪər/",
        "category": "vowel",
        "tts": "ear",
        "spellings": ["ear", "eer", "ere"],
        "examples": {"ear": ["year", "dear", "clear"], "eer": ["deer", "cheers"], "ere": ["here"]},
        "source": "reference",
    },
    {
        "id": "long_e",
        "ipa": "/iː/",
        "category": "vowel",
        "tts": "ee",
        "spellings": ["ee", "ea", "e", "ie", "e_e"],
        "examples": {
            "ee": ["bee", "tree", "green", "sweet", "street", "feeds", "beets"],
            "ea": ["sea", "eat", "eats", "beans", "means", "peas", "treats"],
            "e": ["he"],
            "ie": ["believe"],
            "e_e": ["these"],
        },
        "source": "teacher",
    },
    {
        "id": "short_i",
        "ipa": "/ɪ/",
        "category": "vowel",
        "tts": "ih",
        "spellings": ["i", "y", "i_e"],
        "examples": {"i": ["it", "big"], "y": ["gymnast"], "i_e": ["engine"]},
        "source": "reference",
    },
    {
        "id": "long_i",
        "ipa": "/aɪ/",
        "category": "vowel",
        "tts": "eye",
        "spellings": ["igh", "ie", "y", "i_e", "i", "ei"],
        "examples": {
            "igh": ["night"],
            "ie": ["tie"],
            "y": ["my"],
            "i_e": ["like", "kite", "bite", "drive", "five", "hike", "pile", "side", "slide", "smile", "time", "while"],
            "i": ["ice"],
            "ei": ["height"],
        },
        "source": "teacher",
    },
    {
        "id": "short_o",
        "ipa": "/ɒ/",
        "category": "vowel",
        "tts": "oh",
        "spellings": ["o"],
        "examples": {"o": ["odd", "hot"]},
        "source": "reference",
    },
    {
        "id": "long_o",
        "ipa": "/oʊ/",
        "category": "vowel",
        "tts": "oh",
        "spellings": ["oa", "ow", "o", "o_e"],
        "examples": {
            "oa": ["boat", "coals", "roar", "roast", "roasted", "toast", "toasted"],
            "ow": ["snow", "blow", "glow", "grown", "low"],
            "o": ["so"],
            "o_e": ["home", "hole"],
        },
        "source": "teacher",
    },
    {
        "id": "oi",
        "ipa": "/ɔɪ/",
        "category": "vowel",
        "tts": "oy",
        "spellings": ["oi", "oy"],
        "examples": {"oi": ["coin"], "oy": ["boy"]},
        "source": "reference",
    },
    {
        "id": "long_oo",
        "ipa": "/uː/",
        "category": "vowel",
        "tts": "oo",
        "spellings": ["oo", "ew", "ue", "u_e", "o", "ui"],
        "examples": {
            "oo": ["moon", "food", "cook", "cooked", "cooking", "cool", "cools", "good", "soon", "tools", "wood", "ooze"],
            "ew": ["grew", "crew", "stew"],
            "ue": ["blue"],
            "u_e": ["rule", "cube", "flute"],
            "o": ["to"],
            "ui": ["fruit"],
        },
        "source": "teacher",
    },
    {
        "id": "short_oo",
        "ipa": "/ʊ/",
        "category": "vowel",
        "tts": "uh",
        "spellings": ["oo", "u"],
        "examples": {"oo": ["look", "book"], "u": ["put"]},
        "source": "reference",
    },
    {
        "id": "or",
        "ipa": "/ɔr/",
        "category": "vowel",
        "tts": "or",
        "spellings": ["or", "aw", "au", "ore", "oor", "our"],
        "examples": {
            "or": ["for", "fork", "cork", "form", "formed", "more", "stored"],
            "aw": ["saw"],
            "au": ["cause"],
            "ore": ["more"],
            "oor": ["door"],
            "our": ["four"],
        },
        "source": "teacher",
    },
    {
        "id": "ow",
        "ipa": "/aʊ/",
        "category": "vowel",
        "tts": "ow",
        "spellings": ["ow", "ou"],
        "examples": {
            "ow": ["cow", "brown", "chow", "down"],
            "ou": ["out"],
        },
        "source": "teacher",
    },
    {
        "id": "short_u",
        "ipa": "/ʌ/",
        "category": "vowel",
        "tts": "uh",
        "spellings": ["u", "o"],
        "examples": {"u": ["up", "bus"], "o": ["son"]},
        "source": "reference",
    },
    {
        "id": "ur",
        "ipa": "/ɜr/",
        "category": "vowel",
        "tts": "er",
        "spellings": ["ur", "er", "ir", "ear"],
        "examples": {
            "ur": ["fur", "turn"],
            "er": ["her", "fern", "perch"],
            "ir": ["girl", "bird", "birds", "chirp", "chirped", "first", "girls", "third"],
            "ear": ["learn"],
        },
        "source": "teacher",
    },
    {
        "id": "ure",
        "ipa": "/jʊər/",
        "category": "vowel",
        "tts": "yoor",
        "spellings": ["ure"],
        "examples": {"ure": ["pure"]},
        "source": "reference",
    },
    {
        "id": "schwa",
        "ipa": "/ə/",
        "category": "vowel",
        "tts": "uh",
        "spellings": ["a"],
        "examples": {"a": ["parachute"]},
        "source": "reference",
    },
    # ===== COMPOSITE PATTERNS (teacher-specific groupings) =====
    {
        "id": "all",
        "ipa": "/ɔːl/",
        "category": "vowel",
        "tts": "awl",
        "spellings": ["all"],
        "examples": {
            "all": ["tall", "ball", "ballpark", "baseball", "basketball", "called", "dodgeball", "kickball", "small"],
        },
        "source": "teacher",
    },
]

# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------

# phoneme id → phoneme dict
PHONEME_BY_ID: dict[str, dict] = {p["id"]: p for p in PHONEMES}

# grapheme → phoneme id (first match wins for ambiguous graphemes like "oo")
# We build this with teacher-sourced phonemes taking priority.
_teacher_first = sorted(PHONEMES, key=lambda p: (0 if p["source"] == "teacher" else 1))
GRAPHEME_TO_PHONEME: dict[str, str] = {}
for _p in _teacher_first:
    for _g in _p["spellings"]:
        if _g not in GRAPHEME_TO_PHONEME:
            GRAPHEME_TO_PHONEME[_g] = _p["id"]

# All graphemes that are vowel-sound patterns (used by breakdown generation)
VOWEL_GRAPHEMES: set[str] = set()
for _p in PHONEMES:
    if _p["category"] == "vowel":
        for _g in _p["spellings"]:
            VOWEL_GRAPHEMES.add(_g)

# Words where 'ow' is /aʊ/ (ow phoneme) not /oʊ/ (long_o phoneme)
OW_AS_OW: set[str] = {
    "brown", "chow", "cow", "down", "how", "now", "town",
    "wow", "plow", "crowd", "frown", "growl", "owl",
    "brow", "clown", "drown", "gown", "prow", "prowl",
    "scowl", "shower", "tower", "towel", "vowel", "power",
}


def get_element_tts(
    element: str, active_graphemes: list[str], word: str,
    preceding_element: str | None = None,
) -> str:
    """Get TTS pronunciation for one breakdown element.

    Args:
        element: The breakdown element (e.g., 'b', 'ai', 'a_e', 'ch', 'ed')
        active_graphemes: The graphemes of the active spelling unit for this word
        word: The full word (needed for ambiguous cases like 'ow')
        preceding_element: The previous breakdown element (needed for suffix TTS)
    """
    # Suffix: -ed (context-dependent pronunciation)
    if element == "ed" and preceding_element is not None:
        return get_suffix_ed_tts(preceding_element)

    # Suffix: -s (context-dependent pronunciation)
    if element == "s" and preceding_element is not None and word.endswith("s"):
        return get_suffix_s_tts(preceding_element)

    # Suffix: -ing
    if element == "ing":
        return "ing"

    # Split digraph notation (a_e, i_e, etc.)
    if "_" in element:
        phoneme_id = GRAPHEME_TO_PHONEME.get(element)
        if phoneme_id:
            return PHONEME_BY_ID[phoneme_id]["tts"]
        return element.replace("_", "")

    # Vowel grapheme that's part of the active pattern
    if element in active_graphemes and element in VOWEL_GRAPHEMES:
        # Handle ambiguous 'ow'
        if element == "ow":
            if word in OW_AS_OW:
                return PHONEME_BY_ID["ow"]["tts"]  # "ow" (/aʊ/)
            else:
                return PHONEME_BY_ID["long_o"]["tts"]  # "oh" (/oʊ/)
        # Handle ambiguous 'oo'
        if element == "oo":
            # Most book words use long oo; short_oo words are "look", "book", "put" etc.
            short_oo_words = {"look", "book", "cook", "good", "wood", "hood", "foot", "stood", "took", "shook"}
            if word in short_oo_words:
                return PHONEME_BY_ID["short_oo"]["tts"]
            return PHONEME_BY_ID["long_oo"]["tts"]
        phoneme_id = GRAPHEME_TO_PHONEME.get(element)
        if phoneme_id:
            return PHONEME_BY_ID[phoneme_id]["tts"]

    # Consonant digraph
    if element in DIGRAPH_TTS:
        return DIGRAPH_TTS[element]

    # Single consonant letter
    if element in CONSONANT_TTS:
        return CONSONANT_TTS[element]

    # Longer element (suffix like "park") — TTS handles as-is
    return element


def get_suffix_ed_tts(preceding_element: str) -> str:
    """Get TTS pronunciation for the -ed suffix based on the preceding sound.

    Rules:
    - After /t/ or /d/ → /ɪd/ (added syllable): darted, roasted
    - After voiceless consonant → /t/: chirped, cooked
    - After voiced consonant or vowel → /d/: called, formed, stored
    """
    if preceding_element in TD_SOUNDS:
        return "id"
    if preceding_element in VOICELESS_SOUNDS:
        return "tuh"
    return "duh"


def get_suffix_s_tts(preceding_element: str) -> str:
    """Get TTS pronunciation for the -s suffix based on the preceding sound.

    Rules:
    - After voiceless consonant → /s/: treats, beets
    - After voiced consonant or vowel → /z/: beans, nails, birds
    """
    if preceding_element in VOICELESS_SOUNDS:
        return "sss"
    return "zzz"


# ---------------------------------------------------------------------------
# ARPAbet → audio file manifest
#
# Maps each CMU ARPAbet phoneme (stress markers stripped) to:
#   audio_id — filename stem for the audio file (public/audio/phonemes/{audio_id}.mp3)
#   ipa      — IPA transcription for Google Cloud TTS SSML generation
#
# The audio_id values reuse existing filenames where the sound matches.
# For consonants that need a brief schwa to sound natural in isolation,
# the IPA includes a trailing schwa (ə).
# ---------------------------------------------------------------------------

ARPABET_TO_AUDIO: dict[str, dict[str, str]] = {
    # --- Stops ---
    "B":  {"audio_id": "buh",  "ipa": "bə"},
    "D":  {"audio_id": "duh",  "ipa": "də"},
    "G":  {"audio_id": "guh",  "ipa": "gə"},
    "K":  {"audio_id": "kuh",  "ipa": "kə"},
    "P":  {"audio_id": "puh",  "ipa": "pə"},
    "T":  {"audio_id": "tuh",  "ipa": "tə"},
    # --- Affricates ---
    "CH": {"audio_id": "chuh", "ipa": "tʃə"},
    "JH": {"audio_id": "juh",  "ipa": "dʒə"},
    # --- Fricatives ---
    "DH": {"audio_id": "thh",  "ipa": "ð"},
    "F":  {"audio_id": "fff",  "ipa": "f"},
    "HH": {"audio_id": "huh",  "ipa": "hə"},
    "S":  {"audio_id": "sss",  "ipa": "s"},
    "SH": {"audio_id": "shh",  "ipa": "ʃ"},
    "TH": {"audio_id": "thh",  "ipa": "θ"},
    "V":  {"audio_id": "vvv",  "ipa": "v"},
    "Z":  {"audio_id": "zzz",  "ipa": "z"},
    "ZH": {"audio_id": "zhuh", "ipa": "ʒə"},
    # --- Nasals ---
    "M":  {"audio_id": "mmm",  "ipa": "m"},
    "N":  {"audio_id": "nnn",  "ipa": "n"},
    "NG": {"audio_id": "ng",   "ipa": "ŋ"},
    # --- Liquids ---
    "L":  {"audio_id": "lll",  "ipa": "l"},
    "R":  {"audio_id": "rrr",  "ipa": "ɹ"},
    # --- Semivowels / Glides ---
    "W":  {"audio_id": "wuh",  "ipa": "wə"},
    "Y":  {"audio_id": "yuh",  "ipa": "jə"},
    # --- Vowels (monophthongs) ---
    "AA": {"audio_id": "ah",   "ipa": "ɑ"},     # "odd", "father"
    "AE": {"audio_id": "aah",  "ipa": "æ"},     # "at", "bat"
    "AH": {"audio_id": "uh",   "ipa": "ə"},     # "hut" (stressed ʌ) or schwa (unstressed)
    "AO": {"audio_id": "aw",   "ipa": "ɔ"},     # "ought", "all", "ball"
    "EH": {"audio_id": "eh",   "ipa": "ɛ"},     # "ed", "red"
    "ER": {"audio_id": "er",   "ipa": "ɝ"},     # "hurt", "her" (r-colored vowel)
    "IH": {"audio_id": "ih",   "ipa": "ɪ"},     # "it", "big"
    "IY": {"audio_id": "ee",   "ipa": "iː"},    # "eat", "bee"
    "UH": {"audio_id": "ooh",  "ipa": "ʊ"},     # "hood", "book"
    "UW": {"audio_id": "oo",   "ipa": "uː"},    # "two", "moon"
    # --- Diphthongs ---
    "AW": {"audio_id": "ow",   "ipa": "aʊ"},    # "now", "cow"
    "AY": {"audio_id": "eye",  "ipa": "aɪ"},    # "hide", "my"
    "EY": {"audio_id": "ay",   "ipa": "eɪ"},    # "ate", "day"
    "OW": {"audio_id": "oh",   "ipa": "oʊ"},    # "oat", "show"
    "OY": {"audio_id": "oy",   "ipa": "ɔɪ"},    # "toy", "boy"
}

# Collect all valid audio IDs from the manifest + multi-phoneme graphemes
VALID_AUDIO_IDS: set[str] = (
    {v["audio_id"] for v in ARPABET_TO_AUDIO.values()}
    | {"ar", "or", "ear", "air", "awl", "id", "ing"}
)
