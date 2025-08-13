from copy import deepcopy
from typing import cast

from labels.model.file import LocationReadCloser
from labels.model.indexables import IndexedDict, IndexedList  # noqa: TC001
from labels.model.package import Package
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.cpp.package import new_conan_lock_dep
from labels.parsers.collection.json import parse_json_with_tree_sitter


def parse_conan_lock(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages = []
    conan_file = cast(
        "IndexedDict[str, IndexedList[str]]",
        parse_json_with_tree_sitter(reader.read_closer.read()),
    )
    for index, dep_line in enumerate(conan_file.get("requires", [])):
        location = deepcopy(reader.location)
        if location.coordinates:
            location.coordinates.line = (
                conan_file["requires"]
                .get_position(
                    index,
                )
                .start.line
            )
        packages.append(
            new_conan_lock_dep(dep_line, location),
        )
    for index, dep_line in enumerate(conan_file.get("build_requires", [])):
        location = deepcopy(reader.location)
        if location.coordinates:
            location.coordinates.line = conan_file["build_requires"].get_position(index).start.line
        packages.append(
            new_conan_lock_dep(dep_line, location, is_dev=True),
        )
    return packages, []
