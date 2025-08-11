import datetime
from typing import Optional, Union

from databricks.ml_features.entities.aggregation_function import (
    AGGREGATION_FUNCTION_BY_SHORTHAND,
    AggregationFunction,
)
from databricks.ml_features_common.entities._feature_store_object import (
    _FeatureStoreObject,
)

MIN_TIME_UNIT = datetime.timedelta(seconds=1)


def _format_simple_timedelta(delta: datetime.timedelta) -> Optional[str]:
    total_seconds = delta.total_seconds()
    assert total_seconds >= 0

    if total_seconds % 86400 == 0:
        days = total_seconds // 86400
        return f"{int(days)}d"

    elif total_seconds % 3600 == 0:
        hours = total_seconds // 3600
        return f"{int(hours)}h"

    return None


class Window(_FeatureStoreObject):
    """
    Defines an aggregation window.

    :param duration: The length of the time window. This defines how far back in time the window spans from the
        requested time. This must be positive. The interval defined by this window includes the start (earlier in time)
        endpoint, but not the end (later in time) endpoint. That is, the interval is [ts - duration, ts).
    :param offset: Optional offset to adjust the end of the window. This can be used to shift the window by a certain
        duration backwards. This must be non-positive if provided. Defaults to 0.
    """

    def __init__(
        self,
        *,
        duration: datetime.timedelta,
        offset: Optional[datetime.timedelta] = None,
    ):
        """Initialize a Window object. See class documentation."""
        self._duration = duration
        self._offset = offset if offset is not None else datetime.timedelta(0)

        self._validate_parameters()

    @property
    def duration(self) -> datetime.timedelta:
        """The length of the time window."""
        return self._duration

    @property
    def offset(self) -> datetime.timedelta:
        """The offset to adjust the end of the window."""
        return self._offset

    def _validate_parameters(self):
        """Validates the parameters provided to the Window class."""
        if not isinstance(
            self._duration, datetime.timedelta
        ) or self._duration <= datetime.timedelta(0):
            raise ValueError("The 'duration' must be a positive datetime.timedelta.")

        if not isinstance(
            self._offset, datetime.timedelta
        ) or self._offset > datetime.timedelta(0):
            raise ValueError("The 'offset' must be non-positive if provided.")

        if self._duration % MIN_TIME_UNIT != datetime.timedelta(0):
            raise ValueError(
                f"The 'duration' {self._duration} must be divisible by {MIN_TIME_UNIT}."
            )

        if self._offset % MIN_TIME_UNIT != datetime.timedelta(0):
            raise ValueError(
                f"The 'offset' {self._offset} must be divisible by {MIN_TIME_UNIT}."
            )


class Aggregation(_FeatureStoreObject):
    """
    Defines a single aggregated feature.

    :param column: The source column to aggregate. The column must exist in the parent FeatureAggregation source_table.
    :param output_column: The output column name. If not provided, a default name will be generated.
    :param function: The function to use. If a string is given, it will be interpreted as short-hand (e.g., "sum", "avg", "count").
    :param window: The time window to aggregate data with.
    """

    def __init__(
        self,
        *,
        column: str,
        output_column: Optional[str] = None,
        function: Union[str, AggregationFunction],
        window: Window,
    ):
        """Initialize an Aggregation object. See class documentation."""
        self._column = column
        if isinstance(function, str):
            if function.lower() not in AGGREGATION_FUNCTION_BY_SHORTHAND:
                raise ValueError(f"Invalid aggregation function: {function}.")

            self._function = AGGREGATION_FUNCTION_BY_SHORTHAND[function.lower()]

        else:
            self._function = function

        self._window = window

        # If output_column is not provided, generate a default output column name.
        self._output_column = (
            output_column
            if output_column
            else self._generate_default_output_column_name()
        )

    @property
    def column(self) -> str:
        """The source column to aggregate."""
        return self._column

    @property
    def output_column(self) -> str:
        """The output column name."""
        return self._output_column

    @property
    def function(self) -> AggregationFunction:
        """The aggregation function to use."""
        return self._function

    @property
    def window(self) -> Window:
        """The time window to aggregate data with."""
        return self._window

    def _generate_default_output_column_name(self) -> str:
        """
        Generates a default output column name.

        :return: A string representing the default output column name.
        """
        duration_str = _format_simple_timedelta(self._window.duration)
        offset_str = (
            _format_simple_timedelta(-self._window.offset)
            if self._window.offset != datetime.timedelta(0)
            else ""
        )
        if duration_str is None or offset_str is None:
            raise ValueError(
                f"Cannot auto-generate output column name for input column {self._column} with duration {self._window.duration} and offset {-self._window.offset} because the duration or offset contains fractional hours. Please specify output_column explicitly."
            )

        if offset_str:
            offset_str = f"_offset_{offset_str}"

        return f"{self._column}_{self._function.name}_{duration_str}{offset_str}"
