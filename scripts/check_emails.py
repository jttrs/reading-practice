"""Check what data the emails actually provide - are the examples comprehensive word lists or just pattern examples?"""
import fitz
import os
import re
from pathlib import Path

EMAILS_DIR = Path("materials/decoding/sophie-emails")
BOOKS_DIR = Path("materials/decoding/reading-group-books")

for pdf_file in sorted(EMAILS_DIR.glob("*.pdf")):
    doc = fitz.open(str(pdf_file))
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    
    # Extract date
    date_m = re.search(r"(\d{4}-\d{2}-\d{2})", pdf_file.name)
    date = date_m.group(1) if date_m else "unknown"
    
    print(f"\n{'='*80}")
    print(f"EMAIL: {date}")
    print(f"{'='*80}")
    
    # Show just the spelling sound and sight word sections
    # Find from "Spelling" to end
    lines = text.split("\n")
    in_section = False
    for line in lines:
        l = line.strip()
        if re.search(r"spelling|sight|high.freq|example", l, re.IGNORECASE):
            in_section = True
        if in_section:
            if re.search(r"thank|best,|ms\.sophie|\.pdf$", l, re.IGNORECASE):
                break
            print(f"  {l}")
