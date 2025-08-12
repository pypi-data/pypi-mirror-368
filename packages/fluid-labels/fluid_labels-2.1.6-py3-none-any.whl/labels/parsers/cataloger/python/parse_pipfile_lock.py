import logging
from typing import TYPE_CHECKING

from labels.model.file import Scope
from labels.utils.strings import format_exception, normalize_name

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import ItemsView

from typing import cast

from pydantic import ValidationError

from labels.model.file import Location, LocationReadCloser
from labels.model.indexables import IndexedDict, ParsedValue
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.python.utils import package_url
from labels.parsers.collection.json import parse_json_with_tree_sitter

LOGGER = logging.getLogger(__name__)


def _get_location(location: Location, sourceline: int, *, is_dev: bool) -> Location:
    location.scope = Scope.DEV if is_dev else Scope.PROD
    if location.coordinates:
        c_upd = {"line": sourceline}
        l_upd = {"coordinates": location.coordinates.model_copy(update=c_upd)}
        return location.model_copy(update=l_upd)
    return location


def _get_version(value: IndexedDict[str, ParsedValue]) -> str:
    version = value.get("version")
    if not isinstance(version, str):
        return ""
    return version.strip("=<>~^ ")


def _get_packages(
    reader: LocationReadCloser,
    dependencies: ParsedValue | None,
    *,
    is_dev: bool = False,
) -> list[Package]:
    if dependencies is None or not isinstance(dependencies, IndexedDict):
        return []

    packages = []

    items: ItemsView[str, ParsedValue] = dependencies.items()
    for name, value in items:
        if not isinstance(value, IndexedDict) or not isinstance(name, str):
            continue
        version = _get_version(value)
        if not name or not version:
            continue

        location = _get_location(reader.location, value.position.start.line, is_dev=is_dev)

        normalized_name = normalize_name(name, PackageType.PythonPkg)
        p_url = package_url(normalized_name, version, None)

        try:
            packages.append(
                Package(
                    name=normalized_name,
                    version=version,
                    locations=[location],
                    language=Language.PYTHON,
                    type=PackageType.PythonPkg,
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
                        "location": location.path(),
                    },
                },
            )
            continue

    return packages


def parse_pipfile_lock_deps(
    _resolver: Resolver | None,
    _env: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    content = cast(
        "IndexedDict[str, ParsedValue]",
        parse_json_with_tree_sitter(reader.read_closer.read()),
    )
    deps: ParsedValue | None = content.get("default")
    dev_deps: ParsedValue | None = content.get("develop")
    packages = [
        *_get_packages(reader, deps),
        *_get_packages(reader, dev_deps, is_dev=True),
    ]
    return packages, []
