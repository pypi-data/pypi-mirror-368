"""FemtoRunner runtimes for FQIR"""

import logging
import copy
from femtorun import FemtoRunner

logger = logging.getLogger(__name__)


class FQIRArithRunner(FemtoRunner):
    """Runs the FQIR arithmetic subgraph runtime

    Args:
        fqir : (:obj:`FQIR`) : main FQIR graph object

    High-level (numpy) interface:
        These implement the base class FemtoRunner interfaces, as required. These interfaces work
        on numpy data, and are meant to be runnable side-by-side with other FemtoRunners.

        * :func:`step`: run one timestep, takes numpy, returns numpy
        * :func:`run`: call step over multiple time steps,
          takes numpy arrays with a time dimension
        * :func:`reset`: initialize simulation
        * :func:`finish`: exit the simulator cleanly
    """

    def __init__(self, fqir, plus_k=0):
        self.fqir = fqir
        self.fqir_state = None
        self.plus_k = plus_k
        super().__init__(None, None)

    def reset(self):
        # get initial state for the fqir runtime
        if "INIT" in self.fqir.subgraphs:
            __, self.fqir_state = self.fqir.subgraphs["INIT"].run(return_objs=True)
            # XXX do something for FMIR?
            # FQIR init seems to always clear to zero right now, so by coincidence we don't
        else:
            self.fqir_state = {}

    def finish(self):
        pass

    def step(self, inputs):
        # invoke fqir runtime at single time-step, carrying state over
        # no padding/unpadding for FQIR

        input_t = list(inputs.values())
        output_t, self.fqir_state = self.fqir.subgraphs["ARITH"].run(
            *input_t, return_dict=True, return_objs=True, state=self.fqir_state
        )

        for k, v in output_t.items():
            output_t[k] = v + self.plus_k

        return output_t, copy.copy(self.fqir_state)
