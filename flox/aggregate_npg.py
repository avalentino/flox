from functools import partial

import numpy as np
import numpy_groupies as npg


def _get_aggregate(engine):
    return npg.aggregate_numpy if engine == "numpy" else npg.aggregate_numba


def sum_of_squares(
    group_idx,
    array,
    engine,
    *,
    axis=-1,
    size=None,
    fill_value=None,
    dtype=None,
):
    return _get_aggregate(engine).aggregate(
        group_idx,
        array,
        axis=axis,
        func="sumofsquares",
        size=size,
        fill_value=fill_value,
        dtype=dtype,
    )


def nansum_of_squares(
    group_idx,
    array,
    engine,
    *,
    axis=-1,
    size=None,
    fill_value=None,
    dtype=None,
):
    return _get_aggregate(engine).aggregate(
        group_idx,
        array,
        axis=axis,
        func="nansumofsquares",
        size=size,
        fill_value=fill_value,
        dtype=dtype,
    )


def nansum(group_idx, array, engine, *, axis=-1, size=None, fill_value=None, dtype=None):
    # npg takes out NaNs before calling np.bincount
    # This means that all NaN groups are equivalent to absent groups
    # This behaviour does not work for xarray

    return _get_aggregate(engine).aggregate(
        group_idx,
        np.where(np.isnan(array), 0, array),
        axis=axis,
        func="sum",
        size=size,
        fill_value=fill_value,
        dtype=dtype,
    )


def nanprod(group_idx, array, engine, *, axis=-1, size=None, fill_value=None, dtype=None):
    # npg takes out NaNs before calling np.bincount
    # This means that all NaN groups are equivalent to absent groups
    # This behaviour does not work for xarray

    return _get_aggregate(engine).aggregate(
        group_idx,
        np.where(np.isnan(array), 1, array),
        axis=axis,
        func="prod",
        size=size,
        fill_value=fill_value,
        dtype=dtype,
    )


def _len(group_idx, array, engine, *, func, axis=-1, size=None, fill_value=None, dtype=None):
    result = _get_aggregate(engine).aggregate(
        group_idx,
        array,
        axis=axis,
        func=func,
        size=size,
        fill_value=0,
        dtype=np.int64,
    )
    if fill_value is not None:
        result = result.astype(np.array([fill_value]).dtype)
        result[result == 0] = fill_value
    return result


len = partial(_len, func="len")
nanlen = partial(_len, func="nanlen")


def median(group_idx, array, engine, *, axis=-1, size=None, fill_value=None, dtype=None):
    return npg.aggregate_numpy.aggregate(
        group_idx,
        array,
        func=np.median,
        axis=axis,
        size=size,
        fill_value=fill_value,
        dtype=dtype,
    )


def nanmedian(group_idx, array, engine, *, axis=-1, size=None, fill_value=None, dtype=None):
    return npg.aggregate_numpy.aggregate(
        group_idx,
        array,
        func=np.nanmedian,
        axis=axis,
        size=size,
        fill_value=fill_value,
        dtype=dtype,
    )


def quantile(group_idx, array, engine, *, q, axis=-1, size=None, fill_value=None, dtype=None):
    return npg.aggregate_numpy.aggregate(
        group_idx,
        array,
        func=partial(np.quantile, q=q),
        axis=axis,
        size=size,
        fill_value=fill_value,
        dtype=dtype,
    )


def nanquantile(group_idx, array, engine, *, q, axis=-1, size=None, fill_value=None, dtype=None):
    return npg.aggregate_numpy.aggregate(
        group_idx,
        array,
        func=partial(np.nanquantile, q=q),
        axis=axis,
        size=size,
        fill_value=fill_value,
        dtype=dtype,
    )


def mode_(array, nan_policy, dtype):
    from scipy.stats import mode

    # npg splits `array` into object arrays for each group
    # scipy.stats.mode does not like that
    # here we cast back
    return mode(array.astype(dtype, copy=False), nan_policy=nan_policy, axis=-1).mode


def mode(group_idx, array, engine, *, axis=-1, size=None, fill_value=None, dtype=None):
    return npg.aggregate_numpy.aggregate(
        group_idx,
        array,
        func=partial(mode_, nan_policy="propagate", dtype=array.dtype),
        axis=axis,
        size=size,
        fill_value=fill_value,
        dtype=dtype,
    )


def nanmode(group_idx, array, engine, *, axis=-1, size=None, fill_value=None, dtype=None):
    return npg.aggregate_numpy.aggregate(
        group_idx,
        array,
        func=partial(mode_, nan_policy="omit", dtype=array.dtype),
        axis=axis,
        size=size,
        fill_value=fill_value,
        dtype=dtype,
    )
