import logging
import re
from copy import (
    deepcopy,
)

from labels.model.file import (
    DependencyType,
    Location,
    LocationReadCloser,
    Scope,
)
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import (
    Relationship,
)
from labels.model.release import Environment
from labels.model.resolver import (
    Resolver,
)
from labels.parsers.cataloger.ruby.package import (
    package_url,
)

LOGGER = logging.getLogger(__name__)

GEM_LOCK_DEP: re.Pattern[str] = re.compile(r"^\s{4}(?P<gem>[^\s]*)\s\([^\d]*(?P<version>.*)\)$")


def build_location(
    reader: LocationReadCloser,
    line_number: int,
) -> Location:
    location = deepcopy(reader.location)
    location.scope = Scope.PROD
    if location.coordinates:
        location.coordinates.line = line_number
        location.dependency_type = DependencyType.DIRECT
    return location


def parse_gemfile_lock(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages: list[Package] = []
    relationships: list[Relationship] = []
    line_gem: bool = False

    for line_number, line in enumerate(
        reader.read_closer.read().splitlines(),
        1,
    ):
        if line.startswith("GEM"):
            line_gem = True
        elif line_gem:
            if matched := GEM_LOCK_DEP.match(line):
                pkg_name = matched.group("gem")
                pkg_version = matched.group("version")
                location = build_location(reader, line_number)

                packages.append(
                    Package(
                        name=pkg_name,
                        version=pkg_version,
                        type=PackageType.GemPkg,
                        locations=[location],
                        p_url=package_url(pkg_name, pkg_version),
                        metadata=None,
                        language=Language.RUBY,
                        licenses=[],
                        is_dev=False,
                    ),
                )
            elif not line:
                break

    return packages, relationships
