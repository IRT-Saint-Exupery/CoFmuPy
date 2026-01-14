# -*- coding: utf-8 -*-
# Copyright 2025 IRT Saint Exupéry and HECATE European project - All rights reserved
#
# The 2-Clause BSD License
#
# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of
#    conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list
#    of conditions and the following disclaimer in the documentation and/or other
#    materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
# THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
# OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
This module provides a command-line utility to retrieve compliant HMI from its
repository. Compliance check is made thanks to API version
"""
import os
import zipfile
import logging
from pathlib import Path

import requests
from packaging.version import Version

from cofmupy.api.version import API_VERSION

# Global configuration variables
FRONTEND_REPO = "jfasquel31450/CoFmuPy-GUI"
GITHUB_API = f"https://api.github.com/repos/{FRONTEND_REPO}/releases"
DIST_DIR = Path("web/dist/cofmupy-gui")
CACHE_DIR = Path.home() / ".my-app" / "frontend-cache"
TIMEOUT = 10

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("gui-fetcher")


def github_headers():
    """
    Return github header if token defined into environment,
    otherwise return empty object.
    """
    token = os.getenv("GITHUB_TOKEN")
    if token:
        return {"Authorization": f"token {token}"}
    return {}


def api_range_contains(api_version: Version, min_v: str, max_v: str) -> bool:
    """
    Compliance check between api version and a range of versions.
    Note that max version should contain ".x" term to indicate that all sub-versions
        are compliant

    Args:
        api_version (Version): API version to check.
        min_v (str): minimum range version
        max_v (str): maximum range version

    Returns:
        boolean: true if api version is between min and max version, otherwise false.
    """
    min_v = Version(min_v)
    if max_v.endswith(".x"):
        max_v = Version(max_v.replace(".x", ".999"))
    else:
        max_v = Version(max_v)

    return min_v <= api_version <= max_v


def is_compatible(meta: dict) -> bool:
    """
    Compliance check between api version (from backend) and metadata (from HMI)

    Args:
        meta (dict): metadata from HMI that contains version range for compliance check.

    Returns:
        boolean: true if api version is compliant with given metadata, otherwise false.
    """
    compat = meta.get("api_compatibility", {})
    return api_range_contains(API_VERSION, compat["min"], compat["max"])


def fetch_frontend():
    """
    Core method that retrieve compliant Hmi version with current api version.
    It parses all release packages from Hmi repository and check compliance between
        versions. Compatible Hmi application is copied into web/dist directory. If there
        are several compatible versions, it takes the latest one.

    Returns:
        boolean: true if api version is compliant with given metadata, otherwise false.
    """
    log.info("Backend API version: %s", API_VERSION)

    r = requests.get(GITHUB_API, headers=github_headers(), timeout=TIMEOUT)
    r.raise_for_status()

    releases = r.json()

    for release in releases:
        assets = {a["name"]: a for a in release["assets"]}

        if "metadata-dist.json" not in assets:
            continue
        if "CoFmuPy-gui-dist.zip" not in assets:
            continue

        meta_url = assets["metadata-dist.json"]["browser_download_url"]
        meta = requests.get(meta_url, timeout=TIMEOUT).json()

        if not is_compatible(meta):
            continue

        tag = release["tag_name"]
        log.info("Compatible frontend found: %s", tag)

        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_zip = CACHE_DIR / f"{tag}.zip"

        if not cache_zip.exists():
            log.info("Downloading CoFmuPy-gui-dist.zip")
            zip_data = requests.get(
                assets["CoFmuPy-gui-dist.zip"]["browser_download_url"],
                headers=github_headers(),
                timeout=TIMEOUT,
            ).content
            cache_zip.write_bytes(zip_data)
        else:
            log.info("Using cached frontend build")

        if DIST_DIR.exists():
            log.info("Cleaning existing dist directory")
            for item in DIST_DIR.iterdir():
                if item.is_dir():
                    os.system(f"rm -rf {item}")
                else:
                    item.unlink()

        DIST_DIR.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(cache_zip) as z:
            z.extractall(DIST_DIR)

        log.info("Frontend installed in %s", DIST_DIR)
        return

    raise RuntimeError("No compatible frontend found for API version")


def main():
    """
    CLI entry point, no arguments expected
    """
    try:
        fetch_frontend()
    except Exception as e:
        log.error("Failed to fetch frontend: %s", e)
        raise SystemExit(1) from e
