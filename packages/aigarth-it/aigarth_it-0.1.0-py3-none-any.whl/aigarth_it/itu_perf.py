"""Aigarth Intelligent Tissue Unit (AITU) performance measurement tools."""

from typing import Any

from pydantic import BaseModel, Field

from .itu_cl import FFCycleStats


class ITUHitFactorsBin(BaseModel):
    """ITU reflection 'hit factors' for binary input."""

    gage_bitstring: str = ""  # "gage" value (bitstring)
    hitbit_count: int = 0
    hitbit_rate: float = 0.0  # hitbit_count / len(gage_bitstring) , interval [0, 1]
    unk_count: int = 0  # 'unknowns' count
    unk_rate: float = 0.0  # unk_count / len(gage_bitstring) , interval [0, 1]
    ffcycle_stats: FFCycleStats = Field(default_factory=FFCycleStats)
    ffcycle_rate: float = 0.0  # 1 / ffcycle_stats.tick_count , range [1, 0)
    perf_rate: float = 0.0  # aggregated performance rate of the individual ITU reflection operation
    # (Ex. perf_rate = hitbit_rate - unk_rate + ffcycle_rate).

    def model_post_init(self, __context: Any) -> None:
        """"""
        self.hitbit_rate = self.hitbit_count / len(self.gage_bitstring) if self.gage_bitstring else 0.0
        self.unk_rate = self.unk_count / len(self.gage_bitstring) if self.gage_bitstring else 0.0
        self.ffcycle_rate = 1 / self.ffcycle_stats.tick_count if self.ffcycle_stats.tick_count else 0.0
        self.perf_rate = self.hitbit_rate - self.unk_rate + self.ffcycle_rate


class ITUHitFactorsBinAggregate(BaseModel):
    """Aggregated ITU reflection 'hit factors' for binary input."""

    allbit_count: int = 0
    hitbit_count: int = 0
    hitbit_rate: float = 0.0
    unk_count: int = 0
    unk_rate: float = 0.0
    alltick_count: int = 0
    ffcycle_rate: float = 0.0
    perf_rate: float = 0.0

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization hook."""
        self.hitbit_rate = self.hitbit_count / self.allbit_count if self.allbit_count else 0.0
        self.unk_rate = self.unk_count / self.allbit_count if self.allbit_count else 0.0
        self.ffcycle_rate = 1 / self.alltick_count if self.alltick_count else 0.0

    def better_than(self, other: Any) -> bool | None:
        """Compare with other aggregated ITU reflection 'hit factors' object.

        :param other:   object to compare with
        :return:        True | False | None. None on reflection equality.
        """
        if self.__class__ != other.__class__:
            return False
        # Figure out supremacy
        if self.hitbit_count > other.hitbit_count:
            return True
        elif self.hitbit_count == other.hitbit_count:
            if self.unk_count > other.unk_count:
                # 'unknowns' are better that 'incorrects'
                return True
            if self.unk_count == other.unk_count:
                # Equal effectiveness
                return None
            else:
                return False
        else:
            return False
