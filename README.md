# Redacting Automation

Ever needed to share a document but it's full of real names, emails, and phone numbers? This tool takes a `.docx` file, finds all the sensitive personal information in it, and replaces everything with realistic-looking fake data — so the document stays readable and useful, just without the real details.

For example:

```
Rajesh Kushal Hegde        →  Mitesh Cherian
rajesh@example.com         →  mitesh.cherian@example.net
+91 9876543210             →  +91 8123456789
HDFC Bank Limited          →  Sundaram Group
```

---

## What gets detected

| Type | How it's found |
|---|---|
| Person names | spaCy AI model + context clues like "Director:" or "Mr." |
| Organizations | spaCy AI model + legal suffixes like "Limited", "LLP" |
| Email addresses | Pattern matching |
| Phone numbers | Pattern matching (Indian mobile format) |
| Physical addresses | Pattern matching + keywords like "Road", "Nagar", PIN codes |
| Dates of birth | Pattern matching + context like "DOB:" or "Date of Birth:" |
| SSNs | Pattern matching |
| Credit card numbers | Pattern matching + Luhn algorithm validation |
| IP addresses | Pattern matching + IP validation |

---

## How it works

There's no single method that can catch every type of personal information reliably, so this tool combines three approaches:

**1. Pattern matching (Regex)**
Used for things that follow a predictable format — emails, phone numbers, credit cards, IP addresses, dates. For example, `+91 9876543210` always looks the same, so a pattern can catch it every time. Credit card numbers go one step further and are validated using the Luhn algorithm to avoid false positives.

**2. AI-based name detection (spaCy NER)**
Used for names and organizations, which don't follow a fixed pattern. The spaCy model reads the text and identifies things like `Sarthak Malvadkar` or `HDFC Bank Limited` as named entities. Every detection is then validated — so things like `Model Colony` or `Kushal Electricals` don't get mistakenly flagged as person names.

**3. Context-based detection**
Some names are hard for the AI to catch on its own. This layer looks for patterns like:
```
Director: Sarthak Malvadkar
Contact Person: Rajesh Kushal Hegde
Managing Director: Rohit Hegde
```
...and extracts the name that follows the label.

All three methods run together, overlapping detections are resolved, and then replacements are applied.

---

## Consistent replacements

If the same name appears 50 times in a document, it gets replaced with the same fake name every time — not 50 different ones. This keeps the document coherent.

All mappings are saved to `output/replacements.json`:

```json
{
    "PERSON": {
        "Rajesh Kushal Hegde": "Mitesh Cherian"
    },
    "EMAIL": {
        "rajesh@example.com": "mitesh.cherian@example.net"
    }
}
```

The next time you run the tool on the same document, it loads this file and reuses the same replacements. Nothing changes between runs.

---

## Input → Output

**Input:** Place your `.docx` file here:
```
input/Red Herring Prospectus.docx
```

**Output:** Two files are created in the `output/` folder:
```
output/redacted_prospectus.docx   ← the cleaned document
output/replacements.json          ← the mapping of what was replaced
```

The original document is never modified.

The tool processes everything in the document — normal paragraphs, tables, and table cells.

---

## Project structure

```
redacted/
├── src/
│   ├── main.py                  # Runs everything
│   ├── detector.py              # Pattern-based detection (emails, phones, etc.)
│   ├── name_detector.py         # AI-based name and org detection
│   ├── person_name_detector.py  # Context-based person detection
│   ├── document_processor.py   # Reads the .docx, applies replacements, saves output
│   └── fake_name_maker.py      # Generates fake values and manages the replacement map
├── input/                       # Put your .docx here
├── output/                      # Redacted document and replacements.json appear here
└── requirement.txt
```

---

## Setup

```bash
pip install -r requirement.txt
python -m spacy download en_core_web_sm
```

---

## Running it

```bash
cd src
python main.py
```

That's it. The tool reads `input/Red Herring Prospectus.docx`, processes it, and writes the results to `output/`.

---

## What you'll see in the terminal

While running, the tool prints a live audit of what it's detecting and rejecting. At the end, you get a summary like this:

```
============================================================
FINAL DETECTION SUMMARY

PERSON          : 23
ORGANIZATION    : 52
EMAIL           : 26
PHONE           : 1
ADDRESS         : 3
SSN             : 0
CREDIT_CARD     : 0
DATE            : 0
IP_ADDRESS      : 0
============================================================
```

A `0` just means that type of information wasn't found in the document — not that the detector is broken.

---

## Limitations

This tool works well but isn't perfect. A few things to keep in mind:

- Names can sometimes look like regular words, and the AI model may miss some or flag the wrong things
- Addresses come in too many formats to catch everything reliably
- The tool is tuned for Indian documents (Indian phone numbers, Indian locale for fake data)
- Always do a quick review of the output before sharing anything highly sensitive

---

## Possible future improvements

- PDF support
- Better address detection
- Multi-country phone number formats
- A simple web interface to upload and download documents
- Confidence scores shown in the output

---

## Notes

- `input/` and `output/` are gitignored — your documents won't accidentally get committed
- Fake data is generated using the Indian locale (`en_IN`) via the Faker library
- Variations like `"the BSE Limited"` and `"BSE Limited"` are treated as the same entity and get the same replacement
