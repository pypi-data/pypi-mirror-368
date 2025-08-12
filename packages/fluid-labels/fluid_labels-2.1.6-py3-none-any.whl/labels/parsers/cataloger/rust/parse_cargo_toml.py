import logging
from typing import TYPE_CHECKING

from labels.utils.strings import format_exception

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import ItemsView

from pydantic import ValidationError

from labels.model.file import DependencyType, Location, LocationReadCloser, Scope
from labels.model.indexables import IndexedDict, ParsedValue
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.rust.utils import package_url
from labels.parsers.collection.toml import parse_toml_with_tree_sitter

LOGGER = logging.getLogger(__name__)


def _get_location(location: Location, sourceline: int) -> Location:
    if location.coordinates:
        c_upd = {"line": sourceline}
        l_upd = {"coordinates": location.coordinates.model_copy(update=c_upd)}
        location.dependency_type = DependencyType.DIRECT
        return location.model_copy(update=l_upd)
    return location


def _get_version(value: ParsedValue) -> str | None:
    if isinstance(value, str):
        return value
    if not isinstance(value, IndexedDict):
        return None
    if "git" in value:
        repo_url: str = str(value.get("git", ""))
        branch: str = str(value.get("branch", ""))
        if repo_url and branch:
            return f"{repo_url}@{branch}"
    version: str = str(value.get("version", ""))
    return version


def _get_packages(
    reader: LocationReadCloser,
    dependencies: ParsedValue,
    *,
    is_dev: bool,
) -> list[Package]:
    if dependencies is None or not isinstance(dependencies, IndexedDict):
        return []

    packages = []

    items: ItemsView[str, ParsedValue] = dependencies.items()

    for name, value in items:
        version = _get_version(value)
        if not name or not version:
            continue

        location = _get_location(reader.location, dependencies.get_key_position(name).start.line)
        location.scope = Scope.DEV if is_dev else Scope.PROD
        try:
            packages.append(
                Package(
                    name=name,
                    version=version,
                    locations=[location],
                    language=Language.RUST,
                    licenses=[],
                    p_url=package_url(name=name, version=version),
                    type=PackageType.RustPkg,
                ),
            )
        except ValidationError as ex:
            LOGGER.warning(
                "Malformed package. Required fields are missing or data types are incorrect.",
                extra={
                    "extra": {
                        "exception": format_exception(str(ex)),
                        "location": location.path(),
                    },
                },
            )
            continue

    return packages


def parse_cargo_toml(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    content: IndexedDict[
        str,
        ParsedValue,
    ] = parse_toml_with_tree_sitter(reader.read_closer.read())

    deps: ParsedValue = content.get(
        "dependencies",
    )
    dev_deps: ParsedValue = content.get(
        "dev-dependencies",
    )
    packages = [
        *_get_packages(reader, deps, is_dev=False),
        *_get_packages(reader, dev_deps, is_dev=True),
    ]
    return packages, []
