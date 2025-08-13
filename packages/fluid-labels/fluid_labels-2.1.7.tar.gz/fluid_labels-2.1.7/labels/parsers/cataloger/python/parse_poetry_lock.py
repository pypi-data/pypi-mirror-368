import logging
from collections.abc import Iterable

from pydantic import ValidationError

from labels.model.file import Location, LocationReadCloser
from labels.model.indexables import IndexedDict, IndexedList, ParsedValue
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship, RelationshipType
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.python.model import PythonRequirementsEntry
from labels.parsers.cataloger.python.utils import package_url
from labels.parsers.collection import toml
from labels.utils.strings import format_exception, normalize_name

LOGGER = logging.getLogger(__name__)


def _get_location(location: Location, sourceline: int) -> Location:
    if location.coordinates:
        c_upd = {"line": sourceline}
        l_upd = {"coordinates": location.coordinates.model_copy(update=c_upd)}
        return location.model_copy(update=l_upd)
    return location


def parse_poetry_lock(
    _resolver: Resolver | None,
    _env: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    _content = reader.read_closer.read()

    toml_content: IndexedDict[str, ParsedValue] = toml.parse_toml_with_tree_sitter(_content)

    packages = _parse_packages(toml_content, reader)
    relationships = _parse_relationships(toml_content, packages)

    return packages, relationships


def _parse_packages(
    toml_content: IndexedDict[str, ParsedValue],
    reader: LocationReadCloser,
) -> list[Package]:
    packages = []
    toml_pkgs = toml_content.get("package")
    if not isinstance(toml_pkgs, IndexedList):
        return []
    for package in toml_pkgs:
        if not isinstance(package, IndexedDict):
            continue
        name: str = str(package.get("name", ""))
        version: str = str(package.get("version", ""))

        if not name or not version:
            continue

        normalized_name = normalize_name(name, PackageType.PythonPkg)
        p_url = package_url(normalized_name, version, package)  # type: ignore

        location = (
            _get_location(reader.location, package.get_key_position("version").start.line)
            if isinstance(package, IndexedDict)
            else reader.location
        )

        try:
            packages.append(
                Package(
                    name=normalized_name,
                    version=version,
                    found_by=None,
                    locations=[location],
                    language=Language.PYTHON,
                    p_url=p_url,
                    metadata=PythonRequirementsEntry(
                        name=name,
                        extras=[],
                        markers=p_url,
                    ),
                    licenses=[],
                    type=PackageType.PythonPkg,
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


def _find_package_by_name(packages: list[Package], name: str) -> Package | None:
    return next(
        (p for p in packages if p.name == normalize_name(name, PackageType.PythonPkg)), None
    )


def _get_dependencies(
    package: ParsedValue,
    packages: list[Package],
) -> tuple[Package | None, IndexedDict[str, ParsedValue]] | None:
    if not isinstance(package, IndexedDict):
        return None

    package_name = package.get("name")
    if not isinstance(package_name, str):
        return None

    _pkg = _find_package_by_name(packages, package_name)

    deps = package.get("dependencies")
    if not isinstance(deps, IndexedDict):
        return None

    return _pkg, deps


def _create_relationships_for_package(
    pkg: Package, dependency_names: Iterable[str], packages: list[Package]
) -> list[Relationship]:
    relationships = []
    for dep_name in dependency_names:
        dep_pkg = _find_package_by_name(packages, dep_name)
        if dep_pkg:
            relationships.append(
                Relationship(
                    from_=dep_pkg.id_,
                    to_=pkg.id_,
                    type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
                )
            )
    return relationships


def _parse_relationships(
    toml_content: IndexedDict[str, ParsedValue],
    packages: list[Package],
) -> list[Relationship]:
    relationships = []
    toml_pkgs = toml_content.get("package")

    if not isinstance(toml_pkgs, IndexedList):
        return []

    for package in toml_pkgs:
        pkg_with_deps = _get_dependencies(package, packages)

        if not pkg_with_deps:
            continue

        pkg, deps = pkg_with_deps

        if not pkg or not deps:
            continue

        relationships.extend(_create_relationships_for_package(pkg, deps.keys(), packages))

    return relationships
