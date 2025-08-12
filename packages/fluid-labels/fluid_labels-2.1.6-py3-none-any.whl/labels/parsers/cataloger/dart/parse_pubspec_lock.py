import logging
from copy import deepcopy
from typing import TYPE_CHECKING, cast

from packageurl import PackageURL
from pydantic import BaseModel, ValidationError
from urllib3.util import parse_url

from labels.model.relationship import Relationship
from labels.utils.strings import format_exception

if TYPE_CHECKING:  # pragma: no cover
    from labels.model.file import Location

from labels.model.file import DependencyType, LocationReadCloser
from labels.model.indexables import IndexedDict, Position
from labels.model.package import Language, Package, PackageType
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.collection.yaml import parse_yaml_with_tree_sitter


class DartPubspecLickEntry(BaseModel):
    name: str
    version: str
    hosted_url: str
    vcs_url: str


LOGGER = logging.getLogger(__name__)


def get_hosted_url(entry: IndexedDict[str, str | dict[str, str]]) -> str:
    hosted = entry.get("hosted")
    description: dict[str, str] | None = cast(
        "dict[str, str] | None",
        entry.get("description"),
    )

    if hosted == "hosted" and description and description["url"] != "https://pub.dartlang.org":
        if host := parse_url(description["url"]).host:
            return host

        return description["url"]

    return ""


def get_vcs_url(entry: IndexedDict[str, str | dict[str, str]]) -> str:
    source = entry.get("source")
    description: dict[str, str] | None = cast(
        "dict[str, str] | None",
        entry.get("description"),
    )

    if description and source == "git":
        if description.get("path") == ".":
            return f"{description['url']}@{description['resolved-ref']}"
        return description["url"] + f"@{description['resolved-ref']}" + f"#{description['path']}"
    return ""


def package_url(entry: DartPubspecLickEntry) -> str:
    qualifiers = {}
    if entry.hosted_url:
        qualifiers["hosted_url"] = entry.hosted_url
    elif entry.vcs_url:
        qualifiers["vcs_url"] = entry.vcs_url

    return PackageURL(  # type: ignore
        type="pub",
        namespace="",
        name=entry.name,
        version=entry.version,
        qualifiers=qualifiers,
        subpath="",
    ).to_string()


def parse_pubspec_lock(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    package_yaml = cast(
        "IndexedDict[str, IndexedDict[str, IndexedDict[str, str | dict[str, str]]]]",
        parse_yaml_with_tree_sitter(reader.read_closer.read()),
    )
    packages: list[Package] = []
    relationships: list[Relationship] = []
    yaml_packages: IndexedDict[str, IndexedDict[str, str | dict[str, str]]] = package_yaml[
        "packages"
    ]
    items = yaml_packages.items()

    for package_name, package_value in items:
        is_transitive = package_value.get("dependency") == "transitive"
        version = package_value.get("version")

        if not isinstance(version, str) or not package_name or not version:
            continue

        current_location: Location = deepcopy(reader.location)
        if current_location.coordinates:
            position: Position = yaml_packages.get_key_position(package_name)
            current_location.coordinates.line = position.start.line
            current_location.dependency_type = (
                DependencyType.TRANSITIVE if is_transitive else DependencyType.DIRECT
            )
        metadata = DartPubspecLickEntry(
            name=package_name,
            version=version,
            hosted_url=get_hosted_url(package_value),
            vcs_url=get_vcs_url(package_value),
        )
        try:
            packages.append(
                Package(
                    name=package_name,
                    version=version,
                    locations=[current_location],
                    language=Language.DART,
                    licenses=[],
                    type=PackageType.DartPubPkg,
                    p_url=package_url(metadata),
                    metadata=metadata,
                ),
            )
        except ValidationError as ex:
            LOGGER.warning(
                "Malformed package. Required fields are missing or data types are incorrect.",
                extra={
                    "extra": {
                        "exception": format_exception(str(ex)),
                        "location": current_location.path(),
                    },
                },
            )
            continue

    return packages, relationships
