#
# DATABRICKS CONFIDENTIAL & PROPRIETARY
# __________________
#
# Copyright 2020-present Databricks, Inc.
# All Rights Reserved.
#
# NOTICE:  All information contained herein is, and remains the property of Databricks, Inc.
# and its suppliers, if any.  The intellectual and technical concepts contained herein are
# proprietary to Databricks, Inc. and its suppliers and may be covered by U.S. and foreign Patents,
# patents in process, and are protected by trade secret and/or copyright law. Dissemination, use,
# or reproduction of this information is strictly forbidden unless prior written permission is
# obtained from Databricks, Inc.
#
# If you view or obtain a copy of this information and believe Databricks, Inc. may not have
# intended it to be made available, please promptly report it to Databricks Legal Department
# @ legal@databricks.com.
#
import sys
from inspect import getfullargspec
from typing import TYPE_CHECKING, Union

from pyspark import since, SparkContext
from pyspark.sql.types import ArrayType, StringType, StructType, BinaryType, MapType
from pyspark.sql.column import Column, _create_column_from_literal, _to_java_column
from pyspark.sql.pandas.functions import _create_pandas_udf
from pyspark.sql.udf import _create_udf
from pyspark.sql.pandas.utils import require_minimum_pandas_version, require_minimum_pyarrow_version

from pyspark.databricks.sql.h3_functions import (  # noqa: F401
    h3_boundaryasgeojson,  # noqa: F401
    h3_boundaryaswkb,  # noqa: F401
    h3_boundaryaswkt,  # noqa: F401
    h3_centerasgeojson,  # noqa: F401
    h3_centeraswkb,  # noqa: F401
    h3_centeraswkt,  # noqa: F401
    h3_compact,  # noqa: F401
    h3_distance,  # noqa: F401
    h3_h3tostring,  # noqa: F401
    h3_hexring,  # noqa: F401
    h3_ischildof,  # noqa: F401
    h3_ispentagon,  # noqa: F401
    h3_isvalid,  # noqa: F401
    h3_kring,  # noqa: F401
    h3_kringdistances,  # noqa: F401
    h3_longlatash3,  # noqa: F401
    h3_longlatash3string,  # noqa: F401
    h3_maxchild,  # noqa: F401
    h3_minchild,  # noqa: F401
    h3_pointash3,  # noqa: F401
    h3_pointash3string,  # noqa: F401
    h3_polyfillash3,  # noqa: F401
    h3_polyfillash3string,  # noqa: F401
    h3_resolution,  # noqa: F401
    h3_stringtoh3,  # noqa: F401
    h3_tochildren,  # noqa: F401
    h3_toparent,  # noqa: F401
    h3_try_polyfillash3,  # noqa: F401
    h3_try_polyfillash3string,  # noqa: F401
    h3_try_validate,  # noqa: F401
    h3_uncompact,  # noqa: F401
    h3_validate,  # noqa: F401
)  # noqa: F401

if TYPE_CHECKING:
    from pyspark.sql._typing import ColumnOrName


@since("3.0.1")
def unwrap_udt(col):
    """
    Unwrap UDT data type column into its underlying struct type
    """
    sc = SparkContext._active_spark_context
    jc = sc._jvm.com.databricks.sql.DatabricksFunctions.unwrap_udt(_to_java_column(col))
    return Column(jc)


def _create_edge_udf(f, returnType, evalType):
    # The following table shows most of Pandas data and SQL type conversions in Python UDFs with
    # Arrow enabled, that are not yet visible to the user. Some of behaviors are buggy and
    # might be changed in the near future. The table might have to be eventually documented
    # externally. Please see SC-70036's PR to see the codes in order to generate the table below.
    #
    # +-----------------------------+--------------+------------------+--------------------+------+--------------------+-----------------------------+----------+----------------------+------------------+------------------+----------------------------+--------------------+--------------+  # noqa
    # |SQL Type \ Python Value(Type)|None(NoneType)|        True(bool)|              1(int)|a(str)|    1970-01-01(date)|1970-01-01 00:00:00(datetime)|1.0(float)|array('i', [1])(array)|         [1](list)|       (1,)(tuple)|bytearray(b'ABC')(bytearray)|          1(Decimal)|{'a': 1}(dict)|  # noqa
    # +-----------------------------+--------------+------------------+--------------------+------+--------------------+-----------------------------+----------+----------------------+------------------+------------------+----------------------------+--------------------+--------------+  # noqa
    # |                      boolean|          None|              True|                True|     X|                   X|                            X|      True|                     X|                 X|                 X|                           X|                   X|             X|  # noqa
    # |                      tinyint|          None|                 1|                   1|     X|                   X|                            X|         1|                     X|                 X|                 X|                           X|                   1|             X|  # noqa
    # |                     smallint|          None|                 1|                   1|     X|                   X|                            X|         1|                     X|                 X|                 X|                           X|                   1|             X|  # noqa
    # |                          int|          None|                 1|                   1|     X|                   X|                            X|         1|                     X|                 X|                 X|                           X|                   1|             X|  # noqa
    # |                       bigint|          None|                 1|                   1|     X|                   X|                            0|         1|                     X|                 X|                 X|                           X|                   1|             X|  # noqa
    # |                       string|          None|            'True'|                 '1'|   'a'|        '1970-01-01'|         '1970-01-01 00:00...|     '1.0'|     "array('i', [1])"|             '[1]'|            '(1,)'|         "bytearray(b'ABC')"|                 '1'|    "{'a': 1}"|  # noqa
    # |                         date|          None|                 X|                   X|     X|datetime.date(197...|         datetime.date(197...|         X|                     X|                 X|                 X|                           X|datetime.date(197...|             X|  # noqa
    # |                    timestamp|          None|                 X|datetime.datetime...|     X|                   X|         datetime.datetime...|         X|                     X|                 X|                 X|                           X|datetime.datetime...|             X|  # noqa
    # |                        float|          None|               1.0|                 1.0|     X|                   X|                            X|       1.0|                     X|                 X|                 X|                           X|                   X|             X|  # noqa
    # |                       double|          None|               1.0|                 1.0|     X|                   X|                            X|       1.0|                     X|                 X|                 X|                           X|                   X|             X|  # noqa
    # |                       binary|          None|bytearray(b'\x00')|  bytearray(b'\x00')|     X|                   X|                            X|         X|  bytearray(b'\x01\...|bytearray(b'\x01')|bytearray(b'\x01')|           bytearray(b'ABC')|                   X|             X|  # noqa
    # |                decimal(10,0)|          None|                 X|                   X|     X|                   X|                            X|         X|                     X|                 X|                 X|                           X|        Decimal('1')|             X|  # noqa
    # +-----------------------------+--------------+------------------+--------------------+------+--------------------+-----------------------------+----------+----------------------+------------------+------------------+----------------------------+--------------------+--------------+  # noqa
    #
    # Note: DDL formatted string is used for 'SQL Type' for simplicity. This string can be
    #       used in `returnType`.
    # Note: The values inside of the table are generated by `repr`.
    # Note: Python 3.8.6, Pandas 1.2.1 and PyArrow 2.0.0 are used.
    # Note: Timezone is KST.
    # Note: 'X' means it throws an exception during the conversion.
    from pyspark.sql import SparkSession

    session = SparkSession._instantiatedSession
    is_arrow_enabled = (
        session is not None
        and session.conf.get("spark.databricks.execution.pythonUDF.arrow.enabled") == "true"
    )
    regular_udf = _create_udf(f, returnType, evalType)
    return_type = regular_udf.returnType
    try:
        is_func_with_args = len(getfullargspec(f).args) > 0
    except TypeError:
        is_func_with_args = False
    is_output_atomic_type = (
        not isinstance(return_type, StructType)
        and not isinstance(return_type, MapType)
        and not isinstance(return_type, ArrayType)
    )

    if is_arrow_enabled and is_output_atomic_type and is_func_with_args:
        require_minimum_pandas_version()
        require_minimum_pyarrow_version()

        import pandas as pd

        def result_func(pdf):
            return pdf

        if type(return_type) == StringType:

            def result_func(r):
                return str(r) if r is not None else r

        elif type(return_type) == BinaryType:

            def result_func(r):
                return bytes(r) if r is not None else r

        def vectorized_udf(*args: pd.Series) -> pd.Series:
            if any(map(lambda arg: isinstance(arg, pd.DataFrame), args)):
                raise NotImplementedError(
                    "Struct input type are not supported with Arrow optimization "
                    "enabled in Python UDFs. Disable "
                    "'spark.databricks.execution.pythonUDF.arrow.enabled' to workaround."
                )
            # Always cast because regular UDF supports more permissive casting
            # compared to pandas UDFs. This is to don't break the user's codes
            # from enabling this edge feature.
            return pd.Series(result_func(f(*a)) for a in zip(*args))

        # Regular UDFs can take callable instances too.
        vectorized_udf.__name__ = f.__name__ if hasattr(f, "__name__") else f.__class__.__name__
        vectorized_udf.__module__ = (
            f.__module__ if hasattr(f, "__module__") else f.__class__.__module__
        )
        vectorized_udf.__doc__ = f.__doc__
        pudf = _create_pandas_udf(vectorized_udf, returnType, None)
        # Keep the attributes as if this is a regular Python UDF.
        pudf.func = f
        pudf.returnType = return_type
        pudf.evalType = regular_udf.evalType
        return pudf
    else:
        return regular_udf


def approx_top_k(
    col: "ColumnOrName",
    k: Union[Column, int] = 5,
    maxItemsTracked: Union[Column, int] = 10000,
) -> Column:
    """Returns the top `k` most frequently occurring item values in a string, boolean, date,
    timestamp, or numeric column `col` along with their approximate counts. The error in each count
    may be up to `2.0 * numRows / maxItemsTracked` where `numRows` is the total number of rows.
    `k` (default: 5) and `maxItemsTracked` (default: 10000) are both integer parameters.
    Higher values  of `maxItemsTracked` provide better accuracy at the cost of increased memory
    usage. Columns that have fewer than `maxItemsTracked` distinct items will yield exact item
    counts.  NULL values are included as their own value in the results.

    Results are returned as an array of structs containing `item` values (with their original input
    type) and their occurrence `count` (long type), sorted by count descending.

    .. versionadded:: 3.3.0

    Examples
    --------
    >>> from pyspark.sql.functions import col
    >>> item = (col("id") % 3).alias("item")
    >>> df = spark.range(0, 1000, 1, 1).select(item)
    >>> df.select(
    ...    approx_top_k("item", 5).alias("top_k")
    ... ).printSchema()
    root
     |-- top_k: array (nullable = true)
     |    |-- element: struct (containsNull = true)
     |    |    |-- item: long (nullable = true)
     |    |    |-- count: long (nullable = true)
    """
    sc = SparkContext._active_spark_context
    assert sc is not None and sc._jvm is not None

    k_col = _to_java_column(k) if isinstance(k, Column) else _create_column_from_literal(k)
    max_items_tracked_col = (
        _to_java_column(maxItemsTracked)
        if isinstance(maxItemsTracked, Column)
        else _create_column_from_literal(maxItemsTracked)
    )
    jc = sc._jvm.com.databricks.sql.DatabricksFunctions.approx_top_k(
        _to_java_column(col), k_col, max_items_tracked_col
    )
    return Column(jc)


def _test() -> None:
    import doctest
    from pyspark.sql import SparkSession
    import pyspark.sql.functions

    globs = pyspark.databricks.sql.functions.__dict__.copy()
    spark = (
        SparkSession.builder.master("local[4]")
        .appName("databricks.sql.functions tests")
        .getOrCreate()
    )
    sc = spark.sparkContext
    globs["sc"] = sc
    globs["spark"] = spark
    (failure_count, test_count) = doctest.testmod(
        pyspark.databricks.sql.functions,
        globs=globs,
        optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE,
    )
    spark.stop()
    if failure_count:
        sys.exit(-1)


if __name__ == "__main__":
    _test()
