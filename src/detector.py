import ipaddress
import re


# =============================================================
# EMAIL
# =============================================================

EMAIL_PATTERN = re.compile(
    r"\b"
    r"[A-Za-z0-9._%+-]+"
    r"@"
    r"[A-Za-z0-9.-]+"
    r"\."
    r"[A-Za-z]{2,}"
    r"\b"
)


# =============================================================
# PHONE
# =============================================================
#
# Supports examples such as:
#
# +91 9876543210
# +91-9876543210
# +91 98765 43210
# 9876543210
# 09876543210
#
# We require an Indian-looking mobile number beginning with
# 6, 7, 8 or 9.
# =============================================================

PHONE_PATTERN = re.compile(
    r"""
    (?<!\d)
    (?:
        \+91[\s-]?
        |
        0091[\s-]?
        |
        0?
    )
    [6-9]\d{4}
    [\s-]?
    \d{5}
    (?!\d)
    """,
    re.VERBOSE
)


# =============================================================
# SSN
# =============================================================

SSN_PATTERN = re.compile(
    r"(?<!\d)"
    r"\d{3}-\d{2}-\d{4}"
    r"(?!\d)"
)


# =============================================================
# IP ADDRESS
# =============================================================

IP_PATTERN = re.compile(
    r"(?<![\d.])"
    r"(?:\d{1,3}\.){3}\d{1,3}"
    r"(?![\d.])"
)


# =============================================================
# CREDIT CARD
# =============================================================
#
# We deliberately allow spaces and hyphens but validate the
# resulting number using Luhn.
#
# Examples:
#
# 4111111111111111
# 4111 1111 1111 1111
# 4111-1111-1111-1111
# =============================================================

CREDIT_CARD_PATTERN = re.compile(
    r"(?<!\d)"
    r"(?:\d[ -]?){13,19}"
    r"(?!\d)"
)


# =============================================================
# DATE OF BIRTH
# =============================================================
#
# We only classify a date as DATE when there is birth-related
# context.
#
# Examples:
#
# Date of Birth: 15/08/1990
# DOB: 15-08-1990
# Birth Date: January 15, 1990
# Born on 15 August 1990
# =============================================================

MONTHS = (
    r"January|February|March|April|May|June|July|August|"
    r"September|October|November|December"
)


DOB_PATTERN = re.compile(
    r"""
    (?:
        date\s+of\s+birth
        |
        \bDOB\b
        |
        birth\s+date
        |
        born\s+on
        |
        date\s+of\s+birth\s+of
    )
    \s*[:\-]?\s*
    (
        \d{1,2}[/-]\d{1,2}[/-]\d{2,4}
        |
        \d{1,2}\s+
        (?:
            January|February|March|April|May|June|July|August|
            September|October|November|December
        )
        \s+
        \d{4}
        |
        (?:
            January|February|March|April|May|June|July|August|
            September|October|November|December
        )
        \s+
        \d{1,2},?
        \s+
        \d{4}
    )
    """,
    re.IGNORECASE | re.VERBOSE
)


# =============================================================
# ADDRESS
# =============================================================
#
# Addresses are difficult to detect with a pure regex because
# there is no universal address format.
#
# Instead we look for address-related context and capture the
# nearby text.
#
# Examples:
#
# Registered Office: 123 MG Road, Pune, Maharashtra
# Address: Bandra Kurla Complex, Mumbai
# Residential Address: ...
# Mailing Address: ...
# =============================================================

ADDRESS_PATTERN = re.compile(
    r"""
    (?:
        registered\s+office
        |
        corporate\s+office
        |
        registered\s+address
        |
        office\s+address
        |
        residential\s+address
        |
        permanent\s+address
        |
        correspondence\s+address
        |
        mailing\s+address
        |
        communication\s+address
        |
        address
    )
    \s*
    (?:
        of
        |
        is
    )?
    \s*
    [:,\-]?
    \s*
    (
        [^.\n;]{5,200}
    )
    """,
    re.IGNORECASE | re.VERBOSE
)


# =============================================================
# ADDRESS CONTEXT WORDS
# =============================================================

ADDRESS_WORDS = {
    "road",
    "rd",
    "street",
    "st",
    "lane",
    "ln",
    "marg",
    "nagar",
    "colony",
    "apartment",
    "apt",
    "building",
    "bldg",
    "floor",
    "plot",
    "survey",
    "sector",
    "taluka",
    "district",
    "village",
    "estate",
    "complex",
    "park",
    "phase",
    "block",
    "tower",
    "flat",
    "house",
    "pincode",
    "pin",
}


def is_valid_ip(value):
    """
    Validate an IPv4/IPv6 address.
    """

    try:

        ipaddress.ip_address(
            value
        )

        return True

    except ValueError:

        return False


def luhn_check(number):
    """
    Validate a credit-card number using
    the Luhn algorithm.
    """

    digits = re.sub(
        r"\D",
        "",
        number
    )

    if not 13 <= len(digits) <= 19:
        return False

    total = 0

    for index, digit in enumerate(
        digits[::-1]
    ):

        value = int(digit)

        if index % 2 == 1:

            value *= 2

            if value > 9:
                value -= 9

        total += value

    return total % 10 == 0


def looks_like_address(value):
    """
    Determine whether a piece of text looks like
    a physical address.
    """

    lower = value.casefold()

    words = set(
        re.findall(
            r"[a-zA-Z]+",
            lower
        )
    )

    # Strong address indicators
    if words & ADDRESS_WORDS:
        return True

    # PIN code + surrounding text
    if re.search(
        r"\b\d{6}\b",
        value
    ):
        return True

    return False


def clean_address(value):
    """
    Clean an address captured after an address label.
    """

    value = value.strip()

    # Remove trailing punctuation
    value = value.rstrip(
        " ,:-"
    )

    return value


def detect_regex_pii(text):

    findings = []

    # =========================================================
    # EMAIL
    # =========================================================

    for match in EMAIL_PATTERN.finditer(text):

        findings.append({
            "type": "EMAIL",
            "value": match.group(),
            "start": match.start(),
            "end": match.end(),
            "confidence": "HIGH",
            "source": "regex",
        })

    # =========================================================
    # PHONE
    # =========================================================

    for match in PHONE_PATTERN.finditer(text):

        value = match.group()

        # Normalize only for validation
        digits = re.sub(
            r"\D",
            "",
            value
        )

        # Remove country code
        if digits.startswith("91") and len(digits) == 12:
            mobile = digits[2:]

        elif digits.startswith("0091") and len(digits) == 14:
            mobile = digits[4:]

        elif digits.startswith("0") and len(digits) == 11:
            mobile = digits[1:]

        else:
            mobile = digits

        if len(mobile) != 10:
            continue

        if mobile[0] not in "6789":
            continue

        findings.append({
            "type": "PHONE",
            "value": value,
            "start": match.start(),
            "end": match.end(),
            "confidence": "HIGH",
            "source": "regex",
        })

    # =========================================================
    # SSN
    # =========================================================

    for match in SSN_PATTERN.finditer(text):

        findings.append({
            "type": "SSN",
            "value": match.group(),
            "start": match.start(),
            "end": match.end(),
            "confidence": "HIGH",
            "source": "regex",
        })

    # =========================================================
    # IP ADDRESS
    # =========================================================

    for match in IP_PATTERN.finditer(text):

        value = match.group()

        if not is_valid_ip(value):
            continue

        findings.append({
            "type": "IP_ADDRESS",
            "value": value,
            "start": match.start(),
            "end": match.end(),
            "confidence": "HIGH",
            "source": "regex",
        })

    # =========================================================
    # CREDIT CARD
    # =========================================================

    for match in CREDIT_CARD_PATTERN.finditer(text):

        value = match.group()

        if not luhn_check(value):
            continue

        findings.append({
            "type": "CREDIT_CARD",
            "value": value,
            "start": match.start(),
            "end": match.end(),
            "confidence": "HIGH",
            "source": "regex",
        })

    # =========================================================
    # DATE OF BIRTH
    # =========================================================

    for match in DOB_PATTERN.finditer(text):

        dob = match.group(1)

        findings.append({
            "type": "DATE",
            "value": dob,
            "start": match.start(1),
            "end": match.end(1),
            "confidence": "HIGH",
            "source": "regex",
        })

    # =========================================================
    # PHYSICAL ADDRESS
    # =========================================================

    for match in ADDRESS_PATTERN.finditer(text):

        address = clean_address(
            match.group(1)
        )

        if not address:
            continue

        if not looks_like_address(
            address
        ):
            continue

        findings.append({
            "type": "ADDRESS",
            "value": address,
            "start": match.start(1),
            "end": match.end(1),
            "confidence": "HIGH",
            "source": "regex",
        })

    return findings