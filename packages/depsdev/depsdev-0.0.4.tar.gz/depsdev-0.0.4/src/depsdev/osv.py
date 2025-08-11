from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from depsdev.base import BaseClient

if TYPE_CHECKING:
    from typing import Any
    from typing import Literal

    from typing_extensions import NotRequired
    from typing_extensions import TypedDict

    class OSVEvent(TypedDict):
        introduced: NotRequired[str]
        fixed: NotRequired[str]
        limit: NotRequired[str]
        lastAffected: NotRequired[str]

    class OSVRange(TypedDict):
        type: NotRequired[
            Literal[
                "UNSPECIFIED",
                "GIT",
                "SEMVER",
                "ECOSYSTEM",
            ]
        ]
        repo: NotRequired[str]
        events: NotRequired[list[OSVEvent]]

    class OSVPackage(TypedDict):
        name: NotRequired[str]
        ecosystem: NotRequired[str]
        purl: NotRequired[str]

    class OSVCredit(TypedDict):
        name: NotRequired[str]
        contact: NotRequired[list[str]]
        type: NotRequired[
            Literal[
                "UNSPECIFIED",
                "OTHER",
                "FINDER",
                "REPORTER",
                "ANALYST",
                "COORDINATOR",
                "REMEDIATION_DEVELOPER",
                "REMEDIATION_REVIEWER",
                "REMEDIATION_VERIFIER",
                "TOOL",
                "SPONSOR",
            ]
        ]

    class OSVSeverity(TypedDict):
        type: NotRequired[
            Literal[
                "UNSPECIFIED",
                "CVSS_V4",
                "CVSS_V3",
                "CVSS_V2",
            ]
        ]
        score: NotRequired[str]

    class OSVReference(TypedDict):
        type: NotRequired[
            Literal[
                "NONE",
                "WEB",
                "ADVISORY",
                "REPORT",
                "FIX",
                "PACKAGE",
                "ARTICLE",
                "EVIDENCE",
            ]
        ]
        url: NotRequired[str]

    class OSVAffected(TypedDict):
        package: NotRequired[OSVPackage]
        ranges: NotRequired[list[OSVRange]]
        versions: NotRequired[list[str]]
        ecosystemSpecific: NotRequired[dict[str, Any]]
        databaseSpecific: NotRequired[dict[str, Any]]
        severity: NotRequired[list[OSVSeverity]]

    class OSVVulnerability(TypedDict):
        id: str
        summary: str
        schemaVersion: NotRequired[str]
        published: NotRequired[str]
        modified: NotRequired[str]
        withdrawn: NotRequired[str]
        aliases: NotRequired[list[str]]
        related: NotRequired[list[str]]
        details: NotRequired[str]
        affected: NotRequired[list[OSVAffected]]
        references: NotRequired[list[OSVReference]]
        databaseSpecific: NotRequired[dict[str, Any]]
        severity: NotRequired[list[OSVSeverity]]
        credits: NotRequired[list[OSVCredit]]

    class V1VulnerabilityList(TypedDict):
        vulns: NotRequired[list[OSVVulnerability]]
        nextPageToken: NotRequired[str]

    class V1Query(TypedDict):
        commit: NotRequired[str]
        version: NotRequired[str]
        package: NotRequired[OSVPackage]
        page_token: NotRequired[str]

    #########################################

    class V1Batchquery(TypedDict):
        queries: list[V1Query]

    class QueryBatchResult(TypedDict):
        vulns: list[dict[Literal["id", "modified"], str]]
        next_page_token: NotRequired[str]

    class QueryBatchResponse(TypedDict):
        results: list[QueryBatchResult]


logger = logging.getLogger(__name__)


@dataclass
class OSVClientV1(BaseClient):
    base_url: str = "https://api.osv.dev"

    async def query(self, query: V1Query) -> V1VulnerabilityList:
        """
        Lists vulnerabilities for given package and version. May also be queried by commit hash.

        POST /v1/query
        """
        return await self._requests(method="POST", url="/v1/query", json=query)  # type:ignore[return-value]

    async def querybatch(self, query: V1Batchquery) -> QueryBatchResponse:
        """
        Query for multiple packages (by either package and version or git commit hash) at once. Returns vulnerability ids and modified field only. The response ordering will be guaranteed to match the input.

        POST /v1/querybatc
        """  # noqa: E501
        return await self._requests(method="POST", url="/v1/querybatch", json=query)  # type:ignore[return-value]

    async def get_vuln(self, vuln_id: str) -> OSVVulnerability:
        """
        Returns vulnerability information for a given vulnerability id.

        GET /v1/vulns/{id}
        """
        return await self._requests(method="GET", url=f"/v1/vulns/{self.url_escape(vuln_id)}")  # type:ignore[return-value]

    # async def import_findings(self) -> Incomplete:
    #     """
    #     Something like this:
    #     """
    #     return await self._requests(method="GET", url="/v1experimental/importfindings")

    # async def determine_version(self) -> Incomplete:
    #     """
    #     Something like this:
    #     """
    #     return await self._requests(method="POST", url="/v1experimental/determineversion")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    client = OSVClientV1()
    import asyncio
    import json

    query: V1Query = {
        "package": {"name": "jinja2", "ecosystem": "PyPI"},
        "version": "2.4.1",
    }
    loop = asyncio.get_event_loop()
    a = client.query(query)
    # a = client.get_vuln("GHSA-3mc7-4q67-w48m")
    # # {"name": "org.yaml:snakeyaml", "version": "1.19", "system": "MAVEN"}
    # a = client.query(
    #     {"package": {"name": "org.yaml:snakeyaml", "ecosystem": "MAVEN"}, "version": "1.19"}
    # )
    a = client.query({"package": {"purl": "pkg:maven/org.yaml/snakeyaml@1.19"}})

    result = loop.run_until_complete(a)
    print(json.dumps(result))  # For demonstration purposes, print the result
