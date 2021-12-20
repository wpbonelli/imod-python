import datetime
import pathlib
import re

import affine
import cftime
import numpy as np
import pytest
import xarray as xr

from imod import util


def test_compose():
    d = {
        "name": "head",
        "directory": pathlib.Path("path", "to"),
        "extension": ".idf",
        "layer": 5,
        "time": datetime.datetime(2018, 2, 22, 9, 6, 57),
        "species": 6,
    }
    path = util.compose(d)
    targetpath = pathlib.Path(d["directory"], "head_c6_20180222090657_l5.idf")
    assert path == targetpath

    d.pop("species")
    path = util.compose(d)
    targetpath = pathlib.Path(d["directory"], "head_20180222090657_l5.idf")
    assert path == targetpath

    d.pop("layer")
    path = util.compose(d)
    targetpath = pathlib.Path(d["directory"], "head_20180222090657.idf")
    assert path == targetpath

    d.pop("time")
    d["layer"] = 1
    path = util.compose(d)
    targetpath = pathlib.Path(d["directory"], "head_l1.idf")
    assert path == targetpath

    d["species"] = 6
    path = util.compose(d)
    targetpath = pathlib.Path(d["directory"], "head_c6_l1.idf")
    assert path == targetpath


def test_compose__pattern():
    d = {
        "name": "head",
        "directory": pathlib.Path("path", "to"),
        "extension": ".foo",
        "layer": 5,
    }
    targetpath = pathlib.Path(d["directory"], "head_2018-02-22_l05.foo")

    d["time"] = datetime.datetime(2018, 2, 22, 9, 6, 57)
    path = util.compose(d, pattern="{name}_{time:%Y-%m-%d}_l{layer:02d}{extension}")
    assert path == targetpath

    d["time"] = cftime.DatetimeProlepticGregorian(2018, 2, 22, 9, 6, 57)
    path = util.compose(d, pattern="{name}_{time:%Y-%m-%d}_l{layer:02d}{extension}")
    assert path == targetpath

    d["time"] = np.datetime64("2018-02-22 09:06:57")
    path = util.compose(d, pattern="{name}_{time:%Y-%m-%d}_l{layer:02d}{extension}")
    assert path == targetpath

    targetpath = pathlib.Path(d["directory"], ".foo_makes_head_no_layer5_sense_day22")
    path = util.compose(
        d, pattern="{extension}_makes_{name}_no_layer{layer:d}_sense_day{time:%d}"
    )
    assert path == targetpath


def test_decompose():
    d = util.decompose("path/to/head_20180222090657_l5.idf")
    refd = {
        "extension": ".idf",
        "directory": pathlib.Path("path", "to"),
        "name": "head",
        "time": datetime.datetime(2018, 2, 22, 9, 6, 57),
        "layer": 5,
        "dims": ["time", "layer"],
    }
    assert isinstance(d, dict)
    assert d == refd


def test_decompose_species():
    d = util.decompose("path/to/conc_c3_20180222090657_l5.idf")
    refd = {
        "extension": ".idf",
        "species": 3,
        "directory": pathlib.Path("path", "to"),
        "name": "conc",
        "time": datetime.datetime(2018, 2, 22, 9, 6, 57),
        "layer": 5,
        "dims": ["species", "time", "layer"],
    }
    assert isinstance(d, dict)
    assert d == refd


def test_decompose_short_date():
    d = util.decompose("path/to/head_20180222_l5.idf")
    refd = {
        "extension": ".idf",
        "directory": pathlib.Path("path", "to"),
        "name": "head",
        "time": datetime.datetime(2018, 2, 22),
        "layer": 5,
        "dims": ["time", "layer"],
    }
    assert isinstance(d, dict)
    assert d == refd


def test_decompose_nonstandard_date():
    d = util.decompose("path/to/head_2018-02-22_l5.idf")
    refd = {
        "extension": ".idf",
        "directory": pathlib.Path("path", "to"),
        "name": "head",
        "time": datetime.datetime(2018, 2, 22),
        "layer": 5,
        "dims": ["time", "layer"],
    }
    assert isinstance(d, dict)
    assert d == refd


def test_decompose_only_year():
    d = util.decompose("path/to/head_2018_l5.idf", pattern="{name}_{time}_l{layer}")
    refd = {
        "extension": ".idf",
        "directory": pathlib.Path("path", "to"),
        "name": "head",
        "time": datetime.datetime(2018, 1, 1),
        "layer": 5,
        "dims": ["time", "layer"],
    }
    assert isinstance(d, dict)
    assert d == refd


def test_decompose_underscore():
    d = util.decompose("path/to/starting_head_20180222090657_l5.idf")
    refd = {
        "extension": ".idf",
        "directory": pathlib.Path("path", "to"),
        "name": "starting_head",
        "time": datetime.datetime(2018, 2, 22, 9, 6, 57),
        "layer": 5,
        "dims": ["time", "layer"],
    }
    assert isinstance(d, dict)
    assert d == refd


def test_decompose_dash():
    d = util.decompose("path/to/starting-head_20180222090657_l5.idf")
    refd = {
        "extension": ".idf",
        "directory": pathlib.Path("path", "to"),
        "name": "starting-head",
        "time": datetime.datetime(2018, 2, 22, 9, 6, 57),
        "layer": 5,
        "dims": ["time", "layer"],
    }
    assert isinstance(d, dict)
    assert d == refd


def test_decompose_steady_state():
    d = util.decompose("path/to/head_steady-state_l64.idf")
    refd = {
        "extension": ".idf",
        "directory": pathlib.Path("path", "to"),
        "name": "head",
        "time": "steady-state",
        "layer": 64,
        "dims": ["layer", "time"],
    }
    assert isinstance(d, dict)
    assert d == refd


def test_decompose_underscore_in_name():
    d = util.decompose("path/to/some_name.idf")
    refd = {
        "extension": ".idf",
        "directory": pathlib.Path("path", "to"),
        "name": "some_name",
        "dims": [],
    }
    assert isinstance(d, dict)
    assert d == refd


def test_decompose_pattern_underscore():
    d = util.decompose(
        "path/to/starting_head_20180222090657_l5.idf", pattern="{name}_{time}_l{layer}"
    )
    refd = {
        "extension": ".idf",
        "directory": pathlib.Path("path", "to"),
        "name": "starting_head",
        "time": datetime.datetime(2018, 2, 22, 9, 6, 57),
        "layer": 5,
        "dims": ["time", "layer"],
    }
    assert isinstance(d, dict)
    assert d == refd


def test_decompose_pattern_dash():
    d = util.decompose(
        "path/to/starting-head_20180222090657_l5.idf", pattern="{name}_{time}_l{layer}"
    )
    refd = {
        "extension": ".idf",
        "directory": pathlib.Path("path", "to"),
        "name": "starting-head",
        "time": datetime.datetime(2018, 2, 22, 9, 6, 57),
        "layer": 5,
        "dims": ["time", "layer"],
    }
    assert isinstance(d, dict)
    assert d == refd


def test_decompose_regexpattern():
    pattern = re.compile(r"(?P<name>[\w]+)L(?P<layer>[\d+]*)", re.IGNORECASE)
    d = util.decompose("headL11.idf", pattern=pattern)
    refd = {
        "extension": ".idf",
        "directory": pathlib.Path("."),
        "name": "head",
        "layer": 11,
        "dims": ["layer"],
    }
    assert isinstance(d, dict)
    assert d == refd


def test_decompose_nodate():
    d = util.decompose("dem_10m.idf")
    refd = {
        "extension": ".idf",
        "directory": pathlib.Path("."),
        "name": "dem_10m",
        "dims": [],
    }
    assert isinstance(d, dict)
    assert d == refd


def test_decompose_dateonly():
    d = util.decompose("20180222090657.idf", pattern="{time}")
    refd = {
        "extension": ".idf",
        "directory": pathlib.Path("."),
        "name": "20180222090657",
        "time": datetime.datetime(2018, 2, 22, 9, 6, 57),
        "dims": ["time"],
    }
    assert isinstance(d, dict)
    assert d == refd


def test_decompose_datelayeronly():
    d = util.decompose("20180222090657_l7.idf", pattern="{time}_l{layer}")
    refd = {
        "extension": ".idf",
        "directory": pathlib.Path("."),
        "name": "20180222090657_7",
        "time": datetime.datetime(2018, 2, 22, 9, 6, 57),
        "layer": 7,
        "dims": ["time", "layer"],
    }
    assert isinstance(d, dict)
    assert d == refd


def test_decompose_z_float():
    d = util.decompose("test_0.25.idf", pattern="{name}_{z}")
    refd = {
        "extension": ".idf",
        "directory": pathlib.Path("."),
        "name": "test",
        "z": "0.25",
        "dims": ["z"],
    }
    assert isinstance(d, dict)
    assert d == refd


def test_compose_year9999():
    d = {
        "name": "head",
        "directory": pathlib.Path("path", "to"),
        "extension": ".idf",
        "layer": 5,
        "time": datetime.datetime(9999, 2, 22, 9, 6, 57),
        "dims": ["time"],
    }
    path = util.compose(d)
    targetpath = pathlib.Path(d["directory"], "head_99990222090657_l5.idf")
    assert path == targetpath


def test_decompose_dateonly_year9999():
    d = util.decompose("99990222090657.idf", pattern="{time}")
    refd = {
        "extension": ".idf",
        "directory": pathlib.Path("."),
        "name": "99990222090657",
        "time": datetime.datetime(9999, 2, 22, 9, 6, 57),
        "dims": ["time"],
    }
    assert isinstance(d, dict)
    assert d == refd


def test_datetime_conversion__withinbounds():
    times = [datetime.datetime(y, 1, 1) for y in range(2000, 2010)]
    converted, use_cftime = util._convert_datetimes(times, use_cftime=False)
    assert use_cftime is False
    assert all(t.dtype == "<M8[ns]" for t in converted)
    assert converted[0] == np.datetime64("2000-01-01", "ns")
    assert converted[-1] == np.datetime64("2009-01-01", "ns")


def test_datetime_conversion__outofbounds():
    times = [datetime.datetime(y, 1, 1) for y in range(1670, 1680)]
    with pytest.warns(UserWarning):
        converted, use_cftime = util._convert_datetimes(times, use_cftime=False)
    assert use_cftime is True
    assert all(type(t) == cftime.DatetimeProlepticGregorian for t in converted)
    assert converted[0] == cftime.DatetimeProlepticGregorian(1670, 1, 1)
    assert converted[-1] == cftime.DatetimeProlepticGregorian(1679, 1, 1)


def test_datetime_conversion__withinbounds_cftime():
    times = [datetime.datetime(y, 1, 1) for y in range(2000, 2010)]
    converted, use_cftime = util._convert_datetimes(times, use_cftime=True)
    assert use_cftime is True
    assert all(type(t) == cftime.DatetimeProlepticGregorian for t in converted)
    assert converted[0] == cftime.DatetimeProlepticGregorian(2000, 1, 1)
    assert converted[-1] == cftime.DatetimeProlepticGregorian(2009, 1, 1)


def test_transform():
    # implicit dx dy
    data = np.ones((2, 3))
    coords = {"x": [0.5, 1.5, 2.5], "y": [1.5, 0.5]}
    dims = ("y", "x")
    da = xr.DataArray(data, coords, dims)
    actual = util.transform(da)
    expected = affine.Affine(1.0, 0.0, 0.0, 0.0, -1.0, 2.0)
    assert actual == expected

    # explicit dx dy, equidistant
    coords = {
        "x": [0.5, 1.5, 2.5],
        "y": [1.5, 0.5],
        "dx": ("x", [1.0, 1.0, 1.0]),
        "dy": ("y", [-1.0, -1.0]),
    }
    dims = ("y", "x")
    da = xr.DataArray(data, coords, dims)
    actual = util.transform(da)
    assert actual == expected

    # explicit dx dy, non-equidistant
    coords = {
        "x": [0.5, 1.5, 3.5],
        "y": [1.5, 0.5],
        "dx": ("x", [1.0, 1.0, 2.0]),
        "dy": ("y", [-1.0, -1.0]),
    }
    dims = ("y", "x")
    da = xr.DataArray(data, coords, dims)
    with pytest.raises(ValueError):
        util.transform(da)


def test_is_divisor():
    a = np.array([1.0, 0.5, 0.1])
    b = 0.05
    assert util.is_divisor(a, b)
    assert util.is_divisor(-a, b)
    assert util.is_divisor(a, -b)
    assert util.is_divisor(-a, -b)
    b = 0.07
    assert not util.is_divisor(a, b)
    assert not util.is_divisor(-a, b)
    assert not util.is_divisor(a, -b)
    assert not util.is_divisor(-a, -b)


def test_empty():
    da = util.empty_2d(1.0, 0.0, 2.0, -1.0, 10.0, 12.0)
    assert da.isnull().all()
    assert np.allclose(da["x"], [0.5, 1.5])
    assert np.allclose(da["y"], [11.5, 10.5])
    assert da.dims == ("y", "x")

    with pytest.raises(ValueError, match="layer must be 1d"):
        util.empty_3d(1.0, 0.0, 2.0, -1.0, 10.0, 12.0, [[1, 2]])

    da3d = util.empty_3d(1.0, 0.0, 2.0, -1.0, 10.0, 12.0, 1)
    assert da3d.ndim == 3
    da3d = util.empty_3d(1.0, 0.0, 2.0, -1.0, 10.0, 12.0, [1, 3])
    assert np.array_equal(da3d["layer"], [1, 3])
    assert da3d.dims == ("layer", "y", "x")

    times = ["2000-01-01", "2001-01-01"]
    with pytest.raises(ValueError, match="time must be 1d"):
        util.empty_2d_transient(1.0, 0.0, 2.0, -1.0, 10.0, 12.0, [times])

    da2dt = util.empty_2d_transient(1.0, 0.0, 2.0, -1.0, 10.0, 12.0, times[0])
    assert da2dt.ndim == 3
    da2dt = util.empty_2d_transient(1.0, 0.0, 2.0, -1.0, 10.0, 12.0, times)
    assert isinstance(da2dt["time"].values[0], np.datetime64)
    assert da2dt.dims == ("time", "y", "x")

    da3dt = util.empty_3d_transient(1.0, 0.0, 2.0, -1.0, 10.0, 12.0, [0, 1], times)
    assert da3dt.ndim == 4
    assert da3dt.dims == ("time", "layer", "y", "x")


def test_where():
    a = xr.DataArray(
        [[0.0, 1.0], [2.0, np.nan]],
        {"y": [1.5, 0.5], "x": [0.5, 1.5]},
        ["y", "x"],
    )
    cond = a <= 1
    actual = util.where(cond, if_true=a, if_false=1.0)
    assert np.allclose(actual.values, [[0.0, 1.0], [1.0, np.nan]], equal_nan=True)

    actual = util.where(cond, if_true=0.0, if_false=1.0)
    assert np.allclose(actual.values, [[0.0, 0.0], [1.0, 1.0]], equal_nan=True)

    actual = util.where(cond, if_true=a, if_false=1.0, keep_nan=False)
    assert np.allclose(actual.values, [[0.0, 1.0], [1.0, 1.0]])

    with pytest.raises(ValueError, match="at least one of"):
        util.where(False, 1, 0)


def test_to_ugrid2d():
    a = xr.DataArray(
        np.ones((3, 2, 2)),
        {"layer": [1, 2, 3], "y": [1.5, 0.5], "x": [0.5, 1.5]},
        ["layer", "y", "x"],
        name=None,
    )
    with pytest.raises(TypeError, match="data must be xarray"):
        util.to_ugrid2d(a.values)
    with pytest.raises(ValueError, match="A name is required"):
        util.to_ugrid2d(a)

    a.name = "a"
    with pytest.raises(ValueError, match="Last two dimensions of da"):
        util.to_ugrid2d(a.transpose())

    uds = util.to_ugrid2d(a)
    assert isinstance(uds, xr.Dataset)
    for i in range(1, 4):
        assert f"a_layer_{i}" in uds

    ds = xr.Dataset()
    ds["a"] = a
    ds["b"] = a.copy()
    uds = util.to_ugrid2d(ds)
    assert isinstance(uds, xr.Dataset)
    for i in range(1, 4):
        assert f"a_layer_{i}" in uds
        assert f"b_layer_{i}" in uds
