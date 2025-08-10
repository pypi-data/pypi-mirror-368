from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Optional
from typing import Union

from depsdev.v3 import DepsDevClientV3
from depsdev.v3 import HashType
from depsdev.v3 import Incomplete
from depsdev.v3 import System
from depsdev.v3 import url_escape

if TYPE_CHECKING:
    from typing_extensions import Literal
    from typing_extensions import TypedDict

    class PurlDict(TypedDict):
        system: System | SystemLiteral
        name: str
        version: str

    SystemLiteral = Literal[
        "GO",
        "RUBYGEMS",
        "NPM",
        "CARGO",
        "MAVEN",
        "PYPI",
        "NUGET",
    ]

PUrlStr = str
PUrlWithVersionStr = str


class DepsDevClientV3Alpha(DepsDevClientV3):
    async def get_package(self, system: System, name: str) -> Incomplete:
        """
        GetPackage returns information about a package, including a list of its available versions, with the default version marked if known.

        GET /v3alpha/systems/{packageKey.system}/packages/{packageKey.name}
        """  # noqa: E501
        return await self._requests(
            method="GET", url=f"/v3alpha/systems/{system}/packages/{url_escape(name)}"
        )

    async def get_version(self, system: System, name: str, version: str) -> Incomplete:
        """
        GetVersion returns information about a specific package version, including its licenses and any security advisories known to affect it.

        GET /v3alpha/systems/{versionKey.system}/packages/{versionKey.name}/versions/{versionKey.version}
        """  # noqa: E501
        return await self._requests(
            method="GET",
            url=f"/v3alpha/systems/{system}/packages/{url_escape(name)}/versions/{url_escape(version)}",
        )

    async def get_version_batch(
        self,
        requests: list[PurlDict],
        page_token: Optional[str] = None,  # noqa: UP045
    ) -> Incomplete:
        """
        GetVersionBatch performs GetVersion requests for a batch of versions. Large result sets may be paginated.

        POST /v3alpha/versionbatch
        """  # noqa: E501
        payload = {
            "requests": [{"versionKey": x} for x in requests],
            "pageToken": page_token,
        }
        return await self._requests(method="POST", url="/v3alpha/versionbatch", json=payload)

    async def get_requirements(self, system: System, name: str, version: str) -> Incomplete:
        """
        GetRequirements returns the requirements for a given version in a system-specific format. Requirements are currently available for Maven, npm, NuGet, and RubyGems.

        Requirements are the dependency constraints specified by the version.

        GET /v3alpha/systems/{versionKey.system}/packages/{versionKey.name}/versions/{versionKey.version}:requirements
        """  # noqa: E501
        return await self._requests(
            method="GET",
            url=f"/v3alpha/systems/{system}/packages/{url_escape(name)}/versions/{url_escape(version)}:requirements",
        )

    async def get_dependencies(self, system: System, name: str, version: str) -> Incomplete:
        """
        GetDependencies returns a resolved dependency graph for the given package version. Dependencies are currently available for Go, npm, Cargo, Maven and PyPI.

        Dependencies are the resolution of the requirements (dependency constraints) specified by a version.

        The dependency graph should be similar to one produced by installing the package version on a generic 64-bit Linux system, with no other dependencies present. The precise meaning of this varies from system to system.

        GET /v3alpha/systems/{versionKey.system}/packages/{versionKey.name}/versions/{versionKey.version}:dependencies
        """  # noqa: E501
        return await self._requests(
            method="GET",
            url=f"/v3alpha/systems/{system}/packages/{url_escape(name)}/versions/{url_escape(version)}:dependencies",
        )

    async def get_dependents(self, system: System, name: str, version: str) -> Incomplete:
        """
        GetDependents returns information about the number of distinct packages known to depend on the given package version. Dependent counts are currently available for Go, npm, Cargo, Maven and PyPI.

        Dependent counts are derived from the dependency graphs computed by deps.dev, which means that only public dependents are counted. As such, dependent counts should be treated as indicative of relative popularity rather than precisely accurate.

        GET /v3alpha/systems/{versionKey.system}/packages/{versionKey.name}/versions/{versionKey.version}:dependents
        """  # noqa: E501
        return await self._requests(
            method="GET",
            url=f"/v3alpha/systems/{system}/packages/{url_escape(name)}/versions/{url_escape(version)}:dependents",
        )

    async def get_capabilities(self, system: System, name: str, version: str) -> Incomplete:
        """
        GetCapabilityRequest returns counts for direct and indirect calls to Capslock capabilities for a given package version. Currently only available for Go.

        GET /v3alpha/systems/{versionKey.system}/packages/{versionKey.name}/versions/{versionKey.version}:capabilities
        """  # noqa: E501
        return await self._requests(
            method="GET",
            url=f"/v3alpha/systems/{system}/packages/{url_escape(name)}/versions/{url_escape(version)}:capabilities",
        )

    async def get_project(self, project_id: str) -> Incomplete:
        """
        GetProject returns information about projects hosted by GitHub, GitLab, or BitBucket, when known to us.

        GET /v3alpha/projects/{projectKey.id}
        """  # noqa: E501
        return await self._requests(method="GET", url=f"/v3alpha/projects/{url_escape(project_id)}")

    async def get_project_batch(
        self,
        project_ids: list[str],
        page_token: Optional[str] = None,  # noqa: UP045
    ) -> Incomplete:
        """
        GetProjectBatch performs GetProjectBatch requests for a batch of projects. Large result sets may be paginated.

        POST /v3alpha/projectbatch
        """  # noqa: E501
        payload = {
            "requests": [{"projectKey": {"id": x}} for x in project_ids],
            "pageToken": page_token,
        }
        return await self._requests(method="POST", url="/v3alpha/projectbatch", json=payload)

    async def get_project_package_versions(self, project_id: str) -> Incomplete:
        """
        GetProjectPackageVersions returns known mappings between the requested project and package versions. At most 1500 package versions are returned. Mappings which were derived from attestations are served first.

        GET /v3alpha/projects/{projectKey.id}:packageversions
        """  # noqa: E501
        return await self._requests(
            method="GET", url=f"/v3alpha/projects/{url_escape(project_id)}:packageversions"
        )

    async def get_advisory(self, advisory_id: str) -> Incomplete:
        """
        GetAdvisory returns information about security advisories hosted by OSV.

        GET /v3alpha/advisories/{advisoryKey.id}
        """
        return await self._requests(
            method="GET", url=f"/v3alpha/advisories/{url_escape(advisory_id)}"
        )

    async def get_similarly_named_packages(self, system: System, name: str) -> Incomplete:
        """
        GetSimilarlyNamedPackages returns packages with names that are similar to the requested package. This similarity relation is computed by deps.dev.

        GET /v3alpha/systems/{packageKey.system}/packages/{packageKey.name}:similarlyNamedPackages
        """  # noqa: E501
        return await self._requests(
            method="GET",
            url=f"/v3alpha/systems/{system}/packages/{url_escape(name)}:similarlyNamedPackages",
        )

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

        GET /v3alpha/query
        """  # noqa: E501
        params = {
            "hash.type": hash_type.value if hash_type else None,
            "hash.value": hash_value,
            "versionKey.system": system.value if system else None,
            "versionKey.name": name,
            "versionKey.version": version,
        }
        params = {k: v for k, v in params.items() if v is not None}  # Filter out None values
        return await self._requests(method="GET", url="/v3alpha/query", params=params)  # type: ignore[arg-type,unused-ignore]

    async def purl_lookup(self, purl: Union[PUrlStr, PUrlWithVersionStr]) -> Incomplete:  # noqa: UP007
        """
        PurlLookup searches for a package or package version specified via purl, and returns the corresponding result from GetPackage or GetVersion as appropriate.

        For a package lookup, the purl should be in the form pkg:type/namespace/name for a namespaced package name, or pkg:type/name for a non-namespaced package name.

        For a package version lookup, the purl should be in the form pkg:type/namespace/name@version, or pkg:type/name@version.

        Extra fields in the purl must be empty, otherwise the request will fail. In particular, there must be no subpath or qualifiers.

        Supported values for type are cargo, gem, golang, maven, npm, nuget, and pypi. Further details on types, and how to form purls of each type, can be found in the purl spec.

        Special characters in purls must be percent-encoded. This is described in detail by the purl spec.

        GET /v3alpha/purl/{purl}
        """  # noqa: E501
        return await self._requests(method="GET", url=f"/v3alpha/purl/{url_escape(purl)}")

    async def purl_lookup_batch(
        self,
        purls: list[PUrlWithVersionStr],
        page_token: Optional[str] = None,  # noqa: UP045
    ) -> Incomplete:
        """
        PurlLookupBatch performs PurlLookup requests for a batch of purls. This endpoint only supports version lookups. Purls in requests must include a version field.

        Supported purl forms are pkg:type/namespace/name@version for a namespaced package name, or pkg:type/name@version for a non-namespaced package name.

        Extra fields in the purl must be empty, otherwise the request will fail. In particular, there must be no subpath or qualifiers.

        Large result sets may be paginated.

        POST /v3alpha/purlbatch
        """  # noqa: E501
        payload = {"requests": [{"purl": x} for x in purls], "pageToken": page_token}
        return await self._requests(method="POST", url="/v3alpha/purlbatch", json=payload)

    async def query_container_images(self, chain_id: str) -> Incomplete:
        """
        QueryContainerImages searches for container image repositories on DockerHub that match the requested OCI Chain ID. At most 1000 image repositories are returned.

        An image repository is identifier (eg. 'tensorflow') that refers to a collection of images.

        An OCI Chain ID is a hashed encoding of an ordered sequence of OCI layers. For further details see the OCI Chain ID spec.

        GET /v3alpha/querycontainerimages/{chainId}
        """  # noqa: E501
        return await self._requests(
            method="GET", url=f"/v3alpha/querycontainerimages/{url_escape(chain_id)}"
        )


if __name__ == "__main__":
    import asyncio

    async def main() -> None:
        client = DepsDevClientV3Alpha()
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

        print(
            await client.get_version_batch(
                [
                    {"system": "NPM", "name": "@colors/colors", "version": "1.5.0"},
                    {"system": "NUGET", "name": "castle.core", "version": "5.1.1"},
                ]
            )
        )
        print(await client.get_dependents(system, name, version))
        # print(await client.get_capabilities(system, name, version))
        print(
            await client.get_project_batch(
                ["github.com/facebook/react", "github.com/angular/angular"]
            )
        )

        purl1 = "pkg:npm/@colors/colors"
        purl2 = "pkg:npm/@colors/colors@1.5.0"
        print(await client.get_similarly_named_packages(system, name))
        print(await client.purl_lookup(purl1))
        print(await client.purl_lookup_batch([purl2]))
        # print(await client.query_container_images(""))

    asyncio.run(main())
