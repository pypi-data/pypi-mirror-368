import pytest

from depsdev.v3 import System
from depsdev.v3alpha import DepsDevClientV3Alpha


@pytest.mark.asyncio
async def test_all() -> None:
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
        await client.get_project_batch(["github.com/facebook/react", "github.com/angular/angular"])
    )

    purl1 = "pkg:npm/@colors/colors"
    purl2 = "pkg:npm/@colors/colors@1.5.0"
    print(await client.get_similarly_named_packages(system, name))
    print(await client.purl_lookup(purl1))
    print(await client.purl_lookup_batch([purl2]))
    # print(await client.query_container_images(""))
