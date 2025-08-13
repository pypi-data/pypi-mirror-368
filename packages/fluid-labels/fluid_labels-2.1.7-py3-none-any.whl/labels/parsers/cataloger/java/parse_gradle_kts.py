import logging
import re
from copy import deepcopy

from pydantic import BaseModel, ValidationError

from labels.model.file import Location, LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.java.model import JavaArchive, JavaPomProject
from labels.parsers.cataloger.java.package import package_url
from labels.utils.strings import format_exception

LOGGER = logging.getLogger(__name__)
# Constants
QUOTE = r'["\']'
NL = r"(\n?\s*)?"
TEXT = r"[a-zA-Z0-9._-]+"
RE_GRADLE_KTS: re.Pattern[str] = re.compile(
    rf"(runtimeOnly|api|compile|plugin|compileOnly|implementation)\({QUOTE}"
    rf"(?P<group>{TEXT}):(?P<name>{TEXT}):"
    rf"(?P<version>{TEXT})"
    rf"(?::(?P<classifier>{TEXT}))?"
    rf"{QUOTE}\)",
)


def is_comment(line: str) -> bool:
    return (
        line.strip().startswith("//")
        or line.strip().startswith("/*")
        or line.strip().endswith("*/")
    )


class LockFileDependency(BaseModel):
    group: str
    name: str
    version: str
    line: int | None = None


def parse_gradle_lockfile_kts(
    _resolver: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    dependencies = parse_dependencies(reader)
    packages = create_packages(dependencies, reader.location)
    return packages, []


def parse_dependencies(reader: LocationReadCloser) -> list[LockFileDependency]:
    dependencies: list[LockFileDependency] = []
    is_block_comment = False

    for line_no, raw_line in enumerate(reader.read_closer.readlines(), start=1):
        line = raw_line.strip()
        is_block_comment = update_block_comment_status(line, is_block_comment=is_block_comment)

        if is_block_comment or is_comment(line):
            continue

        dependency = extract_dependency(line, line_no)
        if dependency:
            dependencies.append(dependency)

    return dependencies


def update_block_comment_status(line: str, *, is_block_comment: bool) -> bool:
    if "/*" in line:
        return True
    if "*/" in line:
        return False
    return is_block_comment


def extract_dependency(line: str, line_no: int) -> LockFileDependency | None:
    if match := RE_GRADLE_KTS.match(line):
        version = match.group("version")
        if version:
            return LockFileDependency(
                group=match.group("group"),
                name=match.group("name"),
                version=version,
                line=line_no,
            )

    return None


def create_packages(
    dependencies: list[LockFileDependency],
    reader_location: Location,
) -> list[Package]:
    packages: list[Package] = []

    for dependency in dependencies:
        name = dependency.name
        version = dependency.version

        if not name or not version:
            continue

        location = deepcopy(reader_location)
        if location.coordinates:
            location.coordinates.line = dependency.line

        archive = create_java_archive(dependency, name, version)

        package = create_package(name, version, location, archive, dependency.group)
        if package:
            packages.append(package)

    return packages


def create_java_archive(
    dependency: LockFileDependency,
    name: str,
    version: str,
) -> JavaArchive:
    return JavaArchive(
        pom_project=JavaPomProject(
            group_id=dependency.group,
            name=name,
            artifact_id=name,
            version=version,
        ),
    )


def create_package(
    name: str,
    version: str,
    location: Location,
    archive: JavaArchive,
    group: str,
) -> Package | None:
    try:
        return Package(
            name=f"{group}:{name}",
            version=version,
            locations=[location],
            language=Language.JAVA,
            type=PackageType.JavaPkg,
            metadata=archive,
            p_url=package_url(name, version, archive),
            licenses=[],
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
        return None
