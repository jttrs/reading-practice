"""
Extract decoding practice data from teacher email PDFs and reading group book PDFs.

Outputs src/data/decoding-words.json with:
- spellingUnits: spelling sound patterns with phonemes and examples
- decodingWords: words from books matched to spelling patterns with breakdowns
- sightWords: high-frequency sight words from teacher emails

Usage:
    uv run python scripts/extract_decoding_data.py
"""

import json
import os
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path

import fitz  # PyMuPDF

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MATERIALS_DIR = Path("materials/decoding")
EMAILS_DIR = MATERIALS_DIR / "sophie-emails"
BOOKS_DIR = MATERIALS_DIR / "reading-group-books"
OUTPUT_PATH = Path("src/data/decoding-words.json")

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class SpellingUnit:
    id: str
    patterns: list[str]
    phoneme: str
    examples: list[str]
    source_email: str  # date string
    book: str


@dataclass
class DecodingWord:
    word: str
    spelling_unit_id: str
    decoding_breakdown: list[str]
    book: str


@dataclass
class SightWord:
    word: str
    source_email: str
    book: str


@dataclass
class EmailData:
    date: str
    book_titles: list[str]
    spelling_patterns: list[dict]  # [{patterns, phoneme, examples}]
    sight_words: list[str]


# ---------------------------------------------------------------------------
# Source Parsers Registry
# ---------------------------------------------------------------------------

SOURCE_PARSERS: dict[str, callable] = {}


def register_parser(name: str):
    """Decorator to register a source parser."""
    def decorator(func):
        SOURCE_PARSERS[name] = func
        return func
    return decorator


# ---------------------------------------------------------------------------
# PDF Text Extraction
# ---------------------------------------------------------------------------


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract all text from a PDF file."""
    doc = fitz.open(str(pdf_path))
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


# ---------------------------------------------------------------------------
# Email Parser
# ---------------------------------------------------------------------------


def _parse_date_from_filename(filename: str) -> str:
    """Extract date from email filename like 'Gmail - Reading group 3 update - 2026-03-13.pdf'."""
    match = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
    if match:
        return match.group(1)
    # Try pattern without hyphens before date
    match = re.search(r"(\d{4}-\d{2}-\d{2})", filename.replace(" ", ""))
    return match.group(1) if match else "unknown"


def _extract_book_titles(text: str) -> list[str]:
    """Extract book titles from email text."""
    titles = []

    # Pattern: "we are reading "Title"" or "we read a book called "Title""
    reading_patterns = [
        r'(?:reading|read[^i].*?called)\s+"([^"]+)"',
        r'(?:reading|read[^i].*?called)\s+["\u201c]([^"\u201d]+)["\u201d]',
    ]
    for pat in reading_patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            titles.append(m.group(1).strip())

    # Pattern: quoted title at start of content section (like "Fun fort")
    quote_patterns = [
        r'["\u201c]([A-Z][^"\u201d]{3,50})["\u201d]\s+by\s+',
        r'["\u201c]([A-Z][^"\u201d]{3,50})["\u201d]\s*\n',
    ]
    for pat in quote_patterns:
        for m in re.finditer(pat, text):
            title = m.group(1).strip()
            if title not in titles:
                titles.append(title)

    return titles


def _extract_spelling_patterns(text: str) -> list[dict]:
    """Extract spelling sound patterns, phonemes, and examples from email text."""
    results = []

    # Find the spelling sound section — must start at beginning of line
    # to avoid matching mid-sentence references like "focus on spelling sounds,"
    spelling_section_match = re.search(
        r"^[Ss]pelling [Ss]ound[s]?\s*(?:focus|for this week)?[:\s]*\n(.*?)(?=^[Ss]ight [Ww]ord|^[Hh]igh.[Ff]requency|^[Nn]o sight|^[Tt]hank|^[Ll]et me know)",
        text,
        re.DOTALL | re.IGNORECASE | re.MULTILINE,
    )
    if not spelling_section_match:
        # Fallback: colon followed by content on same line (single-line format)
        spelling_section_match = re.search(
            r"[Ss]pelling [Ss]ound[s]?\s*(?:focus|for this week)?\s*:\s*(.+?)$",
            text,
            re.IGNORECASE | re.MULTILINE,
        )
    if not spelling_section_match:
        return results

    section = spelling_section_match.group(1).strip()

    # Check for "No spelling sound" or "none"
    if re.search(r"no spelling sound", section, re.IGNORECASE):
        return results
    if re.match(r"\s*none\s*$", section, re.IGNORECASE):
        return results

    # Pattern: "a_e /a/ → lake" or "ai,ay /a/" or "Er, ir, ur / ur/"
    # Also: "Ea – eat" / "Ee - tree" / "all -/awl/"
    # General approach: find groups of patterns and their phonemes

    # Extract any "Example:" lines first, then remove them from section
    extra_examples = []
    example_match = re.search(r"[Ee]xample[s]?:\s*(.+?)$", section, re.MULTILINE)
    if example_match:
        ex_text = example_match.group(1)
        for part in re.split(r"[/,]", ex_text):
            part = re.sub(r"[a-z_]+\s*:", "", part, flags=re.IGNORECASE).strip()
            part = part.strip(" -–")
            if part and part.isalpha() and part.lower() not in ("example", "examples"):
                extra_examples.append(part.lower())
        # Remove the Example line from section to avoid double-parsing
        section = re.sub(r"[Ee]xample[s]?:\s*.+?$", "", section, flags=re.MULTILINE).strip()

    # Try structured format: "pattern /phoneme/ → example"
    structured = re.findall(
        r"([a-z_]+(?:\s*,\s*[a-z_]+)*)\s*/([^/]+)/\s*(?:[→\-–:]\s*(\w+))?",
        section,
        re.IGNORECASE,
    )
    if structured:
        for patterns_str, phoneme, example in structured:
            patterns = [p.strip().lower() for p in re.split(r"[,\s]+", patterns_str) if p.strip()]
            examples = [example.lower()] if example else []
            if not examples and extra_examples:
                examples = extra_examples
            results.append({
                "patterns": patterns,
                "phoneme": f"/{phoneme.strip()}/",
                "examples": examples,
            })
        return results

    # Try format: "Ea – eat" on separate lines
    line_patterns = re.findall(
        r"([A-Za-z_]+(?:\s*,\s*[A-Za-z_]+)*)\s*[–\-:]\s*(?:/([^/]+)/)?\s*(\w+)?",
        section,
    )
    if line_patterns:
        for patterns_str, phoneme, example in line_patterns:
            patterns = [p.strip().lower() for p in re.split(r"[,\s]+", patterns_str) if p.strip()]
            # Filter out noise words
            patterns = [p for p in patterns if len(p) <= 4 and p.isalpha() or "_" in p]
            if not patterns:
                continue
            examples = [example.lower()] if example else []
            phoneme_str = f"/{phoneme.strip()}/" if phoneme else ""
            results.append({
                "patterns": patterns,
                "phoneme": phoneme_str,
                "examples": examples,
            })
        return results

    # Try comma-separated patterns without phonemes: "Oa, ow, oo, ew"
    comma_match = re.match(
        r"^([A-Za-z_]+(?:\s*,\s*[A-Za-z_]+)+)\s*$",
        section.strip(),
        re.MULTILINE,
    )
    if comma_match:
        patterns = [p.strip().lower() for p in comma_match.group(1).split(",")]
        results.append({
            "patterns": patterns,
            "phoneme": "",
            "examples": [],
        })
        return results

    # Try single pattern: "all -/awl/"
    single_match = re.match(
        r"^\s*([a-z_]+)\s*[-–]?\s*/([^/]+)/",
        section.strip(),
        re.IGNORECASE,
    )
    if single_match:
        results.append({
            "patterns": [single_match.group(1).lower()],
            "phoneme": f"/{single_match.group(2).strip()}/",
            "examples": [],
        })

    return results


def _extract_sight_words(text: str) -> list[str]:
    """Extract sight/high-frequency words from email text."""
    words = []

    # Find sight word or high-frequency word section
    section_match = re.search(
        r"(?:[Ss]ight [Ww]ord|[Hh]igh.[Ff]requency [Ww]ord)s?\s*(?:for this week)?[:\s]*\n?(.*?)(?:[Tt]hank|[Bb]est|[Ll]et me know|\Z)",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if not section_match:
        return words

    section = section_match.group(1).strip()

    # Check for "No sight words"
    if re.search(r"no sight word", section, re.IGNORECASE):
        return words

    # Extract numbered or listed words: "1. every" or just "every"
    for line in section.split("\n"):
        line = line.strip()
        if not line:
            continue
        # Remove numbering
        cleaned = re.sub(r"^\d+[.)]\s*", "", line).strip()
        # Remove quotes and other punctuation
        cleaned = cleaned.strip("\"'\u201c\u201d.,;:")
        if cleaned and len(cleaned) < 200:
            # May be comma-separated: "give, live, ever, never"
            if "," in cleaned:
                for w in cleaned.split(","):
                    w = w.strip().lower()
                    if w and w.isalpha():
                        words.append(w)
            else:
                w = cleaned.lower().strip()
                if w and all(c.isalpha() or c == "'" for c in w):
                    words.append(w)

    return words


def _find_example_words_in_section(text: str) -> list[str]:
    """Find example words mentioned alongside spelling patterns."""
    examples = []
    # Pattern: "Example: word1 / word2" or "example: ar: car / or: fork"
    ex_match = re.search(r"[Ee]xample[s]?:\s*(.+?)(?:\n|$)", text)
    if ex_match:
        ex_text = ex_match.group(1)
        # Extract words, skip pattern labels like "ar:"
        for part in re.split(r"[/,]", ex_text):
            part = re.sub(r"[a-z_]+\s*:", "", part, flags=re.IGNORECASE).strip()
            if part and part.isalpha():
                examples.append(part.lower())
    return examples


@register_parser("sophie-emails")
def parse_emails(emails_dir: Path) -> list[EmailData]:
    """Parse all teacher email PDFs."""
    results = []
    if not emails_dir.exists():
        return results

    for pdf_file in sorted(emails_dir.glob("*.pdf")):
        text = extract_pdf_text(pdf_file)
        date = _parse_date_from_filename(pdf_file.name)
        book_titles = _extract_book_titles(text)
        spelling_patterns = _extract_spelling_patterns(text)
        sight_words = _extract_sight_words(text)

        # Try to pick up example words from the broader text if not in structured parse
        if spelling_patterns:
            extra_examples = _find_example_words_in_section(text)
            for sp in spelling_patterns:
                if not sp["examples"] and extra_examples:
                    sp["examples"] = extra_examples

        results.append(EmailData(
            date=date,
            book_titles=book_titles,
            spelling_patterns=spelling_patterns,
            sight_words=sight_words,
        ))

    return results


# ---------------------------------------------------------------------------
# Book Parser
# ---------------------------------------------------------------------------


def _extract_story_words(pdf_path: Path) -> set[str]:
    """Extract unique story words from a book PDF, filtering out boilerplate."""
    text = extract_pdf_text(pdf_path)
    # Remove copyright/publication boilerplate
    lines = text.split("\n")
    story_lines = []
    for line in lines:
        line_stripped = line.strip()
        # Skip copyright, ISBN, publisher info, page numbers
        if any(skip in line_stripped.lower() for skip in [
            "copyright", "isbn", "collaborative classroom",
            "collaborativeclassroom",
            "all rights reserved", "published", "978-",
            "permission", "publishing", "center for the",
            "illustrated by", "corinn kintz", "amy bauman",
            "amy helfer", "lucy bledsoe", "erica j",
            "rob arego", "margaret goldberg",
        ]):
            continue
        # Skip standalone numbers (page numbers)
        if re.match(r"^\d+$", line_stripped):
            continue
        # Skip very short lines that are likely headers
        if len(line_stripped) < 2:
            continue
        story_lines.append(line_stripped)

    story_text = " ".join(story_lines)

    # Tokenize: extract words, lowercase, remove punctuation
    words = re.findall(r"[a-zA-Z']+", story_text)
    # Normalize: lowercase, strip leading/trailing apostrophes
    unique_words = set()
    for w in words:
        w = w.lower().strip("'")
        if len(w) >= 2 and w.isalpha():
            unique_words.add(w)
        elif "'" in w:
            # Keep contractions like "don't"
            unique_words.add(w.lower())

    return unique_words


@register_parser("reading-group-books")
def parse_books(books_dir: Path) -> dict[str, set[str]]:
    """Parse all book PDFs. Returns {book_title: set_of_words}."""
    results = {}
    if not books_dir.exists():
        return results

    for pdf_file in sorted(books_dir.glob("*.pdf")):
        # Book title = filename without .pdf
        title = pdf_file.stem
        words = _extract_story_words(pdf_file)
        results[title] = words

    return results


# ---------------------------------------------------------------------------
# Cross-referencing: match book words to spelling patterns
# ---------------------------------------------------------------------------


def _match_book_to_email(book_title: str, emails: list[EmailData]) -> EmailData | None:
    """Find the email that references a given book title."""
    book_lower = book_title.lower().strip()
    for email in emails:
        for email_book in email.book_titles:
            # Fuzzy match: check if titles are similar
            email_lower = email_book.lower().strip()
            if book_lower == email_lower:
                return email
            # Partial match
            if book_lower in email_lower or email_lower in book_lower:
                return email
            # Handle variations like "Fun fort" vs "Fun Forts"
            if _normalize_title(book_lower) == _normalize_title(email_lower):
                return email
    return None


def _normalize_title(title: str) -> str:
    """Normalize a title for fuzzy matching."""
    # Remove trailing 's', convert to lowercase, strip punctuation
    title = title.lower().strip()
    title = re.sub(r"[^\w\s]", "", title)
    title = re.sub(r"\s+", " ", title)
    # Remove trailing 's' for plural matching
    if title.endswith("s") and not title.endswith("ss"):
        title = title[:-1]
    return title


def _generate_breakdown(word: str, pattern: str) -> list[str] | None:
    """
    Generate a decoding breakdown for a word based on a spelling pattern.

    For split digraphs like 'a_e': match "a...e" where the a and final e
    are separated by consonants.
    For regular patterns like 'ai', 'ee': find the pattern in the word.

    Returns list of breakdown elements or None if no match.
    """
    word_lower = word.lower()

    if "_" in pattern:
        # Split digraph: e.g., "a_e" means 'a' + consonants + 'e' at end
        parts = pattern.split("_")
        if len(parts) != 2:
            return None
        vowel, final = parts  # e.g., 'a', 'e'

        # The word should end with the final letter (or 's' after it)
        # and contain the vowel before some consonants before the final
        # Pattern: (prefix)(vowel)(consonants)(final_e)
        regex = re.compile(
            rf"^(.*?)({re.escape(vowel)})([^aeiou]+)({re.escape(final)})([s]?)$",
            re.IGNORECASE,
        )
        match = regex.match(word_lower)
        if not match:
            return None

        prefix, v, middle, e, suffix = match.groups()
        breakdown = []
        if prefix:
            breakdown.append(prefix)
        # The spelling unit is the vowel + middle + e shown as the pattern
        breakdown.append(f"{v}_{e}")
        if middle:
            # The consonants in between are separate elements
            # Actually, rethink: "lake" → l, a_e, k
            # prefix=l, v=a, middle=k, e=e
            # So breakdown should be: [prefix, pattern, middle]
            # Wait - the middle consonants are between vowel and final e
            breakdown = []
            if prefix:
                breakdown.append(prefix)
            breakdown.append(pattern)
            breakdown.append(middle)
            if suffix:
                breakdown.append(suffix)
        else:
            if suffix:
                breakdown.append(suffix)

        return breakdown if len(breakdown) > 1 else None

    else:
        # Regular pattern: find it in the word
        idx = word_lower.find(pattern.lower())
        if idx == -1:
            return None

        breakdown = []
        prefix = word_lower[:idx]
        suffix = word_lower[idx + len(pattern):]

        if prefix:
            breakdown.append(prefix)
        breakdown.append(pattern)
        if suffix:
            breakdown.append(suffix)

        return breakdown if breakdown else None


def _make_unit_id(patterns: list[str]) -> str:
    """Generate a stable ID from a list of spelling patterns."""
    return "_".join(sorted(p.replace("_", "") for p in patterns))


# Common words to exclude from decoding practice (too simple / not decodable)
EXCLUDE_WORDS = {
    "a", "i", "an", "am", "at", "as", "be", "by", "do", "go", "he", "if",
    "in", "is", "it", "me", "my", "no", "of", "on", "or", "so", "to", "up",
    "us", "we", "the", "and", "but", "for", "not", "you", "all", "can",
    "had", "her", "was", "one", "our", "out", "has", "his", "how", "its",
    "may", "new", "now", "old", "see", "way", "who", "did", "get", "got",
    "him", "let", "say", "she", "too", "use", "with", "have", "that",
    "this", "from", "they", "been", "said", "each", "than", "them",
    "then", "into", "just", "like", "make", "many", "some", "what",
    "when", "your", "come", "made", "here", "about", "could", "their",
    "there", "these", "would", "other", "which",
    "were", "where", "also", "very", "does", "says",
}


def cross_reference(
    emails: list[EmailData],
    books: dict[str, set[str]],
) -> tuple[list[SpellingUnit], list[DecodingWord], list[SightWord]]:
    """Cross-reference emails and books to produce final data."""
    spelling_units: list[SpellingUnit] = []
    decoding_words: list[DecodingWord] = []
    sight_words_out: list[SightWord] = []
    seen_decoding: set[str] = set()  # avoid duplicate words
    seen_sight: set[str] = set()

    for email in emails:
        if not email.spelling_patterns and not email.sight_words:
            continue

        # Build spelling units from this email
        for sp in email.spelling_patterns:
            unit_id = _make_unit_id(sp["patterns"])
            book_name = email.book_titles[0] if email.book_titles else ""

            unit = SpellingUnit(
                id=unit_id,
                patterns=sp["patterns"],
                phoneme=sp["phoneme"],
                examples=sp["examples"],
                source_email=email.date,
                book=book_name,
            )
            spelling_units.append(unit)

            # Find matching book and extract words
            for book_title in email.book_titles:
                book_words = None
                for bt, bw in books.items():
                    if _normalize_title(bt) == _normalize_title(book_title):
                        book_words = bw
                        book_title = bt  # use actual filename-based title
                        break
                if book_words is None:
                    continue

                for word in sorted(book_words):
                    if word in EXCLUDE_WORDS or word in seen_decoding:
                        continue
                    for pattern in sp["patterns"]:
                        breakdown = _generate_breakdown(word, pattern)
                        if breakdown:
                            decoding_words.append(DecodingWord(
                                word=word,
                                spelling_unit_id=unit_id,
                                decoding_breakdown=breakdown,
                                book=book_title,
                            ))
                            seen_decoding.add(word)
                            break

        # Collect sight words
        for sw in email.sight_words:
            sw_lower = sw.lower()
            if sw_lower not in seen_sight:
                book_name = email.book_titles[0] if email.book_titles else ""
                sight_words_out.append(SightWord(
                    word=sw_lower,
                    source_email=email.date,
                    book=book_name,
                ))
                seen_sight.add(sw_lower)

    return spelling_units, decoding_words, sight_words_out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    print("Extracting decoding data from materials...")

    # Parse emails
    print(f"  Parsing emails from {EMAILS_DIR}...")
    emails = parse_emails(EMAILS_DIR)
    print(f"    Found {len(emails)} emails")
    for e in emails:
        print(f"      {e.date}: {len(e.spelling_patterns)} spelling patterns, "
              f"{len(e.sight_words)} sight words, books: {e.book_titles}")

    # Parse books
    print(f"  Parsing books from {BOOKS_DIR}...")
    books = parse_books(BOOKS_DIR)
    print(f"    Found {len(books)} books")
    for title, words in books.items():
        print(f"      {title}: {len(words)} unique words")

    # Cross-reference
    print("  Cross-referencing...")
    spelling_units, decoding_words, sight_words = cross_reference(emails, books)
    print(f"    {len(spelling_units)} spelling units")
    print(f"    {len(decoding_words)} decoding words")
    print(f"    {len(sight_words)} sight words")

    # Build output
    output = {
        "spellingUnits": [
            {
                "id": u.id,
                "patterns": u.patterns,
                "phoneme": u.phoneme,
                "examples": u.examples,
                "sourceEmail": u.source_email,
                "book": u.book,
            }
            for u in spelling_units
        ],
        "decodingWords": [
            {
                "word": w.word,
                "spellingUnitId": w.spelling_unit_id,
                "decodingBreakdown": w.decoding_breakdown,
                "book": w.book,
            }
            for w in decoding_words
        ],
        "sightWords": [
            {
                "word": s.word,
                "sourceEmail": s.source_email,
                "book": s.book,
            }
            for s in sight_words
        ],
    }

    # Write output
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nOutput written to {OUTPUT_PATH}")
    print(f"  {len(output['spellingUnits'])} spelling units")
    print(f"  {len(output['decodingWords'])} decoding words")
    print(f"  {len(output['sightWords'])} sight words")


if __name__ == "__main__":
    main()
