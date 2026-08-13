import re
import spacy


nlp = spacy.load("en_core_web_sm")


# ============================================================
# PERSON VALIDATION
# ============================================================

PERSON_BLOCKLIST = {
    "offer",
    "promoter",
    "promoters",
    "promoter group",
    "promoter selling shareholder",
    "promoter selling shareholders",
    "directors",
    "director",
    "reference rate",
    "registrar",
    "registrar and share transfer agent",
    "bid",
    "bids",
    "bidder",
    "bidders",
    "bid amount",
    "bidder's dp id",
    "email",
    "website",
    "address",
    "telephone",
    "phone",
    "floor",
    "floor price",
    "cap price",
    "offer price",
    "risk",
    "risks",
    "risk factors",
    "mutual funds",
    "shareholder",
    "shareholders",
    "company",
    "board",
    "equity",
    "equity shares",
    "financial information",
    "financial data",
    "financial",
    "operations",
    "password",
    "inventory",
    "trade",
    "fraud",
    "notice",
    "allotment",
    "underwriters",
    "key managerial personnel",
    "key managerial",
}


# Words that strongly indicate that an entity is
# probably NOT a person's name.
PERSON_NON_NAME_WORDS = {
    "website",
    "company",
    "limited",
    "private",
    "corporation",
    "llp",
    "ltd",
    "trust",
    "group",
    "department",
    "ministry",
    "government",
    "authority",
    "bank",
    "exchange",
    "fund",
    "foundation",
    "agency",
    "office",
    "address",
    "account",
    "amount",
    "price",
    "offer",
    "bid",
    "bidder",
    "bidders",
    "shareholder",
    "shareholders",
    "promoter",
    "promoters",
    "director",
    "directors",
    "cagr",
    "margin",
    "tax",
    "dated",
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
}


# Strong person-related context.
PERSON_CONTEXT = re.compile(
    r"(?:"
    r"\bname\b"
    r"|\bcontact person\b"
    r"|\bcontact\b"
    r"|\bdirector\b"
    r"|\bpromoter\b"
    r"|\bchairman\b"
    r"|\bmanaging director\b"
    r"|\bchief executive officer\b"
    r"|\bchief financial officer\b"
    r"|\bcompany secretary\b"
    r"|\bmr\.?\b"
    r"|\bmrs\.?\b"
    r"|\bms\.?\b"
    r"|\bdr\.?\b"
    r")",
    re.IGNORECASE,
)


# Context that strongly suggests the entity is NOT a person.
NON_PERSON_CONTEXT = re.compile(
    r"(?:"
    r"\btaluka\b"
    r"|\bvillage\b"
    r"|\broad\b"
    r"|\blane\b"
    r"|\bmarg\b"
    r"|\bpark\b"
    r"|\bfacility\b"
    r"|\bprivate limited\b"
    r"|\blimited\b"
    r"|\bcorporation\b"
    r"|\bcomplex\b"
    r"|\baccount\b"
    r"|\bbid\b"
    r"|\bbidder\b"
    r"|\boffer\b"
    r"|\bshareholder\b"
    r"|\bshares\b"
    r"|\bprice\b"
    r"|\bamount\b"
    r"|\bcagr\b"
    r"|\bmargin\b"
    r"|\bair conditioning\b"
    r"|\btax\b"
    r")",
    re.IGNORECASE,
)


# ============================================================
# ORGANIZATION VALIDATION
# ============================================================

ORG_STRONG_SUFFIXES = (
    "limited",
    "private limited",
    "pvt ltd",
    "ltd",
    "llp",
    "llc",
    "corporation",
    "corp.",
    "inc.",
    "inc",
    "n.a.",
)


ORG_SPECIAL_INDICATORS = (
    "bank of india",
    "bank of",
    "metal exchange",
    "reserve bank",
    "payments corporation",
    "depository limited",
    "family trust",
    "foundation",
)


ORG_BLOCKLIST = {
    "bank",
    "bankers",
    "corporate office",
    "registered office",
    "monitoring agency",
    "monitoring agency agreement",
    "sponsor banker",
    "sponsor banks",
    "refund bank",
    "escrow collection bank",
    "public offer account bank",
    "offer escrow collection bank",
    "bank balances",
    "bank balances and advances",
    "transit insurance",
    "marine insurance",
    "securities transaction tax",
    "foreign exchange management",
    "gross national disposable income",
    "capital structure",
    "financial information",
    "financial data",
    "market data",
    "key financial",
    "memorandum of association",
    "articles of association",
    "board",
    "company",
    "offer",
}


ORG_DOCUMENT_TERMS = (
    "for the offer",
    "for the issue",
    "for bidders",
    "bid amount",
    "bidder",
    "bidders",
    "account number",
    "dp id",
    "password",
    "financial year",
    "tax deducted",
    "pat margin",
    "pat cagr",
)


# ============================================================
# PERSON NAME SHAPE
# ============================================================

def name_shape_score(value):
    """
    Score how much the text looks like a person's name.

    This intentionally does NOT require strong person context.
    That allows us to recover genuine names that spaCy detects
    without a nearby "Director" or "Contact Person" label.
    """

    value = re.sub(
        r"\s+",
        " ",
        value.strip()
    )

    lower = value.casefold()
    words = value.split()
    lower_words = lower.split()

    score = 0
    reasons = []

    # --------------------------------------------------------
    # Length
    # --------------------------------------------------------

    if 5 <= len(value) <= 60:
        score += 1
        reasons.append("reasonable length")

    else:
        return score, reasons

    # --------------------------------------------------------
    # Word count
    # --------------------------------------------------------

    if 2 <= len(words) <= 5:
        score += 2
        reasons.append("2-5 words")

    else:
        return score, reasons

    # --------------------------------------------------------
    # Numbers
    # --------------------------------------------------------

    if any(
        char.isdigit()
        for char in value
    ):
        return -5, ["contains number"]

    # --------------------------------------------------------
    # Email / URL
    # --------------------------------------------------------

    if "@" in value:
        return -5, ["email"]

    if "www." in lower:
        return -5, ["website"]

    # --------------------------------------------------------
    # Obvious separators
    # --------------------------------------------------------

    if any(
        char in value
        for char in ["/", ":", "\t", "\n"]
    ):
        return -4, ["contains separator"]

    # --------------------------------------------------------
    # Exact blocked phrase
    # --------------------------------------------------------

    if lower in PERSON_BLOCKLIST:
        return -5, ["blocked phrase"]

    # --------------------------------------------------------
    # Non-person words
    # --------------------------------------------------------

    bad_words = (
        set(lower_words)
        & PERSON_NON_NAME_WORDS
    )

    if bad_words:

        return (
            -4,
            [
                "non-person words: "
                + ", ".join(sorted(bad_words))
            ]
        )

    # --------------------------------------------------------
    # Alphabetic ratio
    # --------------------------------------------------------

    alpha_count = sum(
        char.isalpha()
        for char in value
    )

    if alpha_count / len(value) >= 0.75:

        score += 1
        reasons.append("mostly alphabetic")

    else:

        score -= 2
        reasons.append("not mostly alphabetic")

    # --------------------------------------------------------
    # Capitalization
    #
    # Example:
    #
    # Sarthak Malvadkar       -> strong
    # sarthak malvadkar       -> weaker
    # --------------------------------------------------------

    capitalized_words = 0

    for word in words:

        cleaned = re.sub(
            r"[^A-Za-zÀ-ÖØ-öø-ÿ]",
            "",
            word
        )

        if not cleaned:
            continue

        if cleaned[0].isupper():

            capitalized_words += 1

    if capitalized_words == len(words):

        score += 1
        reasons.append("proper capitalization")

    elif capitalized_words >= 2:

        score += 0
        reasons.append("partially capitalized")

    else:

        score -= 1
        reasons.append("poor capitalization")

    return score, reasons


def looks_like_person_name(value):

    score, _ = name_shape_score(value)

    return score >= 4


# ============================================================
# PERSON CONFIDENCE
# ============================================================

def person_confidence(
    text,
    start,
    end,
    value
):
    """
    Calculate confidence using:

        - spaCy PERSON classification
        - name shape
        - surrounding context
    """

    score = 0
    reasons = []

    # --------------------------------------------------------
    # spaCy classified it as PERSON
    # --------------------------------------------------------

    score += 2
    reasons.append("spaCy PERSON")

    # --------------------------------------------------------
    # Name shape
    # --------------------------------------------------------

    shape_score, shape_reasons = (
        name_shape_score(value)
    )

    score += shape_score

    reasons.extend(shape_reasons)

    # --------------------------------------------------------
    # Surrounding context
    # --------------------------------------------------------

    context_start = max(
        0,
        start - 100
    )

    context_end = min(
        len(text),
        end + 100
    )

    context = text[
        context_start:context_end
    ]

    # Strong person context
    if PERSON_CONTEXT.search(context):

        score += 3
        reasons.append(
            "person context"
        )

    # Strong non-person context
    if NON_PERSON_CONTEXT.search(context):

        score -= 3
        reasons.append(
            "non-person context"
        )

    # --------------------------------------------------------
    # Sentence-like candidate detection
    # --------------------------------------------------------

    sentence_words = {
        "hence",
        "therefore",
        "however",
        "whereas",
        "thereafter",
        "future",
        "always",
        "continue",
        "continued",
        "relation",
        "interested",
        "information",
        "responsibility",
    }

    candidate_words = {
        word.casefold()
        for word in re.findall(
            r"[A-Za-z]+",
            value
        )
    }

    sentence_overlap = (
        candidate_words
        & sentence_words
    )

    if sentence_overlap:

        score -= 4

        reasons.append(
            "sentence-like words: "
            + ", ".join(
                sorted(sentence_overlap)
            )
        )

    return score, reasons


# ============================================================
# ORGANIZATION
# ============================================================

def looks_like_organization(value):

    value = re.sub(
        r"\s+",
        " ",
        value.strip()
    )

    lower = value.casefold()

    if len(value) < 4:
        return False

    if len(value) > 120:
        return False

    # --------------------------------------------------------
    # Reject document phrases
    # --------------------------------------------------------

    if re.match(
        r"^the\s+offer\b",
        lower
    ):
        return False

    if re.match(
        r"^the\s+issue\b",
        lower
    ):
        return False

    # --------------------------------------------------------
    # Reject incomplete/truncated phrases
    # --------------------------------------------------------

    if lower.endswith(
        (
            " of",
            " and",
            " the",
            " for",
            " in",
            " to",
        )
    ):
        return False

    # --------------------------------------------------------
    # Exact blocklist
    # --------------------------------------------------------

    if lower in ORG_BLOCKLIST:
        return False

    # --------------------------------------------------------
    # Document terms
    # --------------------------------------------------------

    for term in ORG_DOCUMENT_TERMS:

        if term in lower:
            return False

    # --------------------------------------------------------
    # Generic company fragments
    # --------------------------------------------------------

    generic_names = {
        "bank limited",
        "bank ltd",
        "company limited",
        "private limited",
        "electricals private limited",
        "advisory private limited",
    }

    if lower in generic_names:
        return False

    # --------------------------------------------------------
    # Strong legal suffix
    # --------------------------------------------------------

    for suffix in ORG_STRONG_SUFFIXES:

        if lower.endswith(suffix):
            return True

    # --------------------------------------------------------
    # Strong organization indicator
    # --------------------------------------------------------

    for indicator in ORG_SPECIAL_INDICATORS:

        if indicator in lower:
            return True

    return False


# ============================================================
# NER DETECTOR
# ============================================================

def detect_ner_pii(text):

    doc = nlp(text)

    findings = []

    print()
    print("=" * 70)
    print("PERSON CANDIDATE AUDIT")
    print("=" * 70)

    seen_persons = set()

    for entity in doc.ents:

        value = entity.text.strip()

        # ====================================================
        # PERSON
        # ====================================================

        if entity.label_ == "PERSON":

            normalized = re.sub(
                r"\s+",
                " ",
                value.casefold()
            )

            # Avoid printing duplicate candidates.
            if normalized in seen_persons:
                continue

            seen_persons.add(normalized)

            score, reasons = person_confidence(
                text,
                entity.start_char,
                entity.end_char,
                value
            )

            # ------------------------------------------------
            # Acceptance threshold
            #
            # >= 4 gives us a balance between precision
            # and recall.
            # ------------------------------------------------

            accepted = score >= 4

            if accepted:

                print(
                    f"[PERSON ACCEPT] "
                    f"{value} "
                    f"| score={score} "
                    f"| {'; '.join(reasons)}"
                )

                findings.append({
                    "type": "PERSON",
                    "value": value,
                    "start": entity.start_char,
                    "end": entity.end_char,
                    "confidence": (
                        "HIGH"
                        if score >= 7
                        else "MEDIUM"
                    ),
                    "source": "ner",
                    "score": score,
                })

            else:

                print(
                    f"[PERSON REJECT] "
                    f"{value} "
                    f"| score={score} "
                    f"| {'; '.join(reasons)}"
                )

        # ====================================================
        # ORGANIZATION
        # ====================================================

        elif entity.label_ == "ORG":

            if not looks_like_organization(value):
                continue

            findings.append({
                "type": "ORGANIZATION",
                "value": value,
                "start": entity.start_char,
                "end": entity.end_char,
                "confidence": "MEDIUM",
                "source": "ner",
            })

    print("=" * 70)
    print(
        f"PERSON candidates examined: "
        f"{len(seen_persons)}"
    )
    print("=" * 70)
    print()

    return findings