#  Copyright Femtosense 2024
#
#  By using this software package, you agree to abide by the terms and conditions
#  in the license agreement found at https://femtosense.ai/legal/eula/
#

"""FemtoRunner for Femtocrux simulator"""
import logging
import copy
from femtorun import FemtoRunner
from femtocrux import CompilerClient, FQIRModel
import numpy as np
import torch

logger = logging.getLogger(__name__)


class FXRunner(FemtoRunner):
    def __init__(
        self,
        fqir,
        compiler_client: CompilerClient,
        batch_dim=0,
        sequence_dim=1,
        input_padding=None,
        output_padding=None,
        compiler_args=None,
        input_period=None,
    ):
        self.fqir = fqir
        self.batch_dim = batch_dim
        self.sequence_dim = sequence_dim
        self.compiler_args = compiler_args

        # connect to docker
        self.client = compiler_client

        self.sim_report = None  # will fill in with run()
        self.input_period = input_period

        super().__init__(input_padding, output_padding)

    def reset(self):
        # XXX HACK!
        # for some reason, we need the FS Quantizer to
        # de-floatify the inputs to the model
        # to make quantization have no effect, we hack the FQIR
        arith = self.fqir.subgraphs["ARITH"]
        for x in arith.inputs:
            x.quanta = 0  # scale = 2**quanta = 1 (I don't think this is the correct defn of quanta...)

        # get clean simulator object
        self.simulator = self.client.get_simulator_object(
            FQIRModel(
                self.fqir,
                batch_dim=self.batch_dim,
                sequence_dim=self.sequence_dim,
            ),
            options=self.compiler_args,
        )

    def finish(self):
        pass

    def step(self, inputs):
        # we will just override run(), the docker's interface is more like that
        raise NotImplementedError(
            "FXRunner can only do run(), no fine-grained step() calls"
        )

    def run(
        self, input_dict: dict[str, np.ndarray[np.int16] | torch.Tensor]
    ) -> tuple[dict[str, np.ndarray[np.int16]], dict[str, np.ndarray[np.int16]], bool]:
        """
        run() now supports multiple inputs and returns multiple outputs

        input_dict should follow the format of
        {"input_name1": np.ndarray(int16 types ...),
         "input_name2": np.ndarray([int16 types ...])
        }

        The input names must match the names in the forward function of the torch model. The outputs will
        be named according to the fmot tags. Please read the documentation for a full example of this.
        """
        # run the simulator
        client_outputs, self.sim_report = self.simulator.simulate(
            input_dict,
            input_period=self.input_period,
        )

        output_always_valid_mask = {k: [True] * v for k, v in client_outputs.items()}
        internal_vals = {}

        return client_outputs, internal_vals, output_always_valid_mask
