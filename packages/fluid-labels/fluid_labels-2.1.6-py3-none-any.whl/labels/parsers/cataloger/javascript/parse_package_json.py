import logging
from copy import deepcopy
from typing import cast

from pydantic import ValidationError

from labels.model.file import DependencyType, LocationReadCloser, Scope
from labels.model.indexables import IndexedDict, ParsedValue
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.javascript.model import NpmPackage
from labels.parsers.cataloger.javascript.package import package_url
from labels.parsers.collection.json import parse_json_with_tree_sitter
from labels.utils.strings import format_exception

LOGGER = logging.getLogger(__name__)


def _create_package(
    package_json: IndexedDict[str, ParsedValue],
    reader: LocationReadCloser,
    package_name: str,
    specifier: str,
    *,
    is_dev: bool,
) -> Package | None:
    current_location = deepcopy(reader.location)
    current_location.scope = Scope.DEV if is_dev else Scope.PROD
    dependencies_key = "devDependencies" if is_dev else "dependencies"
    pkg: IndexedDict[str, ParsedValue] = cast(
        "IndexedDict[str, ParsedValue]",
        package_json[dependencies_key],
    )
    if current_location.coordinates:
        current_location.coordinates.line = pkg.get_key_position(package_name).start.line
        current_location.dependency_type = DependencyType.DIRECT
    try:
        return Package(
            name=package_name,
            version=specifier,
            type=PackageType.NpmPkg,
            language=Language.JAVASCRIPT,
            licenses=[],
            locations=[current_location],
            p_url=package_url(package_name, specifier),
            metadata=NpmPackage(
                name=package_name,
                version=specifier,
                is_dev=is_dev,
            ),
            is_dev=is_dev,
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
        return None


def parse_package_json(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    package_json: IndexedDict[str, ParsedValue] = cast(
        "IndexedDict[str, ParsedValue]",
        parse_json_with_tree_sitter(reader.read_closer.read()),
    )
    deps: ParsedValue = package_json.get("dependencies", IndexedDict())
    if not isinstance(deps, IndexedDict):
        LOGGER.warning("No deps found in package JSON")
        return ([], [])

    packages = []
    for package_name, specifier in deps.items():
        if not package_name or not specifier:
            continue

        package = _create_package(
            package_json,
            reader,
            package_name,
            str(specifier),
            is_dev=False,
        )
        if package:
            packages.append(package)

    dev_deps: ParsedValue = package_json.get("devDependencies", IndexedDict())
    if not isinstance(dev_deps, IndexedDict):
        LOGGER.warning("No dev deps found in package JSON")
        return ([], [])
    for package_name, specifier in dev_deps.items():
        if not package_name or not specifier:
            continue

        package = _create_package(
            package_json,
            reader,
            package_name,
            str(specifier),
            is_dev=True,
        )
        if package:
            packages.append(package)

    return packages, []
