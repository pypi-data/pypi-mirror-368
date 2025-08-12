from pydantic import BaseModel

AdvisoryRecord = tuple[
    str,  # id
    str,  # source
    str,  # vulnerable_version
    str | None,  # severity_level
    str | None,  # severity
    str | None,  # severity_v4
    str | None,  # epss
    str | None,  # details
    str | None,  # percentile
    str | None,  # cwe_ids
    str | None,  # cve_finding
    int,  # auto_approve
]


class Advisory(BaseModel):
    id: str
    vulnerable_version: str
    source: str
    package_manager: str
    cpes: list[str]
    severity_level: str = "Low"
    details: str | None = None
    epss: float = 0.0
    percentile: float = 0.0
    severity: str | None = None
    severity_v4: str | None = None
    cwe_ids: list[str] | None = None
    cve_finding: str | None = None
    auto_approve: bool = False
