from abc import abstractmethod
from typing import Optional

from typing_extensions import override

from databricks.ml_features_common.entities._feature_store_object import (
    _FeatureStoreObject,
)


class AggregationFunction(_FeatureStoreObject):
    """Abstract base class for all aggregation functions."""

    @abstractmethod
    def to_sql(self, column_name: str, timestamp_key: Optional[str] = None) -> str:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the aggregation function."""
        pass


class Avg(AggregationFunction):
    """Class representing the average (avg) aggregation function."""

    @override
    def to_sql(self, column_name: str, timestamp_key: Optional[str] = None) -> str:
        return f"AVG({column_name})"

    @property
    def name(self) -> str:
        return "avg"


class Count(AggregationFunction):
    """Class representing the count aggregation function."""

    @override
    def to_sql(self, column_name: str, timestamp_key: Optional[str] = None) -> str:
        return f"COUNT({column_name})"

    @property
    def name(self) -> str:
        return "count"


class ApproxCountDistinct(AggregationFunction):
    """
    Class representing the approximate count distinct aggregation function.
    See https://docs.databricks.com/en/sql/language-manual/functions/approx_count_distinct.html

    :param relativeSD: The relative standard deviation allowed in the approximation.
    """

    def __init__(self, relativeSD: Optional[float] = None):
        if relativeSD is not None and not isinstance(relativeSD, float):
            raise ValueError("relativeSD must be a float if supplied.")
        self._relativeSD = relativeSD

    @property
    def name(self) -> str:
        return "approx_count_distinct"

    @property
    def relativeSD(self) -> Optional[float]:
        return self._relativeSD

    @override
    def to_sql(self, column_name: str, timestamp_key: Optional[str] = None) -> str:
        if self._relativeSD:
            return f"APPROX_COUNT_DISTINCT({column_name}, {self._relativeSD})"
        return f"APPROX_COUNT_DISTINCT({column_name})"


class PercentileApprox(AggregationFunction):
    """
    Class representing the percentile approximation aggregation function.
    See https://docs.databricks.com/en/sql/language-manual/functions/approx_percentile.html

    :param percentile: The percentile to approximate.
    :param accuracy: The accuracy of the approximation.
    """

    def __init__(self, percentile: float, accuracy: Optional[int] = None):
        if not isinstance(percentile, float):
            raise ValueError("percentile must be a float.")
        if accuracy is not None and not isinstance(accuracy, int):
            raise ValueError("accuracy must be an integer if supplied.")
        self._percentile = percentile
        self._accuracy = accuracy

    @property
    def name(self) -> str:
        return "percentile_approx"

    @property
    def percentile(self) -> float:
        return self._percentile

    @property
    def accuracy(self) -> Optional[int]:
        return self._accuracy

    @override
    def to_sql(self, column_name: str, timestamp_key: Optional[str] = None) -> str:
        if self._accuracy:
            return f"PERCENTILE_APPROX({column_name}, {self._percentile}, {self._accuracy})"
        return f"PERCENTILE_APPROX({column_name}, {self._percentile})"


class First(AggregationFunction):
    """Class representing the first aggregation function."""

    @override
    def to_sql(self, column_name: str, timestamp_key: Optional[str] = None) -> str:
        if not timestamp_key:
            raise ValueError(
                "timestamp_key must be supplied for First aggregation function."
            )
        return f"MIN_BY({column_name}, {timestamp_key})"

    @property
    def name(self) -> str:
        return "first"


class Last(AggregationFunction):
    """Class representing the last aggregation function."""

    @override
    def to_sql(self, column_name: str, timestamp_key: Optional[str] = None) -> str:
        if not timestamp_key:
            raise ValueError(
                "timestamp_key must be supplied for Last aggregation function."
            )
        return f"MAX_BY({column_name}, {timestamp_key})"

    @property
    def name(self) -> str:
        return "last"


class Max(AggregationFunction):
    """Class representing the maximum (max) aggregation function."""

    @override
    def to_sql(self, column_name: str, timestamp_key: Optional[str] = None) -> str:
        return f"MAX({column_name})"

    @property
    def name(self) -> str:
        return "max"


class Min(AggregationFunction):
    """Class representing the minimum (min) aggregation function."""

    @override
    def to_sql(self, column_name: str, timestamp_key: Optional[str] = None) -> str:
        return f"MIN({column_name})"

    @property
    def name(self) -> str:
        return "min"


class StddevPop(AggregationFunction):
    """Class representing the population standard deviation (stddev_pop) aggregation function."""

    @override
    def to_sql(self, column_name: str, timestamp_key: Optional[str] = None) -> str:
        return f"STDDEV_POP({column_name})"

    @property
    def name(self) -> str:
        return "stddev_pop"


class StddevSamp(AggregationFunction):
    """Class representing the sample standard deviation (stddev_samp) aggregation function."""

    @override
    def to_sql(self, column_name: str, timestamp_key: Optional[str] = None) -> str:
        return f"STDDEV_SAMP({column_name})"

    @property
    def name(self) -> str:
        return "stddev_samp"


class Sum(AggregationFunction):
    """Class representing the sum aggregation function."""

    @override
    def to_sql(self, column_name: str, timestamp_key: Optional[str] = None) -> str:
        return f"SUM({column_name})"

    @property
    def name(self) -> str:
        return "sum"


class VarPop(AggregationFunction):
    """Class representing the population variance (var_pop) aggregation function."""

    @override
    def to_sql(self, column_name: str, timestamp_key: Optional[str] = None) -> str:
        return f"VAR_POP({column_name})"

    @property
    def name(self) -> str:
        return "var_pop"


class VarSamp(AggregationFunction):
    """Class representing the sample variance (var_samp) aggregation function."""

    @override
    def to_sql(self, column_name: str, timestamp_key: Optional[str] = None) -> str:
        return f"VAR_SAMP({column_name})"

    @property
    def name(self) -> str:
        return "var_samp"


# Mapping from shorthand strings to instances of corresponding classes
# Only include aggregations that don't require additional arguments
AGGREGATION_FUNCTION_BY_SHORTHAND = {
    "mean": Avg(),
    "avg": Avg(),
    "count": Count(),
    "first": First(),
    "last": Last(),
    "max": Max(),
    "min": Min(),
    "stddev_pop": StddevPop(),
    "stddev_samp": StddevSamp(),
    "sum": Sum(),
    "var_pop": VarPop(),
    "var_samp": VarSamp(),
    "approx_count_distinct": ApproxCountDistinct(),
}
