# SPDX-FileCopyrightText: 2025 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

"""Holds methods to check installed version of Java."""

import logging as log
import re
import shutil
import subprocess

from amirispy.source.exception import AMIRISError
from amirispy.source.logs import log_critical

_ERR_NO_JAVA = "No Java installation found. See {} for further instructions."
_ERR_JAVA_VERSION = "Local Java version '{}' does not match requirements '>{}'."
_URL_INSTALLATION_INSTRUCTIONS = "https://gitlab.com/dlr-ve/esy/amiris/amiris-py#further-requirements"

JAVA_VERSION_PATTERN = '"(\d+\.\d+).*"'  # noqa
JAVA_VERSION_MINIMUM = 11


def check_java_installation(raise_exception: bool = False) -> None:
    """Checks if the java command is available.

    Args:
        raise_exception: if True, an Exception is raised, else a warning

    Raises:
        AMIRISError: if Java installation is not found; logged with level "WARNING" (default) or "CRITICAL"
    """
    if not shutil.which("java"):
        if raise_exception:
            raise log_critical(AMIRISError(_ERR_NO_JAVA.format(_URL_INSTALLATION_INSTRUCTIONS)))
        log.warning(_ERR_NO_JAVA.format(_URL_INSTALLATION_INSTRUCTIONS))


def check_java_version(raise_exception: bool = False) -> None:
    """Checks if Java version is compatible with requirements of FAME.

    Args:
        raise_exception: if True, an Exception is raised, else a warning

     Raises:
        AMIRISError: if Java version is not compatible; logged with level "WARNING" (default) or "CRITICAL"
    """
    version_raw = subprocess.check_output(["java", "-version"], stderr=subprocess.STDOUT)
    version_number = re.search(JAVA_VERSION_PATTERN, str(version_raw)).groups()[0]

    if float(version_number) < JAVA_VERSION_MINIMUM:
        if raise_exception:
            raise log_critical(AMIRISError(_ERR_JAVA_VERSION.format(version_number, JAVA_VERSION_MINIMUM)))
        log.warning(_ERR_JAVA_VERSION.format(version_number, JAVA_VERSION_MINIMUM))


def check_java(skip: bool) -> None:
    """Checks both Java installation and version if not `skip`.

    Args:
        skip: if enabled, checks are skipped

    Raises:
          AMIRISError: if any check fails; logged with level "CRITICAL"
    """
    if not skip:
        check_java_installation(raise_exception=True)
        check_java_version(raise_exception=True)
