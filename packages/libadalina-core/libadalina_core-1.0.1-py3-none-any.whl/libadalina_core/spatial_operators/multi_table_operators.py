from enum import Enum

from .commons import DataFrame
from .single_table_operators import spatial_aggregation, AggregationFunction
import pyspark.sql as ps
import pyspark.sql.functions as func

from libadalina_core.sedona_utils import to_spark_dataframe
from sedona.sql import ST_Intersects

class JoinType(Enum):
    INNER = 'inner'
    LEFT = 'left'
    RIGHT = 'right'
    FULL = 'full'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

def spatial_join(
        left_table: DataFrame,
        right_table: DataFrame,
        join_type: JoinType = JoinType.INNER,
        aggregate: bool = False,
        aggregate_functions: list[AggregationFunction] | None = None
    ) -> ps.DataFrame:

    left_table = to_spark_dataframe(left_table)
    right_table = to_spark_dataframe(right_table)

    result = (left_table
              .withColumnRenamed('geometry', 'geometry_left')
              .join(right_table.withColumnRenamed('geometry', 'geometry_right'),
                    on=ST_Intersects(func.col('geometry_left'), func.col('geometry_right')), how=join_type.value)
              )

    if aggregate:
        if aggregate_functions is None:
            raise ValueError("aggregate_functions must be provided when aggregate is True")
        result = spatial_aggregation(result, aggregate_functions)

    return result

