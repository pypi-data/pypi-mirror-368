#     The Certora Prover
#     Copyright (C) 2025  Certora Ltd.
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, version 3 of the License.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Shared helpers for Rust-based targets (Solana & Soroban).

Placing the build  logic in one module removes
duplication from the dedicated entry scripts.
"""

from __future__ import annotations

import sys
from pathlib import Path

scripts_dir_path = Path(__file__).parent.parent.resolve()  # containing directory
sys.path.insert(0, str(scripts_dir_path))

import time
import logging
from typing import Dict

from Shared import certoraUtils as Util

from CertoraProver.certoraContextClass import CertoraContext

from CertoraProver.certoraBuildRust import set_rust_build_directory


log = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #

def build_rust_project(context: CertoraContext, timings: Dict) -> None:
    """
    Compile the Rust artefact and record elapsed time in *timings*.

    Args:
        context: The CertoraContext object containing the configuration.
        timings: A dictionary to store timing information.
    """
    log.debug("Build Rust target")
    start = time.perf_counter()
    set_rust_build_directory(context)
    timings["buildTime"] = round(time.perf_counter() - start, 4)
    if context.test == str(Util.TestValue.AFTER_BUILD):
        raise Util.TestResultsReady(context)
