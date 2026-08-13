import re


# These are generic document labels.
# We are NOT hard-coding any actual person names.
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


# IMPORTANT:
#
# Do NOT use IGNORECASE here.
#
# A person's name normally starts with capitalized words.
PERSON_LABEL_PATTERN = re.compile(
    r"(?:"
    + "|".join(PERSON_LABELS)
    + r")"
    r"\s*[:\-]\s*"
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

    # A reasonable person's name.
    if not 2 <= len(words) <= 5:
        return False

    if len(value) > 70:
        return False

    # No numbers.
    if any(char.isdigit() for char in value):
        return False

    # No email.
    if "@" in value:
        return False

    blocked_words = {
        "company",
        "website",
        "office",
        "department",
        "government",
        "authority",
        "bank",
        "dated",
        "august",
        "september",
        "october",
        "november",
        "december",
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "general",
        "foreign",
        "trade",
        "future",
        "always",
        "continue",
        "continued",
        "act",
        "acted",
        "relation",
        "interested",
        "listed",
        "listing",
        "absolute",
        "responsibility",
        "information",
        "registration",
        "number",
        "compliance",
        "officer",
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
    }

    lower_words = {
        word.casefold()
        for word in words
    }

    if lower_words & blocked_words:
        return False

    return True


def split_person_candidates(value):

    """
    Handles cases such as:

        Kishan Rastogi/Abhijit Diwan

        Kishan Rastogi and Abhijit Diwan
    """

    parts = re.split(
        r"\s*/\s*|\s+\band\b\s+",
        value
    )

    return [
        part.strip()
        for part in parts
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
            })

            search_position = (
                relative_start
                + len(candidate)
            )

    return findings