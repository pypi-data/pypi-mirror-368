#!/usr/bin/env python
#  Copyright Femtosense 2024
#
#  By using this software package, you agree to abide by the terms and conditions
#  in the license agreement found at https://femtosense.ai/legal/eula/
#

"""
1. New paradigm:
    python API:
        fd.compile()
        fd.simulate()
        fd.compare()
        fd.execute_runner()
        fd.generate_audio_inputs()
        fd.write_metadata_to_disk()
        fd.cleanup_docker_containers()
        fd.get_docker_logs()
    cli:
        fd.run()
2. Only 1 docker client that is shared. Use a context manager so we clean up properly
3. More functional stype functions that have clear input args and returns
4. Got rid of passing args object everywhere
5. all functions but especially run_comparisons broken down into smaller bits
6. Docstrings/typehints
7. print statements are now logger statements
8. Keep objects in memory instead of writing to disk all the time
9. Better docstrings
10. Write more unit tests
"""

import atexit
import argparse
import fmot
import importlib
import logging
import os
import pickle
import sys
from argparse import (
    RawTextHelpFormatter,
)  # allow carriage returns in help strings, for displaying model options
from colorama import Fore, Style
from pathlib import Path

import docker
import numpy as np
import torch
import yaml
from femtocrux import CompilerClient
from femtorun import DummyRunner, FemtoRunner
from fmot.fqir import GraphProto
from scipy.io import wavfile

import femtodriver
from femtodriver import CompiledData, SPURunner
from femtodriver.fx_runner import FXRunner
from femtodriver.fqir_runner import FQIRArithRunner
from femtodriver.program_handler import NullHandler, ProgramHandler
from femtodriver.util.print_header import print_header
from femtodriver.util.run_util import process_single_outputs

# Configure the logging format
logging.basicConfig(
    format="[%(asctime)s][%(name)s][%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
    # level=logging.DEBUG,
)
logger = logging.getLogger(__name__)

try:
    from femtobehav.sim.runner import SimRunner  # for comparison
    from femtomapper.run import FMIRRunner

    DEV_MODE = True
except ImportError:
    DEV_MODE = False
    FMIRRunner = object
    SimRunner = object


if DEV_MODE:
    TOP_LEVEL_PACKAGE_DIR = Path(femtodriver.__file__).parent.parent.parent
    MODEL_SOURCE_DIR = TOP_LEVEL_PACKAGE_DIR / Path("models")
    # will only work if installed locally with -e
    if os.path.exists(MODEL_SOURCE_DIR):
        MODEL_SOURCE_DIR = str(MODEL_SOURCE_DIR)
    else:
        MODEL_SOURCE_DIR = None
else:
    MODEL_SOURCE_DIR = None


def check_dev_mode(feat):
    if not DEV_MODE:
        raise RuntimeError(
            f"{feat} is a FS-only feature, requires internal packages. Exiting"
        )


class Femtodriver:
    def __init__(
        self,
        model_source_dir: str | None = MODEL_SOURCE_DIR,
        debug: bool = False,
        force_femtocrux_compile: bool = False,
        force_femtocrux_sim: bool = False,
    ):
        """
        @param model_source_dir
        @param debug: the log level of the debugger True sets level to DEBUG otherwise INFO
        @param force_femtocrux_compile: use femtocrux to compile. Internal use.
        @param force_femtocrux_sim: whether to force the simulation to use femtocrux. Internal use.
        """
        self.model_source_dir = model_source_dir

        self.model_dir: str | None = None  # the output dir for the model
        self.metadata_zip = None
        self.modelname = None
        self.compiled_data = None
        self.fqir = None
        self.fasmir = None
        self.fmir = None

        # important internal objs
        self.compare_runners: list[FemtoRunner]

        # recording of simulation metrics
        self.sim_metrics: dict
        self.metrics_path: str

        self.femtocrux_client: CompilerClient | None = None
        self.using_cli: bool = False
        self.spu_runner: SPURunner = None
        self.force_femtocrux_compile: bool = force_femtocrux_compile
        self.force_femtocrux_sim: bool = force_femtocrux_sim
        self.compiler_kwargs = {}

        self._suppress_import_debug(debug)

    def __enter__(self):
        """
        Enter definition for context manager.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        When exiting the Context Manager, clean up the docker container
        """
        if exc_type:
            logger.error(f"Exception type: {exc_type}")
            logger.error(f"Exception value: {exc_val}")
            logger.error(f"Traceback: {exc_tb}")

        # Always clean up the Docker client, regardless of any
        if self.femtocrux_client:
            self.femtocrux_client.close()

        # Return False to propagate the exception, if any
        return False

    @staticmethod
    def _parse_args(argv):
        """returns argparse object and sets self.args
        also sets:
            self.comparisons
        """
        parser = argparse.ArgumentParser(
            formatter_class=RawTextHelpFormatter,
            description="run a pickled FASMIR or FQIR on hardware. Compare with output of FB's SimRunner\n\n"
            + "Useful recipes:\n"
            + "----------------------\n"
            + "Run on hardware, default comparisons with full debug (fasmir):\n"
            + "\tpython run_from_pt.py ../models/modelname --hardware=zynq --runners=fasmir --debug --debug_vars=all\n\n"
            + "Generate SD (no board/cable needed):\n"
            + "\tpython run_from_pt.py ../models/modelname\n\n"
            + "Run simulator (no board/cable needed, ignore the comparison):\n"
            + "\tpython run_from_pt.py ../models/modelname --runners=fasmir\n\n",
        )

        parser.add_argument(
            "model",
            nargs="?",
            help="model to run. " + Femtodriver._model_helpstr(),
        )
        parser.add_argument(
            "--model-options-file",
            default=None,
            help=".yaml with run options for different models (e.g. compiler options)."
            "Default is femtodriver/femtodriver/models/options.yaml",
        )
        parser.add_argument(
            "--output-dir",
            default="model_datas",
            help="where to write fasmir, fqir, programming images, programming streams, etc",
        )
        parser.add_argument(
            "--n-frames",
            default=2,
            type=int,
            help="number of random sim inputs to drive in",
        )
        parser.add_argument(
            "--input-file",
            default=None,
            help="file with inputs to drive in. Expects .npy from numpy.save."
            "Expecting single 2D array of values, indices are (timestep, vector_dim)",
        )
        parser.add_argument(
            "--input-sample-indices",
            default=None,
            help="lo,hi indices to run from input_file",
        )
        parser.add_argument(
            "--force-femtocrux-compile",
            default=False,
            action="store_true",
            help="force femtocrux as the compiler, even if FS internal packages present",
        )
        parser.add_argument(
            "--force-femtocrux-sim",
            default=False,
            action="store_true",
            help="force femtocrux as the simulator, even if FS internal packages present",
        )
        parser.add_argument(
            "--hardware",
            default="fakezynq",
            help="primary runner to use: (options: zynq, fakezynq, redis, evk2)",
        )
        parser.add_argument(
            "--runners",
            default="",
            help="which runners to execute. If there are multiple, compare each of them to the first, "
            "comma-separated. Options: hw, fasmir, fqir, fmir, fakehw",
        )
        parser.add_argument(
            "--debug-vars",
            default=None,
            help="debug variables to collect and compare values for, comma-separated (no spaces), or 'all'",
        )
        parser.add_argument(
            "--debug-vars-fname",
            default=None,
            help="file with a debug variable name on each line",
        )
        parser.add_argument(
            "--debug", default=False, action="store_true", help="set debug log level"
        )
        parser.add_argument(
            "--noencrypt",
            default=False,
            action="store_true",
            help="don't encrypt programming files",
        )
        parser.add_argument(
            "--input-period",
            default=0.016,
            type=float,
            help="simulator input period for energy estimation. No impact on runtime. Floating point seconds",
        )
        parser.add_argument(
            "--dummy-output-file",
            default=None,
            help="for fakezynq, the values that the runner should reply with. Specify a .npy for a single variable",
        )
        parser.add_argument(
            "--cleanup-docker",
            action="store_true",
            help="special argument to cleanup running femtocrux docker containers",
        )
        parser.add_argument(
            "--zynq-host",
            default=None,
            help="when using a real zynq board, specify ip address or hostname to connect to.",
        )

        args = parser.parse_args(argv)

        # Logic to handle special argument
        if args.cleanup_docker:
            print(
                "Special argument --cleanup-docker provided, input_file is not required."
            )
        elif not args.model:
            print("Error: model is required unless --cleanup-docker is run.")
            parser.print_help()
            sys.exit(1)

        return args

    def _get_compiler_env_for_docker(self, docker_kwargs):
        # get compiler version
        hwcfg = os.getenv("FS_HW_CFG")
        if hwcfg is None:
            hwcfg = "spu1p3v1.dat"
        if hwcfg is not None:
            if hwcfg.startswith("spu1p3v1"):
                version = {"FS_HW_CFG": hwcfg}
            elif hwcfg.startswith("spu2p0v1"):
                version = {"FS_HW_CFG": hwcfg}
            else:
                raise ValueError(
                    f"unknown FS_HW_CFG value {hwcfg}. "
                    "Must be spu1p3v1.dat or spu2p0v1.dat for SPU-001 or SPU-150 prototype,"
                    "respectively"
                )
        else:
            # assume default of 1p3
            version = {"FS_HW_CFG": "spu1p3v1.dat"}
            logger.warning(
                "FS_HW_CFG not explicitly set. Assuming default of ISA 1p3v1 (mass production chip)"
            )
            logger.warning(
                "  set 'export FS_HW_CFG=spu1p3v1.dat' for mass production chip"
            )
            logger.warning("  set 'export FS_HW_CFG=spu1p2v1.dat' for TC2")
            yn = input(
                "\nEnter 'y' if the default of ISA 1p3 is OK, otherwise set the environment variable and try again: "
            )
            if yn != "y":
                exit(-1)

        docker_kwargs["environment"].update(version)

    def _load_fasmir_pickle(self, model_path):
        fasmir = pickle.load(open(model_path, "rb"))
        if fasmir.__class__.__name__ not in ["FASMIR", "SteerableFASMIR"]:
            raise RuntimeError(f"supplied model {model_path} didn't contain FASMIR")
        return fasmir

    def _load_fqir_torchpickle(self, model_path):
        fqir = fmot.load(model_path, map_location=torch.device("cpu"))
        if fqir.__class__.__name__ not in ["GraphProto"]:
            raise RuntimeError(f"supplied model {model_path} didn't contain FQIR")
        return fqir

    def load_model(
        self, model: str | Path | GraphProto, name: str | None = "fqir"
    ) -> tuple:
        """
        Load a model from a file or in memory fmot fqir GraphProto.

        @param: model: a path to a model fqir on disk or the fqir in memory GraphProto
        @param: name: a string name for the model. Useful only with in memory GraphProto

        @returns tuple of modelname, fqir, fmir, fasmir
        """
        model_path = "resources/identity.pt"
        if isinstance(model, GraphProto):
            self.modelname = name
            self.fqir = model
            return self.modelname, self.fqir, None, None
        elif isinstance(model, Path):
            model_path = str(model)
        elif isinstance(model, str):
            model_path = model

        # get "hello world"/identity out of the way, it's in the package
        if model_path == "LOOPBACK":
            model_path = importlib.resources.files("femtodriver").joinpath(
                "resources/identity.pt"
            )
            self.modelname = "LOOPBACK"
            self.fqir = fmot.load(model_path, map_location=torch.device("cpu"))
            return self.modelname, self.fqir, self.fmir, self.fasmir

        model_with_ext = os.path.basename(os.path.expanduser(model_path))
        self.modelname, model_ext = os.path.splitext(model_with_ext)

        if model_ext in [".pt", ".pth"]:
            # open model
            self.fqir = self._load_fqir_torchpickle(model_path)
        elif model_ext == ".pck":
            # open model
            self.fasmir = self._load_fasmir_pickle(model_path)
        elif model_ext == "":
            # metadata dir
            self.model_dir = model_path
        elif model_ext == ".zip":
            # zipped metadata dir
            self.metadata_zip = model_path
        elif model_ext == ".femto":
            self.compiled_data = CompiledData.read_from_femtofile(
                femtofile_path=model_path
            )
        else:
            raise ValueError(
                f"invalid model extension. Got {model_ext}. Need one of: .pt/.pth (FQIR pickle) or .pck (FASMIR pickle)"
            )
        return self.modelname, self.fqir, self.fmir, self.fasmir

    def compile_metadata(
        self,
        output_dir: str = "model_datas",
        model_options_file: str | None = None,
        noencrypt: bool = False,
    ) -> CompiledData:
        """
        compile the model and create

        also may generate new self.fmir, self.fasmir if starting w/ FQIR

        @param: output_dir: The output directory TODO: Move this code to CompiledData dataclass
        @param: model_options_file: Special model options comiler flags
        @param: noencrypt: use encryption or not (only useful internally)

        @returns: CompiledData object
        """
        if self.compiled_data is not None:
            logger.info(
                "Skipping compilation because we started from compiled femtofile."
            )
            self.model_dir = str(Path(output_dir) / Path(self.modelname))
            self.meta_dir = str(
                Path(output_dir) / Path(self.modelname) / Path("meta_from_femtofile")
            )
            self.compiled_data.write_to_files(output_dir=self.meta_dir)
            return self.compiled_data

        if self.model_dir is not None:
            meta_dir = None
            found = False
            PREV_COMPILED = ["femtomapper", "femtocrux", "zipfile"]
            for compiler_name in PREV_COMPILED:
                # find first working meta dir
                meta_dir = os.path.join(self.model_dir, f"meta_from_{compiler_name}")
                if os.path.exists(meta_dir):
                    found = True
                    break

            # doesn't do anything, just provides handler.fasmir/fmir/fqir = None
            if not found:
                raise RuntimeError(
                    f"couldn't find previously compiled meta_from_ {PREV_COMPILED} in {self.model_dir}"
                )
            handler = NullHandler(meta_dir)

        else:
            # docker kwargs
            docker_kwargs = {"environment": {}}
            self._get_compiler_env_for_docker(
                docker_kwargs=docker_kwargs
            )  # get compiler version

            # get compiler args
            model_options_path = self._get_options_path(
                self.model_source_dir, model_options_file
            )
            self.compiler_kwargs = self._load_model_options(
                self.modelname, model_options_path
            )
            if self.metadata_zip is not None:
                compiler_name = "zipfile"
            elif DEV_MODE and not self.force_femtocrux_compile:
                compiler_name = "femtomapper"
            else:
                compiler_name = "femtocrux"
                self.femtocrux_client = CompilerClient(docker_kwargs)
                atexit.register(self.femtocrux_client.on_exit)

            self.model_dir = os.path.join(
                os.path.expanduser(output_dir), f"{self.modelname}"
            )
            meta_dir = os.path.join(self.model_dir, f"meta_from_{compiler_name}")
            if not os.path.exists(meta_dir):
                os.makedirs(meta_dir)

            handler = ProgramHandler(
                fasmir=self.fasmir,
                fqir=self.fqir,
                femtocrux_client=self.femtocrux_client,
                zipfile_fname=self.metadata_zip,
                encrypt=not noencrypt,
                meta_dir=meta_dir,
            )

        compiled_data, self.fasmir, self.fmir = handler.compile(
            compiler=compiler_name, compiler_kwargs=self.compiler_kwargs
        )

        # if using internal packages (DEV_MODE), it might have made a new FASMIR/FMIR
        # self.fasmir = handler.fasmir
        # self.fmir = handler.fmir
        # compiled_data = handler.compiled_data

        self.meta_dir = meta_dir  # Still need this because we need to fix SPURunner
        return compiled_data

    @staticmethod
    def _get_runner_kwargs(noencrypt, hardware):
        runner_kwargs: dict[str, str | bool] = {"encrypt": not noencrypt}
        if hardware == "zynq":  # hard SPU plugged into FPGA
            runner_kwargs["platform"] = "zcu104"
            runner_kwargs["program_pll"] = True
            runner_kwargs["fake_connection"] = False

        elif hardware == "fpgazynq":  # soft SPU inside FPGA logic
            runner_kwargs["platform"] = "zcu104"
            runner_kwargs["program_pll"] = False
            runner_kwargs["fake_connection"] = False

        elif hardware == "redis":  # redis-based simulation (questa)
            runner_kwargs["platform"] = "redis"
            runner_kwargs["program_pll"] = True
            runner_kwargs["fake_connection"] = False

        elif hardware == "fakezynq":  # e.g. for generating EVK program
            runner_kwargs["platform"] = "zcu104"
            runner_kwargs["program_pll"] = False
            runner_kwargs["fake_connection"] = True

        elif hardware == "fakeredis":  # e.g. for integration test
            runner_kwargs["platform"] = "redis"
            runner_kwargs["program_pll"] = False
            runner_kwargs["fake_connection"] = True

        elif hardware == "evk2":  # e.g. for integration test
            runner_kwargs["platform"] = "evk2"
            runner_kwargs["program_pll"] = True
            runner_kwargs["fake_connection"] = False
        else:
            raise RuntimeError(f"Unknown runner {hardware}")

        return runner_kwargs

    def create_SPURunner(
        self,
        compiled_data: CompiledData,
        meta_dir: str,
        noencrypt: bool = False,
        hardware: str = "fakezynq",
        debug_vars: str | None = None,
        debug_vars_fname: str | None = None,
        dummy_output_file: str | None = None,
        zynq_host: str | None = None,
    ) -> SPURunner:
        """instantiates spu_runner = SPURunner()
        handles debug-vars-related options
        and fake outputs/recv vals
        returns spu_runner
        """

        runner_kwargs = self._get_runner_kwargs(noencrypt=noencrypt, hardware=hardware)

        if not os.path.exists(self.io_records_dir):
            os.makedirs(self.io_records_dir)

        # make SPURunner and SimRunner to compare it to
        fake_hw_recv_vals = None
        if dummy_output_file is not None:
            fake_hw_recv_vals = np.load(dummy_output_file)

        # collect debug vars
        self.debug_vars = []
        if debug_vars_fname is not None:
            varf = open(debug_vars_fname, "r")
            self.debug_vars += varf.readlines()

        if debug_vars is not None:
            self.debug_vars += debug_vars.split(",")
        try:
            spu_runner = SPURunner(
                compiled_data,
                meta_dir,
                fake_hw_recv_vals=fake_hw_recv_vals,
                debug_vars=self.debug_vars,
                io_records_dir=self.io_records_dir,
                zynq_host=zynq_host,
                **runner_kwargs,
            )
        except Exception as e:
            raise e

        if DEV_MODE:
            spu_runner.attach_debugger(self.fasmir)

        # fill in for 'all' debug vars option
        # not all runners can necesarily take 'all' as a debug vars arg
        if debug_vars == "all" or debug_vars == ["all"]:
            self.debug_vars = spu_runner.debug_vars

        return spu_runner

    def generate_audio_inputs(
        self,
        input: str | np.ndarray | None = None,
        spu_runner: SPURunner | None = None,
        n_frames: int = 2,
        input_sample_indices: list | None = None,
    ) -> dict[str, np.ndarray]:
        """
        Read inputs from a file or generate some fake inputs for testing the model in simulation.

        If no input_file is specified, you can specify n_frames to generate fake inputs for

        @param: spu_runner: The FemtoRunner to use, could be hw, fmir, fqir, fasmir
        @param: input_file: the wav file to load into a np.ndarray or the npy file to load a generalized input
        @param: n_frames: allows you to specify length of fake input in frames if not using a wav file input
        @param: input_sample_indices: the slice of the input to simulate. Useful if the input is long to make
                simulation faster.

        @returns A dictionary of the form {"varname": np.ndarray} See the docs about how inputs to models are handled
        """

        if spu_runner is None:
            spu_runner = self.spu_runner

        N = n_frames

        if input is None:
            shaped_inputs = spu_runner.make_fake_inputs(N, style="random")
            return shaped_inputs
        elif isinstance(input, np.ndarray):
            input_vals = self._create_shaped_input_from_ndarray(input, spu_runner)
        elif input.endswith(".wav"):
            input_vals = self._create_shaped_input_from_wav(input, spu_runner)
        elif input.endswith(".npy"):
            input_vals = np.load(input)
        else:
            raise RuntimeError(
                "unsupported file format for --input_file, only .wav and .npy is supported"
            )

        # Create a fake input to get the correct shape and then fill it with the input_vals from above.
        N = input_vals.shape[0]
        shaped_inputs = spu_runner.make_fake_inputs(N, style="random")

        if len(shaped_inputs) > 1:
            raise RuntimeError("can only support one input via file")
        for k, v in shaped_inputs.items():
            shaped_inputs[k] = input_vals

        # trim to sample range, if supplied
        if input_sample_indices is not None:
            lo, hi = input_sample_indices[0], input_sample_indices[1]
            for k, v in shaped_inputs.items():
                shaped_inputs[k] = shaped_inputs[k][int(lo) : int(hi)]

        return shaped_inputs

    def execute_runner(
        self,
        requested_runner: str,
        model_inputs: dict[str, np.ndarray],
        noencrypt: bool = False,
        hardware: str = "fakezynq",
        input_period: float = 0.016,
        dummy_output_file: str | None = None,
        debug_vars: str | None = None,
        debug_vars_fname: str | None = None,
        zynq_host: str | None = None,
    ) -> tuple[dict, FemtoRunner]:
        """
        Runs an input through a given spu_runner. Runners could be hw, fasmir, fmir, fqir.
        The input could be a fake autogenerated random input or an np.ndarray. Use the helper
        function generate_audio_inputs() to turn wav files into the correct shape ndarray.

        @param: requested_runner: a string runner out of set({"hw", "fasmir", "fmir", "fqir"})
        @param: model_inputs: An ndarray that matches the shape required by the model
        @param: input_period: the input period processing time for a frame in seconds

        @returns: returns a tuple
                    element1: dictionary which contains the internals activations and outputs of a runner.
                    element2: the runner object
        """

        femto_runner, runner_name = self.create_runner(
            requested_runner=requested_runner,
            spu_runner=self.spu_runner,
            fqir=self.fqir,
            sim_fasmir=self.fasmir,
            sim_fmir=self.fmir,
            noencrypt=noencrypt,
            hardware=hardware,
            input_period=input_period,
            dummy_output_file=dummy_output_file,
            debug_vars=debug_vars,
            debug_vars_fname=debug_vars_fname,
            zynq_host=zynq_host,
        )

        femto_runner.reset()
        output_vals, internal_vals, output_valid_mask = femto_runner.run(model_inputs)
        outputs = {runner_name: output_vals}
        internals = {runner_name: internal_vals}
        femto_runner.finish()

        result = {
            "compare_str": "Single Runner",
            "pass": "No Comparisons",
            "internals": internals,
            "outputs": outputs,
        }

        return result, femto_runner

    def _get_runner_metrics(self, runner, input_period: float = 0.016) -> str:
        """
        Get the metrics from the FXRunner or the SimRunner

        @returns: the sim metrics as a string
        """
        metrics = ""
        if runner.__class__.__name__ == "SimRunner":
            logger.info("Found a SimRunner")

            yaml_fb_metrics = runner.get_metrics(
                input_period=input_period,
                as_yamlable=True,
                concise=True,
            )

            self.metrics_path = os.path.join(self.model_dir, "metrics.yaml")
            with open(self.metrics_path, "w") as f:
                yaml.dump(yaml_fb_metrics, f, sort_keys=False)

            metrics = runner.get_metrics(input_period=input_period, as_str=True)
            # logger.info("power was", self.sim_metrics["Power (W)"])
            self.sim_metrics = yaml_fb_metrics

        elif runner.__class__.__name__ == "FXRunner":
            logger.info("found Femtocrux's simulator.")
            metrics = runner.sim_report

        return metrics

    def _dump_pickles(self, inputs, outputs, internals):
        """
        Optionally dump pickles
        """
        pickle.dump(
            inputs, open(os.path.join(self.meta_dir, "runner_inputs.pck"), "wb")
        )
        pickle.dump(
            outputs, open(os.path.join(self.meta_dir, "runner_outputs.pck"), "wb")
        )
        pickle.dump(
            internals, open(os.path.join(self.meta_dir, "runner_internals.pck"), "wb")
        )

        logger.info(
            f"outputs and internal variables pickles saved to {os.path.join(self.meta_dir, 'runner_*.pck')}"
        )
        logger.info(
            "  unpickle with internals = pickle.load(open('runner_internals.pck', 'rb'))"
        )
        logger.info("  then internals[runner_name][varname][j]")
        logger.info("  is runner_name's values for varname at timestep j")
        logger.info("  fasmir, fmir, fqir will report everything.")
        logger.info(
            "  the setting of --debug_vars determines what's available from hardware."
        )

        logger.debug("===============================")
        logger.debug("outputs:")
        for runner, vals in outputs.items():
            logger.debug("-------------------------------")
            logger.debug(f"runner {runner}")
            logger.debug(outputs)
        logger.debug("===============================")

        out_fnames, _ = process_single_outputs(outputs)
        if out_fnames is not None:
            logger.info(
                f"also saved single output variable's values for each runner to {out_fnames}"
            )
            logger.info("  summarized to output_diff.png")

    def _prepare_comparisons(
        self,
        spu_runner,
        comparisons,
        fqir,
        sim_fasmir,
        sim_fmir,
        noencrypt: bool = False,
        hardware="fakezynq",
        dummy_output_file: str | None = None,
        debug_vars: str | None = None,
        debug_vars_fname: str | None = None,
        zynq_host: str | None = None,
    ):
        """
        This function creates different runners based on the input comparison list. These runners can then later be
        executed and the outputs can be compared to check that they match.
        """
        runners_to_compare = {}
        for comp in comparisons:
            runner, name = self.create_runner(
                comp,
                spu_runner,
                fqir,
                sim_fasmir,
                sim_fmir,
                noencrypt=noencrypt,
                hardware=hardware,
                dummy_output_file=dummy_output_file,
                debug_vars=debug_vars,
                debug_vars_fname=debug_vars_fname,
                zynq_host=zynq_host,
            )
            runners_to_compare[name] = runner

        return list(runners_to_compare.values()), list(runners_to_compare.keys())

    def create_runner(
        self,
        requested_runner: str,
        spu_runner: SPURunner = None,
        fqir=None,
        sim_fasmir=None,
        sim_fmir=None,
        noencrypt: bool = False,
        hardware: str = "fakezynq",
        input_period: float = 0.016,
        dummy_output_file: str | None = None,
        debug_vars: str | None = None,
        debug_vars_fname: str | None = None,
        zynq_host: str | None = None,
    ) -> tuple[FemtoRunner, str]:
        """
        This function creates a runner based on which runner is requested.
        """
        if spu_runner is None:
            spu_runner = self.spu_runner
        if fqir is None:
            fqir = self.fqir
        if sim_fasmir is None:
            sim_fasmir = self.fasmir
        if sim_fmir is None:
            sim_fmir = self.fmir
        runner = None
        name = ""
        if requested_runner == "hw":
            spu_runner = self.create_SPURunner(
                self.compiled_data,
                self.meta_dir,
                noencrypt=noencrypt,
                hardware=hardware,
                debug_vars=debug_vars,
                debug_vars_fname=debug_vars_fname,
                dummy_output_file=dummy_output_file,
                zynq_host=zynq_host,
            )
            runner = spu_runner
            self.spu_runner = spu_runner
            name = "hardware"
        elif requested_runner == "fasmir":
            if DEV_MODE and not self.force_femtocrux_sim:
                # FB runner
                fasmir_runner = SimRunner(
                    sim_fasmir,  # model might be fqir, need to compile for SimRunner
                    input_padding=spu_runner.io.input_padding,
                    output_padding=spu_runner.io.output_padding,
                )

            else:
                # use FXRunner which wraps docker
                fasmir_runner = FXRunner(
                    self.fqir,  # XXX it will recompile, not sure if there's a way to get it to use what it already compiled
                    compiler_client=self.femtocrux_client,
                    input_padding=spu_runner.io.input_padding,
                    output_padding=spu_runner.io.output_padding,
                    compiler_args=self.compiler_kwargs,
                    input_period=input_period,
                )

            runner = fasmir_runner
            name = "fasmir"

        elif requested_runner == "fqir":
            if fqir is not None:
                # FIXME the def'n is duplicated in FD and FM, should really go in fmot
                fqir_runner = FQIRArithRunner(fqir)
                runner = fqir_runner
                name = "fqir"
            else:
                raise (Exception("Requested fqir runner but no fqir was present."))
        elif requested_runner == "fmir":
            self._check_dev_mode("comparison to FMIR runner")
            if self.force_femtocrux_compile and self.force_femtocrux_sim:
                raise NotImplementedError("FX can't simulate FMIR")
            if fqir is not None:
                fmir_runner = FMIRRunner(sim_fmir)
                runner = fmir_runner
                name = "fmir"
        elif requested_runner == "dummy":
            # for fake runner, what do you reply with
            if dummy_output_file is not None:
                fname = dummy_output_file
                if fname.endswith(".npy"):
                    dummy_vals = np.load(fname)
                    dummy_output_dict = {
                        spu_runner.get_single_output_name(): dummy_vals
                    }
                elif fname.endswith(".pt"):
                    # would put dictionary with multiple output vars in here
                    raise RuntimeError(
                        "unsupported file format for --dummy_output_file, only .npy is supported"
                    )
                else:
                    raise RuntimeError(
                        "unsupported file format for --dummy_output_file, only .npy is supported"
                    )
            else:
                dummy_output_dict = None
            fakehw_runner = DummyRunner(dummy_output_dict)
            runner = fakehw_runner
            name = "dummy"
        else:
            raise RuntimeError(f"unknown comparison runner '{requested_runner}'")

        return runner, name

    def _run_comparisons(
        self,
        comparisons: list[str],
        inputs: dict[str, np.ndarray],
        noencrypt: bool = False,
        hardware="fakezynq",
        dummy_output_file: str | None = None,
        debug_vars: str | None = None,
        debug_vars_fname: str | None = None,
        zynq_host: str | None = None,
    ) -> dict:
        """
        Run comparisons between the different runners.

        @param comparisons: list of comparisons. Possible values, hw, fasmir, fqir, fmir
        @param inputs: an array with a shapre based on the model in question (batch=1 during inference, frames, samples)
        @param dummy_output_file: file containing dummy outputs (only useful internally)
        """
        fqir = self.fqir
        sim_fasmir = self.fasmir
        sim_fmir = self.fmir

        if len(comparisons) <= 1:
            logger.info(
                "You have only specified one item in comparison list. "
                "If this is the intention use simulate() otherwise specify multiple comparisons."
            )
            return 1

        # & is set intersection: fqir, fmir in comparisons set
        if {"fqir", "fmir"} & set(comparisons) and fqir is None:
            raise RuntimeError(
                "asked for fqir or fmir comparison, but did't start from FQIR"
            )
        if {"fasmir"} & set(comparisons) and (fqir is None and sim_fasmir is None):
            raise RuntimeError(
                "asked for fasmir comparison, but we can't make fasmir. "
                "If you started from a femtofile, this isn't supported."
            )

        spu_runner = self.spu_runner

        compare_runners, compare_names = self._prepare_comparisons(
            spu_runner=spu_runner,
            comparisons=comparisons,
            fqir=fqir,
            sim_fasmir=sim_fasmir,
            sim_fmir=sim_fmir,
            noencrypt=noencrypt,
            hardware=hardware,
            dummy_output_file=dummy_output_file,
            debug_vars=debug_vars,
            debug_vars_fname=debug_vars_fname,
            zynq_host=zynq_host,
        )

        self.compare_runners = compare_runners

        spu_runner.ioplug.start_recording("io_sequence")

        # compare_status below is used as a return value for FemtoRunner.compare_runs() as it is
        # mutable and passed in and modified. This is like c++ pass by reference. We want to change
        # this soon but it requires fixes across other repos.
        # The new design for would look like:
        # compare_status, comparison_results = FemtoRunner.compare_runs(...)
        # comparison_results = {
        #     "outputs":   {"runner_name": {...}}
        #     "internals": {"runner_name": {...}}
        # }
        self.compare_status = {}
        outputs, internals = FemtoRunner.compare_runs(
            inputs,
            *compare_runners,
            names=compare_names,
            compare_internals=len(self.spu_runner.debug_vars) > 0,
            except_on_error=False,
            compare_status=self.compare_status,
        )

        spu_runner.ioplug.commit_recording("all.yaml")

        self._dump_pickles(inputs, outputs, internals)

        self.compare_status["outputs"] = outputs
        self.compare_status["internals"] = internals

        return self.compare_status

    def print_comparison_results(self, compare_status) -> None:
        # repeat output comparison result
        line_width = 80
        if compare_status["pass"]:
            logger.info(Fore.GREEN)
            logger.info("@" * line_width)
            logger.info("comparison good!")
            logger.info("@" * line_width)
            logger.info(Style.RESET_ALL)
        else:
            logger.info(Fore.RED)
            logger.info(compare_status["status_str"])
            logger.info("X" * line_width)
            logger.info("X" * line_width)
            logger.info("COMPARISON FAILED")
            logger.info("X" * line_width)
            logger.info("X" * line_width)
            logger.info(Style.RESET_ALL)

    def _suppress_import_debug(self, debug):
        if debug:
            logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
            # turn these down, they're long and annoying
            mpl_logger = logging.getLogger("matplotlib")
            mpl_logger.setLevel(logging.WARNING)
            PIL_logger = logging.getLogger("PIL")
            PIL_logger.setLevel(logging.WARNING)
        else:
            logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    @staticmethod
    def _check_dev_mode(feat):
        if not DEV_MODE:
            raise RuntimeError(
                f"{feat} is a FS-only feature, requires internal packages. Exiting"
            )

    @staticmethod
    def _model_helpstr(model_source_dir=MODEL_SOURCE_DIR):
        if model_source_dir is None:
            return ""

        yamlfname = f"{model_source_dir}/options.yaml"
        with open(yamlfname, "r") as file:
            model_desc = yaml.safe_load(file)

        s = "\navailable models in femtodriver/femtodriver/models:\n"
        thisdir, subdirs, files = next(iter(os.walk(model_source_dir)))
        for file in files:
            if file.endswith(".pt"):
                modelname = file[:-3]

                s += f"  {modelname}"
                if modelname not in model_desc:
                    s += "\t  <-- missing specification in options.yaml"
                s += "\n"
            elif file.endswith(".pck"):
                modelname = file[:-4]

                s += f"  {modelname}"
                if modelname not in model_desc:
                    s += "\t  <-- missing specification in options.yaml"
                s += "\n"

        return s

    @staticmethod
    def _get_options_path(model_source_dir, model_options_file):
        if model_options_file is not None:
            model_options_file = os.path.expanduser(model_options_file)
            if not os.path.exists(model_options_file):
                raise ValueError(
                    f"supplied model options file {model_options_file} does not exist"
                )
            return model_options_file

        else:
            if model_source_dir is None:
                return None
            else:
                return os.path.join(model_source_dir, "options.yaml")

    @staticmethod
    def _load_model_options(model, options_path):
        """look up the options (just compiler kwargs right now) for the model"""

        # open yaml to get model options
        if options_path is not None:
            with open(options_path, "r") as file:
                model_desc = yaml.safe_load(file)

            if "DEFAULT" in model_desc:
                logger.info("found DEFAULT compiler options")
                compiler_kwargs = model_desc["DEFAULT"]["compiler_kwargs"]
            else:
                compiler_kwargs = {}

            if model in model_desc:
                if "compiler_kwargs" in model_desc[model]:
                    compiler_kwargs.update(model_desc[model]["compiler_kwargs"])
        else:
            model_desc = {}
            compiler_kwargs = {}

        logger.info("loaded the following compiler options")
        if "DEFAULT" in model_desc:
            logger.info("(based on DEFAULT from options file)")

        for k, v in compiler_kwargs.items():
            logger.info(f"  {k} : {v}")

        return compiler_kwargs

    @property
    def io_records_dir(self):
        return os.path.join(self.model_dir, "io_records")

    def _create_shaped_input_from_wav(
        self, file_path: str, spu_runner: SPURunner
    ) -> np.ndarray:
        """
        Convert an input wav file to a numpy array with the correct shape
        to run through the model. This often means converting it to a
        shape of (frames, samples) where the value of samples is the hop_size.

        @parm file_path: input wavfile
        @returns a numpy array with shape (frames, samples) e.g. (N, 32) for 32 samples per frame
        """

        # Load the wav file
        sampling_rate, data = wavfile.read(file_path)

        # 'sampling_rate' is the sampling rate of the wav file
        # 'data' is a numpy array containing the audio data
        logger.info(
            f"Input wavfile sampling rate: {sampling_rate} data type: {data.dtype}"
        )
        return self._create_shaped_input_from_ndarray(data, spu_runner)

    def _create_shaped_input_from_ndarray(
        self, data: np.ndarray, spu_runner: SPURunner
    ):
        """
        Convert an input wav file to a numpy array with the correct shape
        to run through the model. This often means converting it to a
        shape of (frames, samples) where the value of samples is the hop_size.

        @parm data: a numpy array containing the data with shape (N,) where N is the number of samples
        @returns a numpy array with shape (frames, samples) e.g. (N, 32) for 32 samples per frame
        """

        # Figure out the shape that we need by creating a fake input and reshaping
        # the real data to match this shape.
        fake_input = spu_runner.make_fake_inputs(1, style="random")
        if len(fake_input.keys()) != 1:
            raise (
                Exception(
                    "There is more than 1 expected input for this model so we can't pass the wavfile to it."
                )
            )

        # This just gets the first key from the dict since there should only be 1.
        input_var_name = next(iter(fake_input))

        # This is to find out the shape the input needs to be for the model
        _, samples = fake_input[input_var_name].shape

        # The first part of this line data[:len(data)//samples * samples]
        # truncates the data into something divisible by samples and
        # then we reshape to (frames, samples) to match what the model expects
        data = data[: len(data) // samples * samples].reshape(-1, samples)

        return data

    def _create_fake_spu_runner(self):
        fake_spu_runner = self.create_SPURunner(
            self.compiled_data,
            None,  # shouldn't need it any more
            noencrypt=self.noencrypt,
            hardware="fakezynq",
        )
        return fake_spu_runner

    def write_metadata_to_disk(self, output_dir: str) -> None:
        """
        Write the metadata files to disk in the output dir

        @param: output_dir
        """
        self.compiled_data.write_to_files(output_dir=output_dir)

    def write_metrics_to_disk(self, metrics: str, output_dir: str):
        """
        Write the metrics returned from simulator to the output dir
        """
        fullpath = Path(output_dir).expanduser() / Path(self.modelname) / "metrics.txt"
        with open(fullpath, "w") as f:
            f.write(metrics)

        logger.info(f"Wrote metrics.txt to {fullpath}")

        return fullpath

    def get_docker_logs(self) -> str:
        """
        Get the logs for the docker container if it's running.
        """

        if self.femtocrux_client:
            logs = self.femtocrux_client.container.logs()
            logs = logs.decode("utf-8")
            formatted_logs = logs.replace("\\n", "\n")
            return formatted_logs
        else:
            logger.error(
                "Can't get logs because we don't have a handle to a container."
            )
        return "No logs available"

    def cleanup_docker_containers(self) -> None:
        """
        If you have running femtocrux docker containers because you were using a debugger and exited before
        the cleanup __exit__ of the context manager could be called, we provide this helper to manually
        cleanup any running docker containers.
        """
        # Initialize Docker client
        client = docker.from_env()

        # Get a list of all running containers
        running_containers = client.containers.list()

        # Filter containers that are using the image ghcr.io/femtosense/femtocrux
        femtocrux_containers = [
            container
            for container in running_containers
            if container.image.tags
            and any(
                tag.startswith("ghcr.io/femtosense/femtocrux")
                for tag in container.image.tags
            )
        ]

        if not femtocrux_containers:
            print(
                "No running containers found with the image tag 'ghcr.io/femtosense/femtocrux'."
            )
        else:
            for container in femtocrux_containers:
                print(f"Stopping container {container.name} with ID {container.id}...")
                container.stop()
                print(f"Container {container.name} stopped.")

    def generate_program_files(self) -> None:
        """
        Generate 0PROG_A addresses, 0PROG_D data files.
        This prog file format will be deprecated soon in favor of
        femtofiles which provide numerous benefits.

        These program files will be written to disk under:

        {output_dir}/{model_name}/io_records/apb_records/
        """
        if not self.spu_runner:
            self.spu_runner = self._create_fake_spu_runner()

        self.spu_runner.reset(record=True)
        logger.info(f"Program files exported to {self.io_records_dir}/apb_records/")

    def compile(
        self,
        model,
        model_name: str | None = None,
        model_options_file=None,
        output_dir: str | Path = "model_datas",
        noencrypt: bool = False,
        model_type: str = "custom",
        model_version: str = "1.0.0",
        target_spu="spu001",
    ) -> tuple[str, str, str]:
        """
        Compiles the model metadata stored in the meta_dir on disk and also
        generates program files in femto format as well as PROG format.

        @params: Look at the run() method docstring for information in parameters

        @returns: A tuple of (the meta data directory on disk, the femtofile_path, the femtofile size)
        """
        if isinstance(output_dir, Path):
            output_dir = str(output_dir)

        # Set this to none so that it can get repopulated on each call
        self.model_dir = None
        self.noencrypt = noencrypt

        self.modelname, self.fqir, self.fmir, self.fasmir = self.load_model(
            model, model_name
        )

        if self.using_cli:
            print_header("Compiling Metadata")
        # compile the model using ProgramHandler
        # regardless of the input type, all paths end in a metadata dir
        self.compiled_data = self.compile_metadata(
            output_dir=output_dir,
            model_options_file=model_options_file,
            noencrypt=noencrypt,
        )

        if self.using_cli:
            print_header("Exporting Prog Files (Deprecated Soon)")
        self.generate_program_files()

        if model_name is None:
            model_info = self.io_records_dir.split("/")
            model_name = model_info[-2] if len(model_info) > 2 else "fqir"

        if self.using_cli:
            print_header("Exporting femtofile")
        femtofile_path, femtofile_size = self.spu_runner.export_femto_file(
            compiled_data=self.compiled_data,
            model_type=model_type,
            model_name=model_name,
            femtodriver_version=femtodriver.__version__,
            model_version=model_version,
            target_spu=target_spu,
        )

        return self.meta_dir, femtofile_path, femtofile_size

    def simulate(
        self,
        model_inputs: dict[str, np.ndarray],
        input_period: float,
    ) -> tuple[dict, str]:
        """
        Runs a simulation using Fasmir and returns metrics including estimated power.

        @params: See run() docstring for details on parameters

        @returns: A tuple with the first element as a dictionary of sim results and the second element
                  is string representation of the yaml sim metrics
        """
        if self.meta_dir:
            logger.info("running Simulation")
        else:
            logger.info(
                "You haven't compiled a model. Please compile a model before simulating"
            )

        requested_runner = "fasmir"

        if self.fasmir is None and self.fqir is None:
            raise (
                Exception(
                    "Can't run hardware simulation without fqir or fasmir. Did you start from a femtofile?\n"
                    "Running simulate() starting from a femtofile is not supported. Start from fqir if you can."
                )
            )

        result, runner = self.execute_runner(
            requested_runner,
            model_inputs=model_inputs,
            input_period=input_period,
        )

        metrics = self._get_runner_metrics(runner, input_period=input_period)

        return result, metrics

    def compare(
        self,
        model_inputs: dict[str, np.ndarray],
        runners_to_compare: list,
        noencrypt: bool = False,
        hardware="fakezynq",
        dummy_output_file: str | None = None,
        debug_vars: str | None = None,
        debug_vars_fname: str | None = None,
        zynq_host: str | None = None,
    ) -> dict:
        """
        Compare runs a comparison between different FemtoRunners.

        @param runners_to_compare: The runners to compare. These are fqir, fmir, fasmir and hw.
                                   information on the rest of the arguments are in the run() docstring
        @returns: returns a dictionary of the status of the comparison and any mismatches as well as the results of
                  each runner.
        """
        if self.meta_dir:
            logger.info("running Simulation")
        else:
            logger.info(
                "You haven't compiled a model. Please compile a model before simulating"
            )

        return self._run_comparisons(
            runners_to_compare,
            inputs=model_inputs,
            noencrypt=noencrypt,
            hardware=hardware,
            dummy_output_file=dummy_output_file,
            debug_vars=debug_vars,
            debug_vars_fname=debug_vars_fname,
            zynq_host=zynq_host,
        )

    def run(
        self,
        model: str | Path | GraphProto,
        model_options_file=None,
        output_dir: str = "model_datas",
        n_frames: int = 2,
        input_file: str = None,
        input_sample_indices: str | None = None,
        force_femtocrux_compile: bool = False,
        force_femtocrux_sim: bool = False,
        hardware: str = "fakezynq",
        runners: str = "",
        debug_vars: str | None = None,
        debug_vars_fname: str | None = None,
        debug: bool = False,
        noencrypt: bool = False,
        input_period: float = 0.016,
        dummy_output_file: str | None = None,
        cleanup_docker: bool = False,
        zynq_host: str | None = None,
    ):
        """
        This is the python API version of the CLI argparse arguments. The descriptions from there hold.

        Required params:
        model:                          Model to run.

        Optional:
        model_options_file:             .yaml with run options for different models (e.g., compiler options).
                                        Default is femtodriver/femtodriver/models/options.yaml
        output_dir:                     Directory where to write fasmir, fqir, programming images,
                                        programming streams, etc.
        n_frames:                       Number of random frames to run through simulation.
        input_file:                     File with inputs to drive in. Expects .npy from numpy.save.
                                        Expecting single 2D array of values, indices are (timestep, vector_dim)
        input_sample_indices:           lo, hi indices to run from input_file.
        force_femtocrux_compile:        Force femtocrux as the compiler, even if FS internal packages present.
        force_femtocrux_sim:            Force femtocrux as the simulator, even if FS internal packages present.
        hardware:                       Primary runner to use: (options: zynq, fakezynq, redis).
        runners:                        Which runners to execute. If there are multiple, compare each of them
                                        to the first, comma-separated. Options: hw, fasmir, fqir, fmir, fakehw.
        debug_vars:                     Debug variables to collect and compare values for, comma-separated
                                        (no spaces), or 'all'.
        debug_vars_fname:               File with a debug variable name on each line.
        debug:                          Set debug log level.
        noencrypt:                      Don't encrypt programming files.
        input_period:                   Simulator input period for energy estimation. No impact on runtime.
                                        Floating point seconds.
        dummy_output_file:              For fakezynq, the values that the runner should reply with.
                                        Specify a .npy for a single variable.
        zynq_host:                      The ip address or hostname of the zynq board
        """

        if cleanup_docker:
            print_header("Cleaning up femtocrux docker containers")
            self.cleanup_docker_containers()
            return 0

        if isinstance(output_dir, Path):
            output_dir = str(output_dir)

        # Set this to none so that it can get repopulated on each call
        self.model_dir = None

        # collect comparisons
        if runners == "":
            self.comparisons = []
        else:
            self.comparisons = runners.split(",")
        ########################################################

        self.using_cli = True
        meta_dir, femtofile_path, femtofile_size = self.compile(
            model,
            model_options_file=model_options_file,
            output_dir=output_dir,
            noencrypt=noencrypt,
        )

        self.write_metadata_to_disk(output_dir=self.meta_dir)

        result = {}

        if input_sample_indices is not None:
            input_sample_indices = input_sample_indices.split(",")

        model_inputs = self.generate_audio_inputs(
            input=input_file,
            spu_runner=self.spu_runner,
            n_frames=n_frames,
            input_sample_indices=input_sample_indices,
        )

        if len(self.comparisons) == 1 and "fasmir" in self.comparisons:
            print_header("Running Simulation")
            sim_result, sim_metrics = self.simulate(
                model_inputs=model_inputs,
                input_period=input_period,
            )
            self.write_metrics_to_disk(sim_metrics, output_dir=output_dir)
        elif len(self.comparisons) == 1:
            print_header(f"Executing runner {self.comparisons[0]} on {hardware}")

            result, runner = self.execute_runner(
                requested_runner=self.comparisons[0],
                model_inputs=model_inputs,
                noencrypt=noencrypt,
                hardware=hardware,
                dummy_output_file=dummy_output_file,
                debug_vars=debug_vars,
                debug_vars_fname=debug_vars_fname,
                zynq_host=zynq_host,
            )
            logger.info(f"Result of runner execution: {result}")

        elif len(self.comparisons) > 1:
            print_header("Running Comparisons")
            result = self.compare(
                runners_to_compare=self.comparisons,
                model_inputs=model_inputs,
                noencrypt=noencrypt,
                hardware=hardware,
                dummy_output_file=dummy_output_file,
                debug_vars=debug_vars,
                debug_vars_fname=debug_vars_fname,
                zynq_host=zynq_host,
            )
            self.print_comparison_results(result)

        return result

    def main(self, parsed_args) -> int:
        self.args = parsed_args
        args_dict = vars(self.args)

        return self.run(**args_dict)


def main(argv, model_source_dir=MODEL_SOURCE_DIR):
    parsed_args = Femtodriver._parse_args(argv)

    with Femtodriver(
        model_source_dir=model_source_dir,
        debug=parsed_args.debug,
        force_femtocrux_sim=parsed_args.force_femtocrux_sim,
        force_femtocrux_compile=parsed_args.force_femtocrux_compile,
    ) as fd:
        result = fd.main(parsed_args)

    if result == {}:  # no comparison performed, but clean exit
        return 0
    elif isinstance(result, dict) and "pass" in result:
        return not result["pass"]  #  0 = pass, 1 = no pass
    else:
        assert False and "got unexpected output from fd.main()"


def cli():
    main(sys.argv[1:])


if __name__ == "__main__":
    fd = Femtodriver()
    exit(fd.main(sys.argv[1:]))
