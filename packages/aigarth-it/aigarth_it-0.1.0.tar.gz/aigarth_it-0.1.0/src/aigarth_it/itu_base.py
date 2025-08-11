"""Aigarth Intelligent Tissue Unit (AITU) base definition."""

import hashlib
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, ClassVar
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from .dataset import dataset_meta_csv
from .exceptions import AigarthITUError, PYDANTIC_ERRORS


class AigarthITU(ABC):
    """Base interface specification for Aigarth Intelligent Tissue Unit (AITU)."""

    @abstractmethod
    def mutate(self, *args, **kwargs) -> Any:
        """Mutate."""
        pass

    @abstractmethod
    def feedforward(self, *args, **kwargs) -> Any:
        """Produce a 'forward' value (AITU output) from the 'feed' data (AITU input)."""
        pass

    @abstractmethod
    def reflect(self, *args, **kwargs) -> Any:
        """Encode-transform-decode a single object of outer space."""
        pass

    @abstractmethod
    def reflect_many(self, *args, **kwargs) -> Any:
        """Encode-transform-decode multiple objects of outer space."""
        pass


class ITUVersion(BaseModel, validate_assignment=True):
    """ITU version."""

    # 'training_season' - id of training data set
    # Schema: <data type (target intelligent capability group)>-<data source>-<YYYYMMDDHHmmss>-<record count>'
    # Example: "ARITHMETIC_ADDITION-x.com-20250615193518-12"
    training_season: str = Field(frozen=True)
    # 'training_episode' - training 'episode' number (within a training season)
    training_episode: int = Field(default=0, frozen=True)
    # 'training_dataset_hash' - dataset file digest
    training_dataset_hash: str = Field(frozen=True)
    # 'training_complete' - True, if the 'ultimate' training level achieved for the training dataset
    training_complete: bool = Field(default=False)
    # 'version_major' - to be incremented for ITU design/API changes (ITU class version)
    version_major: int = Field(default=1, frozen=True)
    # 'version_minor' - to be incremented for each subsequent training season
    version_minor: int = Field(default=0, frozen=True)
    # 'version_micro' - to be incremented for every successful mutation within a 'training season'
    version_micro: int = Field(default=0, frozen=True)
    # 'note' - free form note for the ITU version
    note: str = Field(default="", frozen=True)
    # 'timestamp' - ITU version object creation timestamp
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), frozen=True)

    @field_validator("training_episode", "version_major", "version_minor", "version_micro")
    @classmethod
    def nonzero_positive_int(cls, v: int) -> int:
        """Verify that a value is non-zero positive integer."""
        if v <= 0:
            raise ValueError(f"Non-zero positive value is required: {v}")
        return v

    def __str__(self) -> str:
        """Get ITU version string."""
        version = f"{self.version_major}.{self.version_minor}.{self.version_micro}"
        return version


class ITUMeta(BaseModel):
    """ITU metadata."""

    tds_hash_algorithm: ClassVar[str] = "blake2b"  # hashing algorithm to verify identity of training datasets

    group: str = Field(frozen=True)  # Group of intelligent capabilities
    type: str = Field(frozen=True)  # ITU object class name
    input_bitwidth: int = Field(default=1, frozen=True)
    output_bitwidth: int = Field(default=1, frozen=True)
    uuid: UUID = Field(frozen=True)  # auto-set
    version_history: list[ITUVersion]  # auto-set

    @field_validator("input_bitwidth", "output_bitwidth")
    @classmethod
    def bitwidth(cls, v: int) -> int:
        """Verify that a bitwidth is non-zero positive integer."""
        if v <= 0:
            raise ValueError(f"Non-zero positive value is required: {v}")
        return v

    def __init__(self, **kwargs):
        kwargs["uuid"] = uuid4()
        now_utc = datetime.now(timezone.utc)
        kwargs["version_history"] = [
            ITUVersion(
                training_season=f"NB-void-{now_utc.strftime('%Y%m%d%H%M%S')}-0",
                training_dataset_hash="",
                training_complete=True,
                timestamp=now_utc,
            )
        ]
        super().__init__(**kwargs)

    @property
    def id(self) -> str:
        """ITU id."""
        return self.uuid.hex

    @property
    def version(self) -> ITUVersion:
        """ITU version object."""
        return self.version_history[-1]

    @property
    def version_string(self) -> str:
        """ITU version string."""
        return str(self.version)

    def _tds_identity(self, training_dataset_fpath: Path) -> tuple[str, str]:
        """Get training dataset identity information.

        :param training_dataset_fpath:  training dataset file path
        :return:                        TDS identity parameters
        """
        lm_prefix = f"{self.__class__.__name__}: Get TDS identity: "

        try:
            tds_meta = dataset_meta_csv(training_dataset_fpath, self.tds_hash_algorithm)
        except (OSError, ValueError) + PYDANTIC_ERRORS as e:
            raise AigarthITUError(
                f"{lm_prefix}Get training dataset metadata: {str(training_dataset_fpath)}: {e.__class__.__name__}: {e}"
            )
        training_season = tds_meta.id
        tds_digest = tds_meta.digest

        return training_season, tds_digest

    def set_version(
        self,
        training_episode: int,
        training_season: str | None = None,
        training_dataset_fpath: Path | None = None,
    ) -> None:
        """Set ITU version.

        !IMPORTANT! To avoid ITU version properties auto-calculation errors please make sure you do no run concurrent
                    training processes for the same ITU instance (UUID) across systems.

        :param training_episode:        number of training episode (within a training season)
        :param training_season:         training season id. If specified turns off training season id auto-discovery
                                        from a training dataset file.
        :param training_dataset_fpath:  training dataset file path
        """
        lm_prefix = f"{self.__class__.__name__}: Set version: "

        training_season_prev = self.version_history[-1].training_season
        training_dataset_hash_prev = self.version_history[-1].training_dataset_hash
        version_minor_prev = self.version_history[-1].version_minor
        version_micro_prev = self.version_history[-1].version_micro
        training_complete_prev = self.version_history[-1].training_complete

        # Verify value for the 'training episode'
        tds_current_episode = self.training_episode(training_season, training_dataset_fpath)
        if training_episode <= tds_current_episode:
            raise AigarthITUError(
                f"{lm_prefix}New value for training episode must be higher then the current one: {training_season=}, "
                f" episode_current={tds_current_episode}, episode_new={training_episode}"
            )

        if training_season:
            tds_digest = hashlib.new(self.tds_hash_algorithm, training_season.encode()).hexdigest()
        elif training_dataset_fpath:
            training_season, tds_digest = self._tds_identity(training_dataset_fpath=training_dataset_fpath)
        else:
            raise AigarthITUError(f"{lm_prefix}Either training_season or training_dataset_fpath is required")

        # Compute value for the minor version number
        if training_season == training_season_prev:
            if tds_digest == training_dataset_hash_prev:
                if training_complete_prev:
                    raise AigarthITUError(
                        f"{lm_prefix}Training already complete for the season: id={training_season}, "
                        f"digest={tds_digest}"
                    )
                else:
                    version_minor = version_minor_prev
            else:
                raise AigarthITUError(
                    f"{lm_prefix}Training dataset digest mismatch for the season: id={training_season}, "
                    f"digest={tds_digest}"
                )
        else:
            version_minor = version_minor_prev + 1

        # Compute value for the version micro number
        if tds_digest == training_dataset_hash_prev:
            version_micro = version_micro_prev + 1
        else:
            version_micro = 1

        version = ITUVersion(
            training_season=training_season,
            training_episode=training_episode,
            training_dataset_hash=tds_digest,
            version_minor=version_minor,
            version_micro=version_micro,
        )
        self.version_history.append(version)

    def training_episode(self, training_season: str | None = None, training_dataset_fpath: Path | None = None) -> int:
        """Get the most recent registered training episode value for a specific training season (dataset).

        !IMPORTANT! To avoid ITU 'base' training episode discovery errors please make sure you do no run concurrent
                    training processes for the same ITU instance (UUID) across systems.

        :param training_season:         training season id. If specified turns off training season id auto-discovery
                                        from a training dataset file.
        :param training_dataset_fpath:  training dataset file path
        :return:                        'base' training episode value
        """
        lm_prefix = f"{self.__class__.__name__}: Get training episode: "

        if training_season:
            tds_digest = hashlib.new(self.tds_hash_algorithm, training_season.encode()).hexdigest()
        elif training_dataset_fpath:
            training_season, tds_digest = self._tds_identity(training_dataset_fpath=training_dataset_fpath)
        else:
            raise AigarthITUError(f"{lm_prefix}Either training_season or training_dataset_fpath is required")

        # Search version history for the most recent occurrence of the training season
        for i in range(len(self.version_history) - 1, -1, -1):
            v = self.version_history[i]
            if v.training_season == training_season:
                if v.training_dataset_hash == tds_digest:
                    if v.training_complete:
                        raise AigarthITUError(
                            f"{lm_prefix}Training already complete for the season: id={training_season}, "
                            f"digest={tds_digest}"
                        )
                    else:
                        return v.training_episode
                else:
                    raise AigarthITUError(
                        f"{lm_prefix}Training dataset digest mismatch for the season: id={training_season}, "
                        f"digest={tds_digest}"
                    )

        # Training episode not in version history = start from scratch
        return 0

    def set_training_complete(self, training_complete: bool) -> None:
        """Set the 'training complete' flag for the current ITU's version."""
        self.version_history[-1].training_complete = training_complete
