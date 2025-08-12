import logging
import sqlite3
from typing import Any

from labels.advisories.database import BaseDatabase
from labels.advisories.match_versions import match_vulnerable_versions
from labels.advisories.utils import create_advisory_from_record
from labels.model.advisories import Advisory

LOGGER = logging.getLogger(__name__)


class ImagesDatabase(BaseDatabase):
    def __init__(self) -> None:
        super().__init__(db_name="skims_sca_advisories_for_images.db")


DATABASE = ImagesDatabase()


def fetch_advisory_from_database(
    cursor: sqlite3.Cursor,
    package_manager: str,
    platform_version: str,
    package_name: str,
) -> list[Any]:
    cursor.execute(
        """
        SELECT
            adv_id,
            source,
            vulnerable_version,
            severity_level,
            severity,
            severity_v4,
            epss,
            details,
            percentile,
            cwe_ids,
            cve_finding,
            auto_approve
        FROM advisories
        WHERE package_manager = ? AND platform_version = ? AND package_name = ?;
        """,
        (package_manager, platform_version, package_name),
    )
    return cursor.fetchall()


def get_package_advisories(
    package_manager: str,
    package_name: str,
    version: str,
    platform_version: str,
) -> list[Advisory]:
    connection = DATABASE.get_connection()
    cursor = connection.cursor()

    return [
        adv
        for record in fetch_advisory_from_database(
            cursor,
            package_manager,
            platform_version,
            package_name,
        )
        if (adv := create_advisory_from_record(record, package_manager, package_name, version))
    ]


def get_vulnerabilities(
    platform: str,
    product: str,
    version: str,
    platform_version: str | None,
) -> list[Advisory]:
    vulnerabilities = []
    if (
        product
        and version
        and platform_version
        and (
            advisories := get_package_advisories(
                platform,
                product.lower(),
                version,
                platform_version,
            )
        )
    ):
        vulnerabilities = [
            advisor
            for advisor in advisories
            if match_vulnerable_versions(version.lower(), advisor.vulnerable_version)
        ]

    return vulnerabilities
