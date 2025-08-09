#  Copyright Femtosense 2024
#
#  By using this software package, you agree to abide by the terms and conditions
#  in the license agreement found at https://femtosense.ai/legal/eula/
#

import logging
import os
import shutil
import zipfile
from typing import Any

import yaml

import femtodriver.util.packing as packing
from femtodriver import CompiledData
from femtodriver.typing_help import ARRAYINT, ARRAYU64, HWTARGET, IOTARGET, VARVALS

logger = logging.getLogger(__name__)

# this is the fname preamble that comes out of FX,
# also use for when we compile from FM
# it's a little odd, yeah
MEM_IMAGE_FNAME_PRE = "test"


class NullHandler:
    """used when bypassing ProgramHandler, to preserve downstream syntax"""

    def __init__(self, meta_dir):
        self.meta_dir = meta_dir
        self.fasmir = None
        self.fmir = None
        self.fqir = None
        self.compiled_data: CompiledData

    def compile(
        self, compiler: str = "null", compiler_kwargs: None = None
    ) -> tuple[None, None, None]:
        return None, None, None


class ProgramHandler:
    """This makes all the program sources and compiler outputs look the same to SPURunner

    Knows how to accept these raw program inputs:
        - FQIR
        - FASMIR
        - zipfile from previous FX run

    Produces the two necessary SPURunner ingredients
        - an extracted data dir with the memory images
        - a metadata yaml

    Can compile/extract the following ways:
        - FQIR --(FX)--> zipfile --> images + meta
        - FQIR --(FM)--> FASMIR  --> images + meta + FASMIR(for debug)
    """

    def __init__(
        self,
        fqir=None,
        fasmir=None,
        zipfile_fname=None,
        femtocrux_client=None,
        encrypt=True,
        insert_debug_stores=False,
        meta_dir="spu_runner_data",
    ):
        self.fqir = fqir
        self.fasmir = fasmir
        self.fmir = None  # can be filled in when compiling w/ FM
        self.zipfile_fname = zipfile_fname
        self.encrypt = encrypt
        self.insert_debug_stores = insert_debug_stores
        self.femtocrux_client = femtocrux_client
        self.compiled_data: CompiledData

        # this is where the outputs go
        # the runner uses the memory images and metadata here
        self.meta_dir = meta_dir

    def compile(
        self, compiler: str = "femtocrux", compiler_kwargs: dict | None = None
    ) -> tuple[CompiledData, Any, Any]:
        """
        Compile the model to get fasmir and CompiledData and optionally fmir
        """
        if compiler_kwargs is None:
            compiler_kwargs = {}
        # don't have a finished product, need to compile
        if self.fasmir is None and self.zipfile_fname is None:
            if self.fqir is None:
                raise ValueError("compilation must start with FQIR")

            if compiler == "femtocrux":
                self.zipfile_fname = "fx_compiled.zip"  # we will create this zipfile
                self.compiled_data = self._compile_with_fx_to_zipfile(
                    compiler_kwargs=compiler_kwargs
                )

            elif compiler == "femtomapper":
                self._compile_with_fm_to_fasmir(mapper_conf_kwargs=compiler_kwargs)
                self.compiled_data = self._extract_fasmir()
                # for testing, this is route FX takes
                # self.compiled_data = CompiledData.read_from_files(self.meta_dir)

        # start with already-generated FX output
        elif self.zipfile_fname is not None:
            self._extract_zipfile()
            self.compiled_data = CompiledData.read_from_files(self.meta_dir)

        # start with FASMIR object
        elif self.fasmir is not None:
            self.compiled_data = self._extract_fasmir()

        # modify the meta yaml with FQIR info
        # e.g. original shapes (for padding)
        if self.fqir is not None:
            self.compiled_data.metadata = self._add_fqir_meta()

        return self.compiled_data, self.fasmir, self.fmir

    def _compile_with_fx_to_zipfile(self, compiler_kwargs={}):
        """calls FX to turn fqir into the zipfile"""
        from femtocrux import CompilerClient, FQIRModel

        client = self.femtocrux_client

        bitstream = client.compile(
            FQIRModel(
                self.fqir,
                batch_dim=0,
                sequence_dim=1,
            ),
            options=compiler_kwargs,
        )

        compiled_data = CompiledData.read_from_zip(bitstream)
        return compiled_data

    def _extract_zipfile(self):
        """simply unpacks self.zipfile_fname into self.meta_dir"""
        with zipfile.ZipFile(self.zipfile_fname, "r") as zip_ref:
            zip_ref.extractall(self.meta_dir)

    def _compile_with_fm_to_fasmir(self, mapper_conf_kwargs={}):
        """Standard compilation sequence for FQIR, should eventually be grouped in FM"""
        try:
            from femtomapper.passman import (
                MapperConf,
                MapperState,
                PassMan,
                get_utm_inputs,
            )
        except ImportError:
            ImportError(
                "couldn't import femtomapper. This is a Femtosense-internal developer mode"
            )

        state = MapperState(fqir=self.fqir)
        conf = MapperConf(**mapper_conf_kwargs)
        passman = PassMan(conf)
        state = passman.do(state)

        self.fasmir = state.fasmir
        self.fmir = state.fmir

    @property
    def yamlfname(self):
        return os.path.join(self.meta_dir, "metadata.yaml")

    @property
    def image_dir(self):
        return os.path.join(self.meta_dir, MEM_IMAGE_FNAME_PRE)

    @classmethod
    def extract_fasmir(cls, fasmir, meta_dir, encrypt=True):
        PH = cls(
            fqir=None,
            fasmir=fasmir,
            zipfile_fname=None,
            encrypt=encrypt,
            insert_debug_stores=False,
            meta_dir=meta_dir,
        )
        PH._extract_fasmir()

    def _extract_fasmir(self):
        """emit memory images from fasmir
        also optionally inserts debug stores first
        """

        try:
            from femtobehav.sim.runner import ProgState
        except ImportError:
            raise ImportError(
                "couldn't import femtobehav, needed to extract FASMIR. This is a Femtosense-internal developer mode"
            )

        # debug stores, calls the debugger
        if self.insert_debug_stores:
            try:
                from femtodriver.debugger import SPUDebugger
            except ImportError:
                raise ImportError(
                    "couldn't import debugger. This is a Femtosense-internal developer feature"
                )
            SPUDebugger.insert_debug_stores(self.fasmir)

        # dump the metadata yaml
        metadata = self.fasmir.get_yaml_metadata(self.yamlfname, write_to_disk=False)

        # emit memory images
        basename = self.image_dir

        mems_per_core = {}
        for cidx in range(len(self.fasmir.used_cores())):
            prog_state = ProgState.FromFASMIR(
                self.fasmir
            )  # just used to construct memory files, {cidx : femtobehav.fasmir.ProgState}

            mems_per_core[cidx] = prog_state[cidx].get_packed_mems(encrypt=self.encrypt)

        compiled_data = CompiledData(metadata=metadata, mems_per_core=mems_per_core)

        return compiled_data

    def _add_fqir_meta(self):
        """adds FQIR metadata to yaml"""

        meta = self.compiled_data.metadata

        input_padding = {}
        output_padding = {}

        for tproto in self.fqir.subgraphs["ARITH"].inputs:
            num_fasmir_words = meta["inputs"][tproto.name]["len_64b_words"]
            num_fasmir_els = packing.words_to_els(
                num_fasmir_words, precision=meta["inputs"][tproto.name]["precision"]
            )
            input_padding[tproto.name] = {
                "fqir": tproto.shape[0],
                "fasmir": num_fasmir_els,
            }

        for tproto in self.fqir.subgraphs["ARITH"].outputs:
            num_fasmir_words = meta["outputs"][tproto.name]["len_64b_words"]
            num_fasmir_els = packing.words_to_els(
                num_fasmir_words, precision=meta["outputs"][tproto.name]["precision"]
            )
            output_padding[tproto.name] = {
                "fqir": tproto.shape[0],
                "fasmir": num_fasmir_els,
            }

        meta["fqir_input_padding"] = input_padding
        meta["fqir_output_padding"] = output_padding

        return meta
