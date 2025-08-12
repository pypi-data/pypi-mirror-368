import logging
import re
from typing import TYPE_CHECKING

from labels.model.file import Scope
from labels.utils.strings import format_exception, normalize_name

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import ItemsView

from pydantic import ValidationError

from labels.model.file import DependencyType, Location, LocationReadCloser
from labels.model.indexables import IndexedDict, IndexedList, ParsedValue
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.python.utils import package_url
from labels.parsers.collection.toml import parse_toml_with_tree_sitter

LOGGER = logging.getLogger(__name__)


def _get_location(location: Location, sourceline: int, scope: Scope) -> Location:
    location.scope = scope
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
    return str(value.get("version", ""))


def _get_packages(
    reader: LocationReadCloser,
    dependencies: IndexedDict[str, ParsedValue],
    *,
    is_dev: bool = False,
) -> list[Package]:
    packages: list[Package] = []

    items: ItemsView[str, ParsedValue] = dependencies.items()

    for name, value in items:
        version = _get_version(value)
        if not name or not version:
            continue

        location = _get_location(
            reader.location,
            dependencies.get_key_position(name).start.line,
            scope=Scope.DEV if is_dev else Scope.PROD,
        )

        normalized_name = normalize_name(name, PackageType.PythonPkg)
        p_url = package_url(normalized_name, version, None)

        try:
            packages.append(
                Package(
                    name=normalized_name,
                    version=version,
                    locations=[location],
                    language=Language.PYTHON,
                    licenses=[],
                    p_url=p_url,
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


def _get_uv_packages(
    reader: LocationReadCloser,
    dependencies: IndexedList[ParsedValue],
    *,
    is_dev: bool = False,
) -> list[Package]:
    packages: list[Package] = []
    dep_pattern = re.compile(r"^([A-Za-z0-9_.\-]+)\s*([<>=!~]+.*)?$")

    for dep_string in dependencies:
        if not isinstance(dep_string, str):
            continue

        match = dep_pattern.match(dep_string.strip())
        if match:
            name = match.group(1)
            version = match.group(2).strip() if match.group(2) else "*"
        else:
            name = dep_string.strip()
            version = "*"
        if not name:
            continue

        normalized_name = normalize_name(name, PackageType.PythonPkg)
        p_url = package_url(normalized_name, version, None)

        location = _get_location(
            reader.location,
            reader.location.coordinates.line
            if reader.location.coordinates and reader.location.coordinates.line is not None
            else 0,
            scope=Scope.DEV if is_dev else Scope.PROD,
        )
        try:
            packages.append(
                Package(
                    name=normalized_name,
                    version=version,
                    locations=[location],
                    language=Language.PYTHON,
                    licenses=[],
                    p_url=p_url,
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
    return packages


def _parse_poetry_dependencies(
    content: IndexedDict[str, ParsedValue],
    reader: LocationReadCloser,
) -> list[Package]:
    packages: list[Package] = []
    tool = content.get("tool")
    if not isinstance(tool, IndexedDict):
        return packages

    poetry = tool.get("poetry")
    if not isinstance(poetry, IndexedDict):
        return packages

    deps = poetry.get("dependencies")
    if isinstance(deps, IndexedDict):
        packages.extend(_get_packages(reader, deps))

    group = poetry.get("group")
    if isinstance(group, IndexedDict):
        dev = group.get("dev")
        if isinstance(dev, IndexedDict):
            dev_deps = dev.get("dependencies")
            if isinstance(dev_deps, IndexedDict):
                packages.extend(_get_packages(reader, dev_deps, is_dev=True))

    dev_dependencies = poetry.get("dev-dependencies")
    if isinstance(dev_dependencies, IndexedDict):
        packages.extend(_get_packages(reader, dev_dependencies, is_dev=True))

    return packages


def _parse_uv_dependencies(
    content: IndexedDict[str, ParsedValue],
    reader: LocationReadCloser,
) -> list[Package]:
    packages: list[Package] = []
    project = content.get("project")
    if not isinstance(project, IndexedDict):
        return packages

    uv_deps = project.get("dependencies")
    if isinstance(uv_deps, IndexedList):
        packages.extend(_get_uv_packages(reader, uv_deps))

    optional_deps = project.get("optional-dependencies")
    if isinstance(optional_deps, IndexedDict):
        uv_dev_deps = optional_deps.get("dev")
        if isinstance(uv_dev_deps, IndexedList):
            packages.extend(_get_uv_packages(reader, uv_dev_deps, is_dev=True))

    dependency_groups = content.get("dependency-groups")
    if isinstance(dependency_groups, IndexedDict):
        dev_group = dependency_groups.get("dev")
        if isinstance(dev_group, IndexedList):
            packages.extend(_get_uv_packages(reader, dev_group, is_dev=True))

    return packages


def parse_pyproject_toml(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    content = parse_toml_with_tree_sitter(reader.read_closer.read())

    packages = []
    packages.extend(_parse_poetry_dependencies(content, reader))
    packages.extend(_parse_uv_dependencies(content, reader))

    return packages, []
