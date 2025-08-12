import logging
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


def parse_dotnet_pkgs_config(
    _resolver: Resolver | None,
    _env: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    root = BeautifulSoup(reader.read_closer.read(), features="html.parser")
    packages = []

    for pkg in root.find_all("package", recursive=True):
        name: str | None = pkg.get("id")
        version: str | None = pkg.get("version")

        if not name or not version:
            continue

        line = pkg.sourceline
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
            packages.append(
                Package(
                    name=normalized_package_name,
                    version=version,
                    locations=[location],
                    language=Language.DOTNET,
                    licenses=[],
                    type=PackageType.DotnetPkg,
                    metadata=None,
                    p_url=p_url,
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

    return packages, []
