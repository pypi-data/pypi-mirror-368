from __future__ import annotations

import logging
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import TYPE_CHECKING
from typing import Optional
from urllib.parse import quote

import httpx

if TYPE_CHECKING:
    from httpx._types import QueryParamTypes
    from typing_extensions import Literal

logger = logging.getLogger(__name__)
Incomplete = object


class HashType(str, Enum):
    MD5 = "MD5"
    SHA1 = "SHA1"
    SHA256 = "SHA256"
    SHA512 = "SHA512"


class System(str, Enum):
    GO = "GO"
    RUBYGEMS = "RUBYGEMS"
    NPM = "NPM"
    CARGO = "CARGO"
    MAVEN = "MAVEN"
    PYPI = "PYPI"
    NUGET = "NUGET"


def url_escape(string: str) -> str:
    return quote(string, safe="")


@dataclass
class DepsDevClientV3:
    client: httpx.AsyncClient = field(init=False)
    timeout: float = 5.0
    base_url: str = "https://api.deps.dev"

    def __post_init__(self) -> None:
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)

    async def _requests(
        self,
        url: str = "",
        method: Literal["GET", "POST"] = "GET",
        params: QueryParamTypes | None = None,
        json: object | None = None,
    ) -> Incomplete:
        response = await self.client.request(method=method, url=url, params=params, json=json)
        if not response.is_success:
            logger.error(
                "Request failed with status code %s: %s", response.status_code, response.text
            )
            response.raise_for_status()
        return response.json()

    async def get_package(self, system: System, name: str) -> Incomplete:
        """
        GetPackage returns information about a package, including a list of its available versions, with the default version marked if known.

        GET /v3/systems/{packageKey.system}/packages/{packageKey.name}
        """  # noqa: E501
        return await self._requests(
            method="GET", url=f"/v3/systems/{system}/packages/{url_escape(name)}"
        )

    async def get_version(self, system: System, name: str, version: str) -> Incomplete:
        """
        GetVersion returns information about a specific package version, including its licenses and any security advisories known to affect it.

        GET /v3/systems/{versionKey.system}/packages/{versionKey.name}/versions/{versionKey.version}
        """  # noqa: E501
        return await self._requests(
            method="GET",
            url=f"/v3/systems/{system}/packages/{url_escape(name)}/versions/{url_escape(version)}",
        )

    async def get_requirements(self, system: System, name: str, version: str) -> Incomplete:
        """
        GetRequirements returns the requirements for a given version in a system-specific format. Requirements are currently available for Maven, npm, NuGet and RubyGems.

        Requirements are the dependency constraints specified by the version.

        GET /v3/systems/{versionKey.system}/packages/{versionKey.name}/versions/{versionKey.version}:requirements
        """  # noqa: E501
        return await self._requests(
            method="GET",
            url=f"/v3/systems/{system}/packages/{url_escape(name)}/versions/{url_escape(version)}:requirements",
        )

    async def get_dependencies(self, system: System, name: str, version: str) -> Incomplete:
        """
        GetDependencies returns a resolved dependency graph for the given package version. Dependencies are currently available for Go, npm, Cargo, Maven and PyPI.

        Dependencies are the resolution of the requirements (dependency constraints) specified by a version.

        The dependency graph should be similar to one produced by installing the package version on a generic 64-bit Linux system, with no other dependencies present. The precise meaning of this varies from system to system.

        GET /v3/systems/{versionKey.system}/packages/{versionKey.name}/versions/{versionKey.version}:dependencies
        """  # noqa: E501
        return await self._requests(
            method="GET",
            url=f"/v3/systems/{system}/packages/{url_escape(name)}/versions/{url_escape(version)}:dependencies",
        )

    async def get_project(self, project_id: str) -> Incomplete:
        """
        GetProject returns information about projects hosted by GitHub, GitLab, or BitBucket, when known to us.

        GET /v3/projects/{projectKey.id}
        """  # noqa: E501
        return await self._requests(method="GET", url=f"/v3/projects/{url_escape(project_id)}")

    async def get_project_package_versions(self, project_id: str) -> Incomplete:
        """
        GetProjectPackageVersions returns known mappings between the requested project and package versions. At most 1500 package versions are returned. Mappings which were derived from attestations are served first.

        GET /v3/projects/{projectKey.id}:packageversions
        """  # noqa: E501
        return await self._requests(
            method="GET", url=f"/v3/projects/{url_escape(project_id)}:packageversions"
        )

    async def get_advisory(self, advisory_id: str) -> Incomplete:
        """
        GetAdvisory returns information about security advisories hosted by OSV.

        GET /v3/advisories/{advisoryKey.id}
        """
        return await self._requests(method="GET", url=f"/v3/advisories/{url_escape(advisory_id)}")

    async def query(
        self,
        hash_type: Optional[HashType] = None,  # noqa: UP045
        hash_value: Optional[str] = None,  # noqa: UP045
        system: Optional[System] = None,  # noqa: UP045
        name: Optional[str] = None,  # noqa: UP045
        version: Optional[str] = None,  # noqa: UP045
    ) -> Incomplete:
        """
        Query returns information about multiple package versions, which can be specified by name, content hash, or both. If a hash was specified in the request, it returns the artifacts that matched the hash.

        Querying by content hash is currently supported for npm, Cargo, Maven, NuGet, PyPI and RubyGems. It is typical for hash queries to return many results; hashes are matched against multiple release artifacts (such as JAR files) that comprise package versions, and any given artifact may appear in several package versions.

        GET /v3/query
        """  # noqa: E501
        params = {
            "hash.type": hash_type.value if hash_type else None,
            "hash.value": hash_value,
            "versionKey.system": system.value if system else None,
            "versionKey.name": name,
            "versionKey.version": version,
        }
        params = {k: v for k, v in params.items() if v is not None}  # Filter out None values
        return await self._requests(method="GET", url="/v3/query", params=params)  # type: ignore[arg-type,unused-ignore]


if __name__ == "__main__":
    import asyncio

    async def main() -> None:
        client = DepsDevClientV3()
        system = System.NPM
        name = "@colors/colors"
        version = "1.5.0"
        project_id = "github.com/facebook/react"
        advisory_id = "GHSA-2qrg-x229-3v8q"
        print(await client.get_package(system, name))
        print(await client.get_version(system, name, version))
        print(await client.get_requirements(system, name, version))
        print(await client.get_dependencies(system, name, version))
        print(await client.get_project(project_id))
        print(await client.get_project_package_versions(project_id))
        print(await client.get_advisory(advisory_id))
        print(
            await client.query(
                system=System.NPM,
                name="react",
                version="18.2.0",
            )
        )

    asyncio.run(main())
