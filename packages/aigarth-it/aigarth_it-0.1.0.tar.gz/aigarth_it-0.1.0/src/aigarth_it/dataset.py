"""AITU input dataset tools."""

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel, field_validator


class ITUInputDatasetMeta(BaseModel):
    """Input dataset metadata."""

    metadata_size: ClassVar[int] = 6
    field_delimiter: ClassVar[str] = ","

    data_type: str
    data_source: str
    id: str
    timestamp: datetime
    record_fields: list[str]
    record_count: int | None = None
    digest: str

    @field_validator("timestamp", mode="before")
    @classmethod
    def validate_timestamp(cls, v: str) -> datetime:

        timestamp = datetime.fromisoformat(v)

        if timestamp.tzinfo is None:
            raise ValueError(f"Naive timestamps not supported: {v}")
        if timestamp.tzinfo is not timezone.utc:
            raise ValueError(f"Non UTC timestamps not supported: {v}")

        return timestamp

    @field_validator("record_fields", mode="before")
    @classmethod
    def validate_record_fields(cls, v: str) -> list[str]:
        return v.split()


def dataset_meta_csv(dataset_fpath: Path, hash_algorithm: str) -> ITUInputDatasetMeta:
    """Get metadata of a CSV-formatted dataset.

    :param dataset_fpath:   dataset file path
    :param hash_algorithm:  name of hashing algorithm supported by the 'hashlib' module to be used to compute
                            digest of dataset file
    :return:                dataset metadata object
    """
    with open(dataset_fpath, newline="") as csv_fh:
        ds_metadata_size = ITUInputDatasetMeta.metadata_size
        ds_field_delimiter = ITUInputDatasetMeta.field_delimiter

        ds_metadata_list = []
        while len(ds_metadata_list) < ds_metadata_size and (ds_metadata_row := csv_fh.readline()):
            ds_metadata_list.append(ds_metadata_row.split(ds_field_delimiter)[:2])

        ds_metadata_raw = dict(ds_metadata_list)

    with open(dataset_fpath, "rb") as fh:
        ds_digest = hashlib.file_digest(fh, hash_algorithm).hexdigest()

    ds_metadata = ITUInputDatasetMeta(**ds_metadata_raw, digest=ds_digest)

    return ds_metadata
