from io import BytesIO
from typing import Any

import pandas as pd
from pandas.core.groupby import DataFrameGroupBy

from domain.entities.footfall import Footfall, OriginType
from ports.repositories.footfall_repository import FootfallRepository
from use_cases.exceptions import NotValidFileException


class ProcessFootfallsUseCase:
    def __init__(self, footfall_repository: FootfallRepository):
        self._footfall_repository = footfall_repository

    def __call__(self, file: BytesIO) -> None:
        df, groups = self._to_df(file)
        self._check_consecutive(groups)
        date_extremes = self._get_groups_date_extremes(groups)
        self._invalidate_existing_footfalls(date_extremes)
        footfalls = self._to_entities(df)
        self._footfall_repository.add_batch(footfalls)

    @staticmethod
    def _to_df(file: BytesIO) -> tuple[pd.DataFrame, DataFrameGroupBy]:  # type: ignore
        required_columns = [
            "from_date",
            "to_date",
            "people_in",
            "people_out",
            "wall_id",
        ]
        try:
            df = pd.read_csv(file)
            assert set(df.columns) == set(required_columns)
            for field_name in ("from_date", "to_date"):
                df[field_name] = pd.to_datetime(df[field_name])
            groups_by_walls = df.groupby("wall_id")
            return df, groups_by_walls
        except Exception:
            raise NotValidFileException

    @staticmethod
    def _check_consecutive(groups: DataFrameGroupBy) -> None:  # type: ignore
        for field_name in ("from_date", "to_date"):
            for group_name, group_data in groups:
                group_data = group_data.sort_values(by=field_name)
                time_diff = group_data[field_name].diff()
                consecutive_check = time_diff.dropna() == pd.Timedelta(hours=1)
                if not consecutive_check.all():
                    raise NotValidFileException

    @staticmethod
    def _get_groups_date_extremes(groups: DataFrameGroupBy) -> dict[str, Any]:  # type: ignore
        result = {}
        for group_name, group_data in groups:
            earliest_date = group_data["from_date"].min()
            latest_date = group_data["from_date"].max()
            result[str(group_name)] = {
                "start": earliest_date.to_pydatetime(),
                "end": latest_date.to_pydatetime(),
            }
        return result

    def _invalidate_existing_footfalls(self, groups: dict[str, Any]) -> None:
        for wall_id, dts in groups.items():
            self._footfall_repository.update(
                fields_to_update={"is_active": False},
                with_error=False,
                wall_id_filter=int(wall_id),
                start_date_between=(dts["start"], dts["end"]),
            )

    @staticmethod
    def _to_entities(df: pd.DataFrame) -> list[Footfall]:
        return [
            Footfall(
                start_datetime=row["from_date"].to_pydatetime(),
                end_datetime=row["to_date"].to_pydatetime(),
                people_in=row["people_in"],
                people_out=row["people_out"],
                wall_id=row["wall_id"],
                is_active=True,
                origin=OriginType.reconstruction,
            )
            for _, row in df.iterrows()
        ]
