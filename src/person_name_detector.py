import re


PERSON_LABELS = [
    r"contact\s+person",
    r"name\s+of\s+promoter",
    r"name\s+of\s+shareholder",
    r"name\s+of\s+director",
    r"promoter\s+selling\s+shareholder",
    r"selling\s+shareholder",
    r"managing\s+director",
    r"executive\s+director",
    r"independent\s+director",
    r"chief\s+executive\s+officer",
    r"chief\s+financial\s+officer",
    r"company\s+secretary",
]


PERSON_LABEL_PATTERN = re.compile(
    r"(?:"
    + "|".join(PERSON_LABELS)
    + r")"
    r"\s*[:\-]\s*"
    r"(?:\n\s*)?"
    r"([A-Z][A-Za-z.'’-]+"
    r"(?:\s+[A-Z][A-Za-z.'’-]+){1,4})"
)


def looks_like_name(value):

    value = re.sub(
        r"\s+",
        " ",
        value.strip()
    )

    words = value.split()

    if not 2 <= len(words) <= 5:
        return False

    if len(value) > 70:
        return False

    if any(
        char.isdigit()
        for char in value
    ):
        return False

    if "@" in value:
        return False

    blocked = {
        "company",
        "website",
        "office",
        "department",
        "government",
        "authority",
        "bank",
        "exchange",
        "limited",
        "private",
        "corporation",
        "shareholder",
        "promoter",
        "promoters",
        "director",
        "directors",
        "trust",
        "fund",
        "foundation",
        "agency",
        "account",
        "amount",
        "price",
        "offer",
        "bid",
        "bidder",
        "bidders",
        "tax",
        "cagr",
        "margin",
        "registration",
        "number",
        "information",
        "compliance",
        "officer",
    }

    lower_words = {
        word.casefold()
        for word in words
    }

    if lower_words & blocked:
        return False

    return True


def split_person_candidates(value):

    return [
        part.strip()
        for part in re.split(
            r"\s*/\s*|\s+\band\b\s+",
            value
        )
        if part.strip()
    ]


def detect_context_persons(text):

    findings = []

    for match in PERSON_LABEL_PATTERN.finditer(text):

        value = match.group(1).strip()

        candidates = split_person_candidates(
            value
        )

        search_position = 0

        for candidate in candidates:

            if not looks_like_name(candidate):
                continue

            relative_start = value.find(
                candidate,
                search_position
            )

            if relative_start < 0:
                continue

            start = (
                match.start(1)
                + relative_start
            )

            end = start + len(candidate)

            findings.append({
                "type": "PERSON",
                "value": candidate,
                "start": start,
                "end": end,
                "confidence": "HIGH",
                "source": "context",
                "score": 7,
            })

            search_position = (
                relative_start
                + len(candidate)
            )

    return findings