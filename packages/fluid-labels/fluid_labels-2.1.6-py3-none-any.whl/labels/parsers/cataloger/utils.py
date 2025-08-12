from urllib.parse import parse_qs

from labels.model.release import Release

PURL_QUALIFIER_DISTRO = "distro"


def purl_qualifiers(
    qualifiers: dict[str, str | None],
    release: Release | None = None,
) -> dict[str, str]:
    if release:
        distro_qualifiers = []
        if release.id_:
            distro_qualifiers.append(release.id_)
        if release.version_id:
            distro_qualifiers.append(release.version_id)
        elif release.build_id:
            distro_qualifiers.append(release.build_id)

        if distro_qualifiers:
            qualifiers[PURL_QUALIFIER_DISTRO] = "-".join(distro_qualifiers)

    return {
        key: qualifiers.get(key, "") or ""
        for key in sorted(qualifiers.keys())
        if qualifiers.get(key)
    }


def extract_distro_info(pkg_str: str) -> tuple[str | None, str | None, str | None]:
    parts = pkg_str.split("?", 1)
    if len(parts) != 2:
        return None, None, None

    query = parts[1]
    params = parse_qs(query)
    distro_id = params.get("distro_id", [None])[0]
    distro_version = params.get("distro_version_id", [None])[0]
    arch = params.get("arch", [None])[0]
    return distro_id, distro_version, arch
