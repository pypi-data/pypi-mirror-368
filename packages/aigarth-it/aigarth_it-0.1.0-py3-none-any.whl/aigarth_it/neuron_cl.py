"""'Circle' AIT neuron."""

from itertools import zip_longest, starmap

from .common import ternary_clamp
from .exceptions import AigarthITUError


class AITClNeuron:
    """'Circle' AIT neuron."""

    def __init__(self, input_weights: list[int] | None = None, input_skew: int = 0) -> None:
        """Initialize 'Circle' AIT neuron.

        :param input_weights:   input weight values (expected to be balanced 'trit' values - [-1, 0, +1])
        :param input_skew:      difference between number of inputs assigned to 'backward' and 'forward' input groups.
                                The 'backward' input group is 'connected' to neurons sitting on lower AITU 'circle'
                                indices as compared with this neuron's index. 'Forward' input group is 'connected' to
                                neurons sitting on higher AITU 'circle' indices as compared with this neuron's index.
                                '0' - inputs assigned equally. The last odd input (if any) goes to the 'forward' input
                                      group.
                                positive numer - assign this more inputs to the 'forward' input group.
                                negative numer - assign this more inputs to the 'backward' input group.
                                NOTE. Naturally, the range of absolute 'input_skew' values is limited by total number of
                                      inputs.
        """
        self.lm_prefix = f"{self.__class__.__name__}: "
        # NOTE. A neuron 'has' as many inputs as the number of input weights.
        self._input_weights: list[int] = [ternary_clamp(int(w)) for w in input_weights] if input_weights else [1]
        self._input_skew: int = int(input_skew)
        # 'Input split index' is an index of the first input belonging to the 'forward' input group.
        # The condition must be met: 0 <= self._input_split_index <= len(self._input_weights)
        self._input_split_index: int = self._get_input_split_index(
            input_count=len(self._input_weights), input_skew=self._input_skew
        )
        self._state_next: int | None = None
        self._state: int = 0

    @staticmethod
    def _get_input_split_index(input_count: int, input_skew: int) -> int:
        """Compute input split index.

        :param input_count: total number of neuron 'inputs'
        :param input_skew:  'input skew' value
        :return:            'input split index' value
        """
        if int(input_count) <= 0:
            raise ValueError(f"'input_count' must be greater than 0: {input_count}")

        input_min_index, input_max_index = 0, input_count
        input_split_index = max(input_min_index, min(input_max_index, input_count // 2 - int(input_skew)))

        return input_split_index

    @property
    def input_weights(self) -> list[int]:
        """Get input weights."""
        return self._input_weights

    @input_weights.setter
    def input_weights(self, input_weights: list[int] | None) -> None:
        """Set input weights.

        :param input_weights: input weight values
        """
        self._input_weights = [ternary_clamp(int(w)) for w in input_weights] if input_weights else [1]
        self._input_split_index = self._get_input_split_index(
            input_count=len(self._input_weights), input_skew=self._input_skew
        )

    @property
    def input_skew(self) -> int:
        """Get 'input skew' value."""
        return self._input_skew

    @input_skew.setter
    def input_skew(self, input_skew: int | None) -> None:
        """Set 'input skew' value.

        :param input_skew: 'input skew' value
        """
        self._input_skew = int(input_skew) if input_skew else 0
        self._input_split_index = self._get_input_split_index(
            input_count=len(self._input_weights), input_skew=self._input_skew
        )

    @property
    def input_split_index(self) -> int:
        """Get neuron's 'input split index' value."""
        return self._input_split_index

    @property
    def state(self) -> int:
        """Get neuron's state."""
        return self._state

    @state.setter
    def state(self, state: int | None) -> None:
        """Set state.

        :param state: state value (balanced trit)
        """
        self._state = ternary_clamp(int(state)) if state else 0

    def feedforward(self, feed: tuple[int, ...] | None = None):
        """Produce a 'forward' value from the 'feed' data and preserve it internally as the 'next' value
        of neurons' 'state' (balanced trit value - [-1, 0, +1]).

        :param feed:    set of balanced trit values ([-1, 0, +1]) fed to the neuron as input
        """
        feed = feed or tuple()
        len_iw = len(self.input_weights)
        len_feed = len(feed)

        if len_iw <= len_feed:
            zipped = zip(feed, self.input_weights)
        else:
            zipped = zip_longest(feed, self.input_weights, fillvalue=0)

        products = starmap(lambda x, y: x * y, zipped)

        sum_prods = sum(products)

        forward = ternary_clamp(sum_prods)

        self._state_next = forward

    def commit_state(self) -> tuple[int, bool]:
        """Commit the preserved neuron's 'next' state value.

        :return: neuron's state data
        """
        if self._state_next is None:
            raise AigarthITUError(f"{self.lm_prefix}Commit neuron state: Next state is not defined")
        else:
            state_changed = self._state_next != self._state
            self._state = self._state_next
            self._state_next = None

        return self._state, state_changed
