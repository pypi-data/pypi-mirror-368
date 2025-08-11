"""'Circle' Aigarth Intelligent Tissue Unit (AITU) definition."""

import logging
import random
import secrets
from enum import Enum
from pathlib import Path
from time import process_time
from typing import Any

from pydantic import BaseModel

from .aitu_base import AigarthITU
from .common import random_trit_vector
from .neuron_cl import AITClNeuron

LOG = logging.getLogger(Path(__file__).stem)


class AITUClMutationType(Enum):
    INPUT_WEIGHT = "input_weight"
    NEURON_SPAWN = "neuron_spawn"
    NEURON_REMOVE = "neuron_remove"


class AITUClMutationStatus(BaseModel):
    """AIT mutation status data."""

    type: AITUClMutationType | None = None
    base_neuron_index: int | None = None
    input_index: int | None = None
    input_weight_old: int | None = None
    input_weight_new: int | None = None
    inputs_total: int | None = None
    new_neuron_index: int | None = None
    neurons_total: int | None = None


class FFCYCLE_END_REASON:
    NO_OUTPUT_ZEROES = "All 'output' neurons got 'non-zero' state"
    TICK_CAP = "Tick cap reached"
    NO_NSTATE_SCHANGES = "None of AIT neurons changed their state"


class FFCycleStats(BaseModel):
    """AITU 'feedforward' cycle statistics container."""

    tick_count: int = 0
    end_reason: str = FFCYCLE_END_REASON.TICK_CAP
    duration_total: float = 0.0
    duration_tick: float = 0.0


class AigarthITUCl(AigarthITU):
    """'Circle' Aigarth Intelligent Tissue Unit (AITU) definition."""

    FF_CYCLE_CAP_BASE = 1000000

    def __init__(self, input_bitwidth: int | None = None, output_bitwidth: int | None = None) -> None:
        """Initialize AITU instance."""
        self.lm_prefix = f"{self.__class__.__name__}: "

        self.input_bitwidth = input_bitwidth if (isinstance(input_bitwidth, int) and input_bitwidth > 0) else 1
        self.output_bitwidth = output_bitwidth if (isinstance(output_bitwidth, int) and output_bitwidth > 0) else 1

        self.ff_cycle_cap = self.FF_CYCLE_CAP_BASE * self.output_bitwidth

        # AITU default initial (creation-time) configuration:
        #   * structure consists of 'input' and 'output' neurons only
        #   * all neurons have the only 'forward' input link assigned with randomly chosen weight
        #   * 'input' and 'output' neurons are randomly distributed across the 'tissue material'
        #
        # NOTES:
        #   * Number of 'input' and 'output' neurons (not necessarily, but) might be changed throughout AITU's
        #     lifecycle.
        #   * neuron input configurations (number of inputs, their weights and 'input skew') might be changed
        #     (if/as necessary) individually for each neuron throughout AITU's lifecycle.
        self._neurons_i = [AITClNeuron(input_weights=random_trit_vector(size=1)) for _ in range(self.input_bitwidth)]
        self._neurons_o = [AITClNeuron(input_weights=random_trit_vector(size=1)) for _ in range(self.output_bitwidth)]
        self._circle = self._neurons_i[:] + self._neurons_o[:]
        random.shuffle(self._circle)

    def mutate(self) -> AITUClMutationStatus:
        """Mutate.

        :return:    mutation status data object
        """
        # Identify a neuron's input weight to change
        idx_all_weights = []
        for ni, neuron in enumerate(self._circle):

            if len(neuron.input_weights) >= len(self._circle):
                ii_margin_base, ii_margin_odd = divmod(len(neuron.input_weights) - (len(self._circle) - 1), 2)
                ia_idx_start = ii_margin_base + ii_margin_odd
                ia_idx_end = ia_idx_start + (len(self._circle) - 1)
            else:
                ia_idx_start, ia_idx_end = 0, len(neuron.input_weights)

            for wi in range(ia_idx_start, ia_idx_end):
                idx_all_weights.append((ni, wi))

        idx_neuron, idx_weight = secrets.choice(idx_all_weights)

        # Change input weight
        weight_new = self._circle[idx_neuron]._input_weights[idx_weight] + secrets.choice((-1, 1))

        mutation_status = AITUClMutationStatus(
            base_neuron_index=idx_neuron,
            input_index=idx_weight,
            input_weight_old=self._circle[idx_neuron]._input_weights[idx_weight],
            input_weight_new=weight_new,
            inputs_total=len(self._circle[idx_neuron].input_weights),
        )

        if weight_new in (-1, 0, 1):
            self._circle[idx_neuron]._input_weights[idx_weight] = weight_new
            mutation_status.type = AITUClMutationType.INPUT_WEIGHT

            zero_input_weights = [iw for iw in self._circle[idx_neuron]._input_weights if iw == 0]
            if len(zero_input_weights) == len(self._circle[idx_neuron]._input_weights):
                if not (self._circle[idx_neuron] in self._neurons_i or self._circle[idx_neuron] in self._neurons_o):
                    # Remove the 'base' neuron, if removal condition met (all input weights are zero, and it's not a
                    # member of input or output neuron groups)
                    del self._circle[idx_neuron]
                    mutation_status.type = AITUClMutationType.NEURON_REMOVE
        else:
            # Spawn a neuron
            # Get a 'spawn model' neuron (the one to be cloned)
            neuron_smodel, _ = self.get_neuron_spawn_model(idx_neuron, idx_weight)
            # Clone the 'spawn  model' neuron
            neuron_new = neuron_smodel.__class__(
                input_weights=neuron_smodel.input_weights,
                input_skew=neuron_smodel.input_skew,
            )
            # Insert (just cloned) new neuron into the 'circle'
            idx_neuron_new = idx_neuron + 1  # Select location adjacent to the 'base' neuron
            self._circle.insert(idx_neuron_new, neuron_new)

            mutation_status.type = AITUClMutationType.NEURON_SPAWN
            mutation_status.new_neuron_index = idx_neuron_new

        # # Bump ICM version
        # self.meta.set_version(training_dataset_fpath=training_dataset_fpath, training_episode=training_episode)
        # LOG.info(f"{self.lm_prefix}Mutate ICM: uuid={self.meta.id}, version={str(self.meta.version_string)}: "
        #          f"Upgrade ICM version: version_new={str(self.meta.version_string)}, neurons={len(self._circle)}")
        #
        # LOG.info(
        #     f"{self.lm_prefix}Mutate ICM: uuid={self.meta.id}, version_new={str(self.meta.version_string)}, "
        #     f"neurons={len(self._circle)}: "
        #     f"training_dataset={str(training_dataset_fpath)}, {training_episode=}: OK"
        # )
        mutation_status.neurons_total = len(self._circle)

        return mutation_status

    def get_neuron_spawn_model(self, circle_index: int, weights_index: int) -> tuple[AITClNeuron, int]:
        """Get a neuron to serve as a model for spawning a new neuron as a part of AITU mutation procedure.

        :param circle_index:    index of a mutation 'base' neuron in the 'circle' (the one whose input's change
                                initiated spawning a new neuron)
        :param weights_index:   index of a mutation 'base' neuron's input in the 'weights' of the mutation 'base' neuron
                                (the one whose change initiated spawning a new neuron)
        :return:                'model' neuron for spawning a new neuron
        """
        neuron_base = self._circle[circle_index]
        len_bw_gr = neuron_base.input_split_index

        if weights_index < neuron_base.input_split_index:
            idx_neuron_spawn_model = (circle_index - len_bw_gr + weights_index) % len(self._circle)
        else:
            idx_neuron_spawn_model = (circle_index + 1 + weights_index - len_bw_gr) % len(self._circle)

        neuron_spawn_model = self._circle[idx_neuron_spawn_model]

        return neuron_spawn_model, idx_neuron_spawn_model

    def get_neuron_feed(self, circle_index: int) -> tuple[int, ...]:
        """Get 'feed' values for a neuron.

        :param circle_index:    neuron's index (location) on the 'circle'
        :return:                list of neuron feed values
        """
        n = self._circle[circle_index]

        oi_margin_base, oi_margin_odd = 0, 0
        if len(n.input_weights) >= len(self._circle):
            oi_margin_base, oi_margin_odd = divmod(len(n.input_weights) - (len(self._circle) - 1), 2)

        len_bw_gr = n.input_split_index
        len_fw_gr = len(n.input_weights) - n.input_split_index

        len_bw_gr_active = len_bw_gr - oi_margin_base - oi_margin_odd
        len_fw_gr_active = len_fw_gr - oi_margin_base

        bw_feed_active = [
            self._circle[i % len(self._circle)].state for i in range(circle_index - len_bw_gr_active, circle_index)
        ]
        bw_feed = [0] * (len_bw_gr - len_bw_gr_active) + bw_feed_active

        fw_feed_active = [
            self._circle[i % len(self._circle)].state
            for i in range(circle_index + 1, circle_index + 1 + len_fw_gr_active)
        ]
        fw_feed = fw_feed_active + [0] * (len_fw_gr - len_fw_gr_active)

        feed = bw_feed + fw_feed

        return tuple(feed)

    def feedforward(self, feed: tuple[int, ...] | None = None) -> tuple[tuple[int, ...], FFCycleStats]:
        """Produce a 'forward' value from the 'feed' data.

        :param feed:    set of balanced 'trit' values ([-1,0,+1]) fed to the AITU as input
        :return:        AITU's output computed from the input values (set of balanced 'trit' values)
        """
        # Reset states of all neurons
        for n in self._circle:
            n.state = 0
        # Assign AITU's 'feed' to initial states of 'input' neurons
        len_init = min(len(feed), self.meta.input_bitwidth)
        for i in range(len_init):
            self._neurons_i[i].state = feed[i]

        # Run 'feedforward' cycle
        ffcycle_end_reason = FFCYCLE_END_REASON.TICK_CAP
        ffcycle_start_timestamp = process_time()
        for tick in range(self.ff_cycle_cap):  # Ticking break condition #2: Ticks upper limit was reached
            no_n_state_changes = True
            no_zero_out_n_states = True
            # Compute 'next' state for all neurons (forward)
            for i, n in enumerate(self._circle):
                # Collect 'feed' for a neuron
                n_feed = self.get_neuron_feed(i)
                # Compute 'forward' for a neuron
                n.feedforward(n_feed)
            # Promote 'forward' to 'state' for all neurons
            for n in self._circle:
                n_state, changed = n.commit_state()
                if changed:
                    no_n_state_changes = False
            # Ticking break condition #3: no neurons have changed their state
            if no_n_state_changes:
                ffcycle_end_reason = FFCYCLE_END_REASON.NO_NSTATE_SCHANGES
                break
            # Ticking break condition #1: all 'output' neurons got non-zero state
            for n in self._neurons_o:
                if n.state == 0:
                    no_zero_out_n_states = False
                    break
            if no_zero_out_n_states:
                ffcycle_end_reason = FFCYCLE_END_REASON.NO_OUTPUT_ZEROES
                break

        ffcycle_stop_timestamp = process_time()
        # Extract AITU's 'forward' value from 'output' neurons
        aitu_forward = tuple([n.state for n in self._neurons_o])

        ffcycle_duration_total = ffcycle_stop_timestamp - ffcycle_start_timestamp
        ffcycle_tick_count = tick + 1
        ffcycle_stats = FFCycleStats(
            tick_count=ffcycle_tick_count,
            end_reason=ffcycle_end_reason,
            duration_total=ffcycle_duration_total,
            duration_tick=ffcycle_duration_total / ffcycle_tick_count,
        )

        return aitu_forward, ffcycle_stats

    def reflect(self, *args, **kwargs) -> Any:
        """Encode-transform-decode a single object of outer space."""
        raise NotImplementedError("reflect() not implemented.")

    def reflect_many(self, *args, **kwargs) -> Any:
        """Encode-transform-decode multiple objects of outer space."""
        raise NotImplementedError("reflect_many() not implemented.")
