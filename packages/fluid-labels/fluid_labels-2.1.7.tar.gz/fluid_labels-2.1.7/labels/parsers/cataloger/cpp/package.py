import re
from copy import deepcopy

from packageurl import PackageURL

from labels.model.file import DependencyType, Location, LocationReadCloser, Scope
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.graph_parser import Graph, NId, node_to_str


def get_conan_dep_info(dep_line: str) -> tuple[str, str]:
    product, version = re.sub(r"[\"\]\[]", "", dep_line).strip().split("@")[0].split("/")
    if "," in version:
        version = re.sub(r",(?=[<>=])", " ", version).split(",")[0]
    return product, version


def build_conan_file_location(
    location: Location,
    line_number: int,
    *,
    is_dev: bool,
) -> Location:
    location = deepcopy(location)
    location.scope = Scope.DEV if is_dev else Scope.PROD
    if location.coordinates:
        location.coordinates.line = line_number
        location.dependency_type = DependencyType.DIRECT
    return location


def build_conan_file_py_location(location: Location, sourceline: int, *, is_dev: bool) -> Location:
    location.scope = Scope.DEV if is_dev else Scope.PROD
    if location.coordinates:
        c_upd = {"line": sourceline}
        l_upd = {"coordinates": location.coordinates.model_copy(update=c_upd)}
        return location.model_copy(update=l_upd)
    return location


def package_url(name: str, version: str) -> str:
    return PackageURL(
        type="conan",
        namespace="",
        name=name,
        version=version,
        qualifiers=None,
        subpath="",
    ).to_string()


def new_conan_file_py_dep(
    *,
    graph: Graph,
    node_id: NId,
    dep_info: str | None = None,
    is_dev: bool,
    location: Location,
) -> Package:
    dep_attrs = graph.nodes[node_id]
    if dep_info is None:
        dep_info = dep_attrs.get("label_text") or node_to_str(graph, node_id)
    dep_info = dep_info.replace("(", "").replace(")", "")
    product, version = get_conan_dep_info(dep_info)
    location.scope = Scope.DEV if is_dev else Scope.PROD
    dep_line = dep_attrs["label_l"]
    location = build_conan_file_py_location(location, dep_line, is_dev=is_dev)
    return Package(
        name=product,
        version=version,
        type=PackageType.ConanPkg,
        locations=[location],
        p_url=package_url(product, version),
        metadata=None,
        language=Language.CPP,
        licenses=[],
        is_dev=is_dev,
    )


def new_conan_file_dep(
    line: str,
    reader: LocationReadCloser,
    line_number: int,
    *,
    is_dev: bool,
    packages: list[Package],
) -> None:
    pkg_name, pkg_version = get_conan_dep_info(line)
    location = build_conan_file_location(reader.location, line_number, is_dev=is_dev)
    packages.append(
        Package(
            name=pkg_name,
            version=pkg_version,
            type=PackageType.ConanPkg,
            locations=[location],
            p_url=package_url(pkg_name, pkg_version),
            metadata=None,
            language=Language.CPP,
            licenses=[],
            is_dev=is_dev,
        ),
    )


def new_conan_lock_dep(
    dep_info: str,
    location: Location,
    *,
    is_dev: bool = False,
) -> Package:
    product, version = dep_info.split("/")
    version = version.split("#")[0]
    location.scope = Scope.DEV if is_dev else Scope.PROD
    return Package(
        name=product,
        version=version,
        type=PackageType.ConanPkg,
        locations=[location],
        p_url=package_url(product, version),
        metadata=None,
        language=Language.CPP,
        licenses=[],
        is_dev=is_dev,
    )
