import logging
from typing import TYPE_CHECKING

from labels.utils.strings import format_exception

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import ItemsView

from typing import cast

from packageurl import PackageURL
from pydantic import ValidationError

from labels.model.file import DependencyType, Location, LocationReadCloser, Scope
from labels.model.indexables import IndexedDict
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.collection.yaml import parse_yaml_with_tree_sitter

LOGGER = logging.getLogger(__name__)


def _get_location(location: Location, sourceline: int, *, is_dev: bool = False) -> Location:
    location.scope = Scope.DEV if is_dev else Scope.PROD
    if location.coordinates:
        c_upd = {"line": sourceline}
        l_upd = {"coordinates": location.coordinates.model_copy(update=c_upd)}
        location.dependency_type = DependencyType.DIRECT
        return location.model_copy(update=l_upd)
    return location


def _get_packages(
    reader: LocationReadCloser,
    dependencies: IndexedDict[str, str] | None,
    *,
    is_dev: bool = False,
) -> list[Package]:
    if dependencies is None:
        return []
    packages = []
    items: ItemsView[str, IndexedDict[str, str] | str] = dependencies.items()
    for name, version in items:
        if not name or not isinstance(version, str) or not version:
            continue
        general_location = _get_location(
            reader.location,
            dependencies.get_key_position(name).start.line,
            is_dev=is_dev,
        )
        try:
            packages.append(
                Package(
                    name=name,
                    version=version,
                    locations=[general_location],
                    language=Language.DART,
                    licenses=[],
                    type=PackageType.DartPubPkg,
                    p_url=PackageURL(  # type: ignore
                        type="pub",
                        name=name,
                        version=version,
                    ).to_string(),
                ),
            )
        except ValidationError as ex:
            LOGGER.warning(
                "Malformed package. Required fields are missing or data types are incorrect.",
                extra={
                    "extra": {
                        "exception": format_exception(str(ex)),
                        "location": general_location.path(),
                    },
                },
            )
            continue
    return packages


def parse_pubspec_yaml(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    content = cast(
        "IndexedDict[str, IndexedDict[str, str]]",
        parse_yaml_with_tree_sitter(reader.read_closer.read()),
    )

    if not content:
        return [], []

    deps: IndexedDict[str, str] | None = content.get("dependencies")
    dev_deps: IndexedDict[str, str] | None = content.get("dev_dependencies")
    packages = [
        *_get_packages(reader, deps, is_dev=False),
        *_get_packages(reader, dev_deps, is_dev=True),
    ]
    return packages, []
