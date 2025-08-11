from __future__ import annotations

import asyncio
import itertools
import logging
from typing import TYPE_CHECKING

from rich.console import Console
from rich.table import Table

from depsdev.osv import OSVClientV1

if TYPE_CHECKING:
    from depsdev.osv import OSVVulnerability
    from depsdev.osv import V1Query

logger = logging.getLogger(__name__)


def get_version_fix(vuln: OSVVulnerability) -> str | None:
    for affected in vuln.get("affected", []):
        for _range in affected.get("ranges", []):
            for event in _range.get("events", []):
                if "fixed" in event:
                    return event["fixed"]
    return None


async def get_vulns(purls: list[str], osv_client: OSVClientV1) -> dict[str, list[OSVVulnerability]]:
    queries: list[V1Query] = [
        {
            "package": {"purl": purl},
        }
        for purl in purls
    ]
    result = await osv_client.querybatch({"queries": queries})
    r = {k: [x["id"] for x in v["vulns"]] for k, v in zip(purls, result["results"]) if v}
    all_result = await asyncio.gather(
        *[osv_client.get_vuln(vuln_id) for vuln_id in itertools.chain.from_iterable(r.values())]
    )
    look_up = {vuln["id"]: vuln for vuln in all_result}
    return {purl: [look_up[vuln_id] for vuln_id in vuln_ids] for purl, vuln_ids in r.items()}


async def main_helper(packages: list[str]) -> int:
    """Main function to analyze packages for vulnerabilities."""

    console = Console()

    console.print(f"Analysing {len(packages)} packages...")

    osv_client = OSVClientV1()

    results = await get_vulns(packages, osv_client)
    console.print(f"Found {len(results)} packages with advisories.")

    for purl, advisories in results.items():
        table = Table(title=purl)

        table.add_column("Id")
        table.add_column("Summary", style="cyan", no_wrap=True)
        table.add_column("Fixed", style="magenta")

        for vuln in advisories:
            table.add_row(
                f"[link=https://github.com/advisories/{vuln['id']}]{vuln['id']}[/link]",
                vuln["summary"],
                get_version_fix(vuln) or "unknown",
            )
        console.print(table)
    return 0
