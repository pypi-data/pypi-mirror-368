#  Copyright Femtosense 2024
#
#  By using this software package, you agree to abide by the terms and conditions
#  in the license agreement found at https://femtosense.ai/legal/eula/
#

from .fd_dataclasses import CompiledData
from .spu_runner import SPURunner, FakeSPURunner
from .plugins.femtofile_export import FemtoFile
from .femtodrive import Femtodriver


def _get_dir():
    import pathlib

    return pathlib.Path(__file__).parent.resolve()


__version__ = (_get_dir() / "VERSION").read_text(encoding="utf-8").strip()

# PEP 8 definiton of public API
# https://peps.python.org/pep-0008/#public-and-internal-interfaces
__all__ = ["Femtodriver", "CompiledData"]
