import logging
from datetime import datetime

from packageurl import PackageURL
from pydantic import BaseModel, ValidationError

from labels.model.file import Location
from labels.model.package import Digest, Language, Package, PackageType
from labels.model.release import Release
from labels.parsers.cataloger.utils import purl_qualifiers
from labels.utils.licenses.validation import validate_licenses
from labels.utils.strings import format_exception

LOGGER = logging.getLogger(__name__)


class AlpmFileRecord(BaseModel):
    path: str
    type: str | None = None
    uid: str | None = None
    gid: str | None = None
    time: datetime | None = None
    size: str | None = None
    link: str | None = None
    digests: list[Digest] | None = None


class AlpmDBEntry(BaseModel):
    licenses: str = ""
    base_package: str = ""
    package: str = ""
    version: str = ""
    description: str = ""
    architecture: str = ""
    size: int = 0
    packager: str = ""
    url: str = ""
    validation: str = ""
    reason: int = 0
    files: list[AlpmFileRecord] | None = None
    backup: list[AlpmFileRecord] | None = None


def package_url(entry: AlpmDBEntry, distro: Release | None = None) -> str:
    qualifiers = {"arch": entry.architecture}
    if entry.base_package:
        qualifiers["upstream"] = entry.base_package
    return PackageURL(
        type="alpm",
        name=entry.package,
        version=entry.version,
        qualifiers=purl_qualifiers(qualifiers, distro),  # type: ignore
        subpath="",
    ).to_string()


def new_package(
    entry: AlpmDBEntry,
    release: Release | None,
    db_location: Location,
) -> Package | None:
    name = entry.package
    version = entry.version

    if not name or not version:
        return None

    licenses_candidates = entry.licenses.split("\n")

    try:
        return Package(
            name=name,
            version=version,
            locations=[db_location],
            licenses=validate_licenses(licenses_candidates),
            type=PackageType.AlpmPkg,
            metadata=entry,
            p_url=package_url(entry, release),
            language=Language.UNKNOWN_LANGUAGE,
        )
    except ValidationError as ex:
        LOGGER.warning(
            "Malformed package. Required fields are missing or data types are incorrect.",
            extra={
                "extra": {
                    "exception": format_exception(str(ex)),
                    "location": db_location.path(),
                },
            },
        )
        return None
