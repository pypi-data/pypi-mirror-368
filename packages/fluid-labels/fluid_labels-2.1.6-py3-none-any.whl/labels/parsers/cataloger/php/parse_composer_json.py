from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import ItemsView

from labels.model.file import DependencyType, Location, LocationReadCloser, Scope
from labels.model.indexables import IndexedDict, ParsedValue
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.php.package import package_url
from labels.parsers.collection.json import parse_json_with_tree_sitter

EMPTY_DICT: IndexedDict[str, ParsedValue] = IndexedDict()


def _get_location(location: Location, sourceline: int, *, is_dev: bool) -> Location:
    location.scope = Scope.DEV if is_dev else Scope.PROD
    if location.coordinates:
        c_upd = {"line": sourceline}
        l_upd = {"coordinates": location.coordinates.model_copy(update=c_upd)}
        location.dependency_type = DependencyType.DIRECT
        return location.model_copy(update=l_upd)
    return location


def _get_packages(
    reader: LocationReadCloser,
    dependencies: IndexedDict[str, ParsedValue],
    *,
    is_dev: bool,
) -> list[Package]:
    if not dependencies:
        return []

    items: ItemsView[str, ParsedValue] = dependencies.items()
    return [
        Package(
            name=name,
            version=version,
            locations=[
                _get_location(
                    reader.location,
                    dependencies.get_key_position(name).start.line,
                    is_dev=is_dev,
                ),
            ],
            language=Language.PHP,
            licenses=[],
            type=PackageType.PhpComposerPkg,
            p_url=package_url(name, version),
            is_dev=is_dev,
        )
        for name, version in items
        if isinstance(version, str)
    ]


def parse_composer_json(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    content = cast(
        "IndexedDict[str, ParsedValue]",
        parse_json_with_tree_sitter(reader.read_closer.read()),
    )
    deps: IndexedDict[str, ParsedValue] = cast(
        "IndexedDict[str, ParsedValue]",
        content.get("require", EMPTY_DICT),
    )
    dev_deps: IndexedDict[str, ParsedValue] = cast(
        "IndexedDict[str, ParsedValue]",
        content.get("require-dev", EMPTY_DICT),
    )
    packages = [
        *_get_packages(reader, deps, is_dev=False),
        *_get_packages(reader, dev_deps, is_dev=True),
    ]
    return packages, []
