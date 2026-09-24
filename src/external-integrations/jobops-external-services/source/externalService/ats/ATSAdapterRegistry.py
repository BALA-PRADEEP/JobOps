from source.Utils.Errors import UnsupportedATSError
from source.externalService.ats.GreenhouseATSAdapter import GreenhouseATSAdapter


class ATSAdapterRegistry:
    _ADAPTERS = {
        "greenhouse": GreenhouseATSAdapter,
    }

    @classmethod
    def create(cls, ats_type: str, profile: dict, resume_path: str):
        adapter_class = cls._ADAPTERS.get(ats_type)
        if adapter_class is None:
            raise UnsupportedATSError(f"ATS dry-run adapter not implemented: {ats_type}")
        return adapter_class(profile, resume_path)

    @classmethod
    def supported(cls) -> set[str]:
        return set(cls._ADAPTERS)
