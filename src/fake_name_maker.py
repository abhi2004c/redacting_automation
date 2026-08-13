import json
import re
from pathlib import Path

from faker import Faker


fake = Faker("en_IN")


class Anonymizer:

    def __init__(self, map_file):

        self.map_file = Path(map_file)

        self.replacements = self.load_map()

        # Keep track of all fake values that have already
        # been generated so we don't accidentally generate
        # the same fake value for two different originals.
        self.generated_values = set()

        for category in self.replacements.values():

            if not isinstance(category, dict):
                continue

            for replacement in category.values():

                self.generated_values.add(
                    replacement
                )

    # ---------------------------------------------------------
    # NORMALIZATION
    # ---------------------------------------------------------

    def normalize(self, value):

        """
        Normalize a value for comparison.

        Examples:

            "HDFC   Bank Limited"
            "HDFC Bank Limited"

        become the same normalized value.

        Also removes a leading "the" so:

            "the BSE Limited"
            "BSE Limited"

        are treated as the same organization.
        """

        value = re.sub(
            r"\s+",
            " ",
            value.strip()
        )

        value = re.sub(
            r"^the\s+",
            "",
            value,
            flags=re.IGNORECASE
        )

        return value.casefold()

    # ---------------------------------------------------------
    # LOAD EXISTING MAP
    # ---------------------------------------------------------

    def load_map(self):

        """
        Load the persistent replacement map.

        If replacements.json doesn't exist, start with
        an empty mapping.
        """

        if not self.map_file.exists():
            return {}

        try:

            with open(
                self.map_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

                if isinstance(data, dict):
                    return data

        except (
            OSError,
            json.JSONDecodeError
        ) as error:

            print(
                f"Warning: Could not load replacement map: {error}"
            )

        return {}

    # ---------------------------------------------------------
    # SAVE MAP
    # ---------------------------------------------------------

    def save_map(self):

        """
        Save the replacement map to JSON.
        """

        self.map_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            self.map_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.replacements,
                file,
                indent=4,
                ensure_ascii=False
            )

    # ---------------------------------------------------------
    # GET REPLACEMENT
    # ---------------------------------------------------------

    def get_replacement(
        self,
        pii_type,
        original
    ):

        """
        Return a consistent fake value for a PII value.

        If the original value has already been seen,
        return the existing fake value.

        Otherwise generate a new fake value and store it.
        """

        if pii_type not in self.replacements:

            self.replacements[pii_type] = {}

        normalized_original = self.normalize(
            original
        )

        # -----------------------------------------------------
        # Search for an existing mapping.
        #
        # This comparison is normalized, so values such as:
        #
        #   "the BSE Limited"
        #   "BSE Limited"
        #
        # can share the same replacement.
        # -----------------------------------------------------

        for (
            stored_value,
            replacement
        ) in self.replacements[
            pii_type
        ].items():

            if (
                self.normalize(stored_value)
                == normalized_original
            ):

                return replacement

        # -----------------------------------------------------
        # No existing mapping.
        # -----------------------------------------------------

        replacement = self.generate_unique_value(
            pii_type
        )

        # Clean whitespace before storing the original.
        #
        # For example:
        #
        # "Distriparks\nPrivate Limited"
        #
        # becomes:
        #
        # "Distriparks Private Limited"
        #
        # This keeps replacements.json clean.
        # -----------------------------------------------------

        clean_original = re.sub(
            r"\s+",
            " ",
            original.strip()
        )

        self.replacements[
            pii_type
        ][clean_original] = replacement

        self.generated_values.add(
            replacement
        )

        return replacement

    # ---------------------------------------------------------
    # GENERATE UNIQUE VALUE
    # ---------------------------------------------------------

    def generate_unique_value(
        self,
        pii_type
    ):

        """
        Generate a unique fake value.

        A maximum number of attempts prevents the
        anonymizer from getting stuck forever.
        """

        MAX_ATTEMPTS = 1000

        for _ in range(MAX_ATTEMPTS):

            value = self.generate_fake_value(
                pii_type
            )

            if value not in self.generated_values:

                return value

        raise RuntimeError(
            "Could not generate a unique fake value "
            f"for PII type '{pii_type}' after "
            f"{MAX_ATTEMPTS} attempts."
        )

    # ---------------------------------------------------------
    # GENERATE FAKE VALUE
    # ---------------------------------------------------------

    def generate_fake_value(
        self,
        pii_type
    ):

        """
        Generate a realistic fake value according
        to the PII category.
        """

        # -----------------------------------------------------
        # PERSON
        # -----------------------------------------------------

        if pii_type == "PERSON":

            return fake.name()

        # -----------------------------------------------------
        # EMAIL
        # -----------------------------------------------------

        if pii_type == "EMAIL":

            return fake.email()

        # -----------------------------------------------------
        # PHONE
        # -----------------------------------------------------

        if pii_type == "PHONE":

            return (
                "+91 "
                + fake.numerify(
                    "9#########"
                )
            )

        # -----------------------------------------------------
        # ORGANIZATION
        # -----------------------------------------------------

        if pii_type == "ORGANIZATION":

            return fake.company()

        # -----------------------------------------------------
        # ADDRESS
        # -----------------------------------------------------

        if pii_type == "ADDRESS":

            return fake.address().replace(
                "\n",
                ", "
            )

        # -----------------------------------------------------
        # DATE / DOB
        # -----------------------------------------------------

        if pii_type == "DATE":

            return fake.date(
                pattern="%d %B %Y"
            )

        # -----------------------------------------------------
        # SSN
        # -----------------------------------------------------

        if pii_type == "SSN":

            return fake.ssn()

        # -----------------------------------------------------
        # CREDIT CARD
        # -----------------------------------------------------

        if pii_type == "CREDIT_CARD":

            return fake.credit_card_number()

        # -----------------------------------------------------
        # IP ADDRESS
        # -----------------------------------------------------

        if pii_type == "IP_ADDRESS":

            return fake.ipv4()

        # -----------------------------------------------------
        # UNKNOWN TYPE
        # -----------------------------------------------------

        return "[REDACTED]"