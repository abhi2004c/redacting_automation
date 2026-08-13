import ipaddress
import re


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)


PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)"
)


SSN_PATTERN = re.compile(
    r"\b\d{3}-\d{2}-\d{4}\b"
)


IP_PATTERN = re.compile(
    r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
)


CREDIT_CARD_PATTERN = re.compile(
    r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)"
)


# We only treat a date as a DOB when there is
# explicit birth-date context.
DOB_PATTERN = re.compile(
    r"(?:"
    r"date\s+of\s+birth"
    r"|"
    r"\bDOB\b"
    r"|"
    r"birth\s+date"
    r"|"
    r"born\s+on"
    r")"
    r"\s*[:\-]?\s*"
    r"("
    r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"
    r"|"
    r"\d{1,2}\s+"
    r"(?:January|February|March|April|May|June|July|August|"
    r"September|October|November|December)"
    r"\s+\d{4}"
    r"|"
    r"(?:January|February|March|April|May|June|July|August|"
    r"September|October|November|December)"
    r"\s+\d{1,2},?\s+\d{4}"
    r")",
    re.IGNORECASE
)


def is_valid_ip(value):
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def luhn_check(number):
    """
    Validate a credit-card number using the Luhn algorithm.
    """

    digits = re.sub(r"\D", "", number)

    if not 13 <= len(digits) <= 19:
        return False

    total = 0

    for index, digit in enumerate(digits[::-1]):

        value = int(digit)

        if index % 2 == 1:

            value *= 2

            if value > 9:
                value -= 9

        total += value

    return total % 10 == 0


def detect_regex_pii(text):

    findings = []

    # ---------------------------------------------------------
    # EMAIL
    # ---------------------------------------------------------

    for match in EMAIL_PATTERN.finditer(text):

        findings.append({
            "type": "EMAIL",
            "value": match.group(),
            "start": match.start(),
            "end": match.end(),
            "confidence": "HIGH",
            "source": "regex"
        })

    # ---------------------------------------------------------
    # PHONE
    # ---------------------------------------------------------

    for match in PHONE_PATTERN.finditer(text):

        findings.append({
            "type": "PHONE",
            "value": match.group(),
            "start": match.start(),
            "end": match.end(),
            "confidence": "HIGH",
            "source": "regex"
        })

    # ---------------------------------------------------------
    # SSN
    # ---------------------------------------------------------

    for match in SSN_PATTERN.finditer(text):

        findings.append({
            "type": "SSN",
            "value": match.group(),
            "start": match.start(),
            "end": match.end(),
            "confidence": "HIGH",
            "source": "regex"
        })

    # ---------------------------------------------------------
    # IP ADDRESS
    # ---------------------------------------------------------

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
            "source": "regex"
        })

    # ---------------------------------------------------------
    # CREDIT CARD
    # ---------------------------------------------------------

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
            "source": "regex"
        })

    # ---------------------------------------------------------
    # DATE OF BIRTH
    # ---------------------------------------------------------

    for match in DOB_PATTERN.finditer(text):

        dob = match.group(1)

        findings.append({
            "type": "DATE",
            "value": dob,
            "start": match.start(1),
            "end": match.end(1),
            "confidence": "HIGH",
            "source": "regex"
        })

    return findings