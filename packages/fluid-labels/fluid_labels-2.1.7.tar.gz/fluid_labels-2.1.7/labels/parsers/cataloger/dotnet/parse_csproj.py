import logging
import re
from copy import deepcopy

from bs4 import BeautifulSoup
from packageurl import PackageURL
from pydantic import ValidationError

from labels.model.file import DependencyType, LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.utils.strings import format_exception, normalize_name

LOGGER = logging.getLogger(__name__)
PACKAGE = re.compile(r".+\\packages\\(?P<package_info>[^\s\\]*)\\.+")
DEP_INFO = re.compile(r"(?P<package_name>.*?)\.(?P<version>\d+[^\s]*)$")


def _get_version(include_info: list[str]) -> str | None:
    return next(
        (
            pkg_info.lstrip("Version=")
            for pkg_info in include_info
            if pkg_info.startswith("Version=")
        ),
        None,
    )


def format_package(
    name: str,
    version: str,
    line: int,
    reader: LocationReadCloser,
) -> Package | None:
    location = deepcopy(reader.location)
    if location.coordinates:
        location.coordinates.line = line
        location.dependency_type = DependencyType.DIRECT

    normalized_package_name = normalize_name(name, PackageType.DotnetPkg)
    p_url = PackageURL(
        type="nuget",
        namespace="",
        name=normalized_package_name,
        version=version,
        qualifiers={},
        subpath="",
    ).to_string()

    try:
        return Package(
            name=normalized_package_name,
            version=version,
            locations=[location],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url=p_url,
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


def _format_csproj_reference_deps(root: BeautifulSoup, reader: LocationReadCloser) -> list[Package]:
    packages = []
    for pkg in root.find_all("reference", recursive=True):
        if dll_path := pkg.find("hintpath"):
            package = PACKAGE.match(dll_path.text)
            if (
                package
                and (pkg_info := DEP_INFO.match(package.group("package_info")))
                and (
                    pkg := format_package(
                        str(pkg_info.group("package_name").lower()),
                        str(pkg_info.group("version")),
                        dll_path.sourceline,
                        reader,
                    )
                )
            ):
                packages.append(pkg)
        elif (include := pkg.get("include")) and (
            include_info := include.replace(" ", "").split(",")
        ):
            version = _get_version(include_info)
            if version and (
                pkg := format_package(
                    str(include_info[0]).strip(),
                    str(version),
                    pkg.sourceline,
                    reader,
                )
            ):
                packages.append(pkg)

    return packages


def parse_csproj(
    _resolver: Resolver | None,
    _env: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages: list[Package] = []
    root = BeautifulSoup(reader.read_closer.read(), features="html.parser")
    packages = [
        package
        for pkg in root.find_all("packagereference", recursive=True)
        if (
            (pkg_name := pkg.get("include"))
            and (version := pkg.get("version"))
            and (package := format_package(pkg_name, version, pkg.sourceline, reader))
        )
    ] + _format_csproj_reference_deps(root, reader)

    return packages, []
