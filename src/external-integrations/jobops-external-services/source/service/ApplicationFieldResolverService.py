import re

from source.Utils.Constants import PROTECTED_FIELD_HINTS


class ApplicationFieldResolverService:
    """Resolve form fields from verified candidate facts without guessing."""

    def __init__(self, profile: dict):
        self.profile = profile

    @staticmethod
    def normalize(text: str) -> str:
        return re.sub(r"\s+", " ", text.strip().lower())

    def classify_protected(self, label: str) -> str | None:
        norm = self.normalize(label)
        for key, hints in PROTECTED_FIELD_HINTS.items():
            if any(hint in norm for hint in hints):
                return key
        return None

    def known_value(self, label: str) -> str | None:
        norm = self.normalize(label)
        identity = self.profile["identity"]
        full_name = identity["name"].strip().split()
        first_name = full_name[0] if full_name else ""
        last_name = " ".join(full_name[1:]) if len(full_name) > 1 else ""

        mappings = [
            (["first name", "given name"], first_name),
            (["last name", "family name", "surname"], last_name),
            (["full name", "name"], identity["name"]),
            (["email"], identity["email"]),
            (["phone", "mobile"], identity["phone"]),
            (["linkedin"], identity["linkedin"]),
            (["portfolio", "website", "personal site"], identity["portfolio"]),
            (["current location", "location"], identity["current_location"]),
        ]
        for hints, value in mappings:
            if any(hint in norm for hint in hints):
                return value
        return None
