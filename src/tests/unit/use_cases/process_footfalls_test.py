from io import BytesIO
from typing import Any

import pandas as pd
import pytest

from adapters.repositories.footfall_repository.mock_repository import (
    MockFootfallRepository,
)
from use_cases.exceptions import NotValidFileException
from use_cases.process_footfalls_use_case import ProcessFootfallsUseCase


@pytest.fixture
def process_footfall_use_case():
    return ProcessFootfallsUseCase(MockFootfallRepository())


@pytest.fixture
def data():
    return {
        "from_date": [
            "2024-02-09 12:00:00",
            "2024-02-09 13:00:00",
            "2024-02-09 12:00:00",
            "2024-02-09 13:00:00",
        ],
        "to_date": [
            "2024-02-09 13:00:00",
            "2024-02-09 14:00:00",
            "2024-02-09 13:00:00",
            "2024-02-09 14:00:00",
        ],
        "people_in": [0, 2, 13, 1],
        "people_out": [0, 0, 10, 1],
        "wall_id": [1, 1, 2, 2],
    }


def to_bytes_csv(data: dict[str, Any]) -> BytesIO:
    df = pd.DataFrame(data)
    csv_data = df.to_csv(index=False)
    csv_bytes = csv_data.encode("utf-8")
    return BytesIO(csv_bytes)


def test_process_footfall_column_missing(
    process_footfall_use_case: ProcessFootfallsUseCase, data: dict[str, Any]
):
    del data["from_date"]
    with pytest.raises(NotValidFileException):
        process_footfall_use_case(to_bytes_csv(data))


def test_process_footfall_datetime_not_valid(
    process_footfall_use_case: ProcessFootfallsUseCase, data: dict[str, Any]
):
    data["from_date"][0] = "not_valid"
    with pytest.raises(NotValidFileException):
        process_footfall_use_case(to_bytes_csv(data))


def test_process_footfall_datetime_not_consecutive(
    process_footfall_use_case: ProcessFootfallsUseCase, data: dict[str, Any]
):
    data["from_date"][2] = "2024-02-19 13:00:00"
    with pytest.raises(NotValidFileException):
        process_footfall_use_case(to_bytes_csv(data))


def test_process_footfall_success(
    process_footfall_use_case: ProcessFootfallsUseCase, data: dict[str, Any]
):
    assert process_footfall_use_case(to_bytes_csv(data)) is None  # type: ignore
