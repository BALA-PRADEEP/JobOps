import json
from copy import deepcopy
from functools import lru_cache

from source.Utils.Config import settings


class CandidateProfileService:
    @staticmethod
    @lru_cache(maxsize=1)
    def _load_profile() -> dict:
        with settings.candidate_profile_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    @classmethod
    def get_profile(cls) -> dict:
        return deepcopy(cls._load_profile())

    @classmethod
    def get_protected_fact(cls, key: str):
        return cls._load_profile()["protected_facts"].get(key)

    @classmethod
    def assert_verified(cls, key: str):
        value = cls.get_protected_fact(key)
        if value is None:
            raise ValueError(f"Protected candidate fact is unknown: {key}")
        return value
