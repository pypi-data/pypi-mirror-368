from __future__ import annotations

import itertools
import json
import logging
import os
import subprocess
import sys
from typing import TYPE_CHECKING

from packageurl import PackageURL

if TYPE_CHECKING:
    from collections.abc import Iterable

logger = logging.getLogger(__name__)


class MavenExtractor:
    @classmethod
    def extract(cls, filename: str) -> Iterable[PackageURL]:
        yield from (cls.parse_single_line(x) for x in cls._clean(cls._get_source(filename)))

    @staticmethod
    def _get_source(filename: str) -> Iterable[str]:
        """
        Read lines from stdin or a file.
        """
        if not filename.endswith("pom.xml"):
            logger.error("Invalid POM file: %s. It should end with 'pom.xml'.", filename)
            raise SystemExit(1)
        result = subprocess.run(
            ["mvn", "dependency:tree"],  # noqa: S607
            check=False,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(filename)),
        )
        if result.returncode != 0:
            print(result.stderr, file=sys.stderr)
            raise SystemExit(1)
        yield from result.stdout.splitlines()

    @staticmethod
    def parse_single_line(line: str) -> PackageURL:
        """
        Parse a single line of Maven dependency output and return a PackageURL object.
        """
        package, *rest = line.split()
        _is_optional = bool(rest)
        group, artifact, _type, version, *classifier = package.split(":")
        return PackageURL(
            type="maven",
            namespace=group,
            name=artifact,
            version=version,
            qualifiers=None,
            subpath=None,
        )

    @staticmethod
    def _clean(lines: Iterable[str]) -> Iterable[str]:
        stage1 = (x.rstrip() for x in lines if x.strip())
        stage2 = itertools.dropwhile(lambda x: not x.startswith("[INFO] --- "), stage1)
        stage3 = itertools.takewhile(
            lambda x: not x.startswith(
                "[INFO] ------------------------------------------------------------------------"
            ),
            stage2,
        )
        stage4 = itertools.islice(stage3, 1, None)  # Skip the first line
        stage5 = (x[7:] for x in stage4)
        yield from (x.split("- ", maxsplit=1)[-1] for x in stage5)


class PipfileLockExtractor:
    @classmethod
    def extract(cls, filename: str) -> Iterable[PackageURL]:
        """
        Extracts package URLs from a Pipfile.lock.
        """
        if not filename.endswith("Pipfile.lock"):
            logger.error("Invalid Pipfile.lock: %s. It should end with 'Pipfile.lock'.", filename)
            raise SystemExit(1)
        with open(filename) as f:
            data = json.load(f)
            for package_name, package_info in data.get("default", {}).items():
                version: str | None = package_info.get("version")
                if version:
                    yield PackageURL(
                        type="pypi",
                        namespace=None,
                        name=package_name,
                        version=version[2:],
                        qualifiers=None,
                        subpath=None,
                    )
                else:
                    logger.warning("Package %s has no version specified.", package_name)


class RequirementsExtractor:
    @classmethod
    def extract(cls, filename: str) -> Iterable[PackageURL]:
        """
        Extracts package URLs from a requirements.txt file.
        """
        if not filename.endswith("requirements.txt"):
            logger.error(
                "Invalid requirements file: %s. It should end with 'requirements.txt'.", filename
            )
            raise SystemExit(1)
        with open(filename) as f:
            for line in f:
                _line = line.strip()
                if not _line or _line.startswith(("#", "-r ", "-i ")):
                    continue
                parts = _line.split(";")[0].split("==")
                if len(parts) == 2:  # noqa: PLR2004
                    name, version = parts
                    yield PackageURL(
                        type="pypi",
                        namespace=None,
                        name=name,
                        version=version,
                        qualifiers=None,
                        subpath=None,
                    )


def get_extractor(filename: str) -> MavenExtractor | PipfileLockExtractor | RequirementsExtractor:
    """
    Returns the appropriate extractor based on the file extension.
    """
    if filename.endswith("pom.xml"):
        return MavenExtractor()
    if filename.endswith("Pipfile.lock"):
        return PipfileLockExtractor()
    if filename.endswith("requirements.txt"):
        return RequirementsExtractor()
    logger.error("Unsupported file format: %s", filename)
    raise SystemExit(1)
