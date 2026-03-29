import json
from collections import defaultdict

with open("src/data/decoding-words.json") as f:
    data = json.load(f)

print("=== SPELLING UNITS ===")
for u in data["spellingUnits"]:
    print(f"  {u['id']:15s}  patterns={str(u['patterns']):25s}  phoneme={u['phoneme']:8s}  examples={str(u['examples']):30s}  book={u['book']}")

print()
print("=== DECODING WORDS BY UNIT ===")
by_unit = defaultdict(list)
for w in data["decodingWords"]:
    by_unit[w["spellingUnitId"]].append(w)

for uid, words in by_unit.items():
    print(f"\n  [{uid}] ({len(words)} words):")
    for w in sorted(words, key=lambda x: x["word"]):
        print(f"    {w['word']:20s}  breakdown={str(w['decodingBreakdown']):35s}  book={w['book']}")

print()
print(f"=== SIGHT WORDS ({len(data['sightWords'])}) ===")
for s in data["sightWords"]:
    print(f"  {s['word']:15s}  email={s['sourceEmail']}  book={s['book']}")
