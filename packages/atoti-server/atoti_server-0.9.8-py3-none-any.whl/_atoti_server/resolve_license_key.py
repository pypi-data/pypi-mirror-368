from _atoti_core import LicenseKeyLocation

from ._resources_directory import RESOURCES_DIRECTORY

_COMMUNITY_LICENSE_KEY_PATH = RESOURCES_DIRECTORY / "community.lic"


def resolve_license_key(
    license_key: LicenseKeyLocation | str,
    /,
) -> str | None:
    match license_key:
        case LicenseKeyLocation.EMBEDDED:
            assert _COMMUNITY_LICENSE_KEY_PATH.exists()
            return resolve_license_key(str(_COMMUNITY_LICENSE_KEY_PATH))
        case LicenseKeyLocation.ENVIRONMENT:
            return None
        case str():
            return license_key
