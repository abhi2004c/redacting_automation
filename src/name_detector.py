import re
import spacy


nlp = spacy.load("en_core_web_sm")


# ---------------------------------------------------------
# PERSON VALIDATION
# ---------------------------------------------------------

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


# Individual words that make a PERSON candidate suspicious.
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
}


PERSON_CONTEXT = re.compile(
    r"(?:"
    r"\bname\b"
    r"|\bcontact person\b"
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


# ---------------------------------------------------------
# ORGANIZATION VALIDATION
# ---------------------------------------------------------

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
    "stock exchange",
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


def looks_like_person_name(value):

    value = re.sub(r"\s+", " ", value.strip())
    lower = value.casefold()

    if len(value) < 5 or len(value) > 60:
        return False

    if any(char.isdigit() for char in value):
        return False

    if "@" in value or "www." in lower:
        return False

    if any(
        char in value
        for char in ["/", ":", "\t", "\n"]
    ):
        return False

    if lower in PERSON_BLOCKLIST:
        return False

    words = lower.split()

    if not 2 <= len(words) <= 5:
        return False

    # Reject names containing document/company terminology.
    if any(
        word in PERSON_NON_NAME_WORDS
        for word in words
    ):
        return False

    alpha_count = sum(
        char.isalpha()
        for char in value
    )

    if alpha_count / len(value) < 0.75:
        return False

    return True


def person_confidence(text, start, end):

    context_start = max(
        0,
        start - 80
    )

    context_end = min(
        len(text),
        end + 80
    )

    context = text[
        context_start:context_end
    ]

    score = 1

    # Strong person context.
    if PERSON_CONTEXT.search(context):
        score += 3

    # Strong non-person context.
    if NON_PERSON_CONTEXT.search(context):
        score -= 3

    return score


def looks_like_organization(value):

    value = re.sub(
        r"\s+",
        " ",
        value.strip()
    )

    lower = value.casefold()

    # Basic length checks
    if len(value) < 4:
        return False

    if len(value) > 120:
        return False

    # --------------------------------------------
    # Reject exact generic/document phrases
    # --------------------------------------------

    if lower in ORG_BLOCKLIST:
        return False

    # --------------------------------------------
    # Reject document-context phrases
    # --------------------------------------------

    for term in ORG_DOCUMENT_TERMS:

        if term in lower:
            return False

    # --------------------------------------------
    # Reject incomplete/truncated organization names
    # --------------------------------------------

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

    # --------------------------------------------
    # Reject generic/meaningless company fragments
    # --------------------------------------------

    GENERIC_ORG_NAMES = {
        "bank limited",
        "bank ltd",
        "company limited",
        "private limited",
        "electricals private limited",
        "advisory private limited",
    }

    if lower in GENERIC_ORG_NAMES:
        return False

    # --------------------------------------------
    # Strong legal/company suffix
    # --------------------------------------------

    for suffix in ORG_STRONG_SUFFIXES:

        if lower.endswith(suffix):
            return True

    # --------------------------------------------
    # Strong organization indicators
    # --------------------------------------------

    for indicator in ORG_SPECIAL_INDICATORS:

        if indicator in lower:
            return True

    # --------------------------------------------
    # Conservative default
    # --------------------------------------------

    return False

def detect_ner_pii(text):

    doc = nlp(text)

    findings = []

    for entity in doc.ents:

        value = entity.text.strip()

        # -----------------------------------------------------
        # PERSON
        # -----------------------------------------------------

        if entity.label_ == "PERSON":

            if not looks_like_person_name(value):
                continue

            score = person_confidence(
                text,
                entity.start_char,
                entity.end_char
            )

            if score < 2:
                continue

            findings.append({
                "type": "PERSON",
                "value": value,
                "start": entity.start_char,
                "end": entity.end_char,
                "confidence": (
                    "HIGH"
                    if score >= 4
                    else "MEDIUM"
                ),
                "source": "ner",
            })

        # -----------------------------------------------------
        # ORGANIZATION
        # -----------------------------------------------------

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

    return findings