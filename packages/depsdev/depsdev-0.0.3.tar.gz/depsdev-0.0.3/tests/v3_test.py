import pytest

from depsdev.v3 import DepsDevClientV3
from depsdev.v3 import System


@pytest.mark.asyncio
async def test_all() -> None:
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
