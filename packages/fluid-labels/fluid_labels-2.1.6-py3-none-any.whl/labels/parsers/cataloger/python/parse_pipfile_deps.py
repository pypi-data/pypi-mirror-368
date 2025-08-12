import logging
from copy import deepcopy

from pydantic import ValidationError

from labels.model.file import DependencyType, Location, LocationReadCloser, Scope
from labels.model.indexables import IndexedDict, ParsedValue
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.python.model import PythonPackage
from labels.parsers.cataloger.python.utils import package_url
from labels.parsers.collection import toml
from labels.utils.strings import format_exception, normalize_name

LOGGER = logging.getLogger(__name__)


def _get_location(location: Location, sourceline: int, scope: Scope) -> Location:
    location.scope = scope
    location.dependency_type = DependencyType.DIRECT
    if location.coordinates:
        c_upd = {"line": sourceline}
        l_upd = {"coordinates": location.coordinates.model_copy(update=c_upd)}
        return location.model_copy(update=l_upd)
    return location


def _get_packages(
    reader: LocationReadCloser,
    toml_packages: IndexedDict[str, ParsedValue],
    *,
    is_dev: bool = False,
) -> list[Package]:
    result = []
    scope = Scope.DEV if is_dev else Scope.PROD
    for package, version_data in toml_packages.items():
        version: str = ""
        if isinstance(version_data, str):
            version = version_data.strip("=<>~^ ")
        if isinstance(version_data, IndexedDict):
            version = str(version_data.get("version", "*")).strip("=<>~^ ")

        if not package or not version or "*" in version:
            continue
        current_location = deepcopy(reader.location)

        location = _get_location(
            current_location,
            package.position.start.line
            if isinstance(package, IndexedDict)
            else toml_packages.get_key_position(package).start.line,
            scope,
        )

        normalized_name = normalize_name(package, PackageType.PythonPkg)
        p_url = package_url(normalized_name, version, None)

        try:
            result.append(
                Package(
                    name=normalized_name,
                    version=version,
                    locations=[location],
                    language=Language.PYTHON,
                    type=PackageType.PythonPkg,
                    metadata=PythonPackage(
                        name=package,
                        version=version,
                    ),
                    p_url=p_url,
                    licenses=[],
                    is_dev=is_dev,
                ),
            )
        except ValidationError as ex:
            LOGGER.warning(
                "Malformed package. Required fields are missing or data types are incorrect.",
                extra={
                    "extra": {
                        "exception": format_exception(str(ex)),
                        "location": reader.location.path(),
                    },
                },
            )
            continue
    return result


def parse_pipfile_deps(
    _resolver: Resolver | None,
    _env: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages = []
    file_content = reader.read_closer.read()
    toml_content: IndexedDict[str, ParsedValue] = toml.parse_toml_with_tree_sitter(file_content)
    toml_packages = toml_content.get("packages")
    if not isinstance(toml_packages, IndexedDict):
        return [], []
    packages = _get_packages(reader, toml_packages)
    dev_deps = toml_content.get("dev-packages")
    if isinstance(dev_deps, IndexedDict):
        dev_pkgs = _get_packages(reader, dev_deps, is_dev=True)
        packages.extend(dev_pkgs)
    return packages, []
