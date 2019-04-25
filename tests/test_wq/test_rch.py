import pathlib

import numpy as np
import pandas as pd
import pytest
import xarray as xr

from imod.wq import RechargeHighestActive, RechargeTopLayer, RechargeLayers


@pytest.fixture(scope="module")
def recharge_top(request):
    datetimes = pd.date_range("2000-01-01", "2000-01-05")
    y = np.arange(4.5, 0.0, -1.0)
    x = np.arange(0.5, 5.0, 1.0)
    rate = xr.DataArray(
        np.full((5, 5, 5), 1.0),
        coords={"time": datetimes, "y": y, "x": x, "dx": 1.0, "dy": -1.0},
        dims=("time", "y", "x"),
    )

    rch = RechargeTopLayer(rate=rate, concentration=rate.copy(), save_budget=False)
    return rch


@pytest.fixture(scope="module")
def recharge_layers(request):
    datetimes = pd.date_range("2000-01-01", "2000-01-05")
    y = np.arange(4.5, 0.0, -1.0)
    x = np.arange(0.5, 5.0, 1.0)
    rate = xr.DataArray(
        np.full((5, 5, 5), 1.0),
        coords={"time": datetimes, "y": y, "x": x, "dx": 1.0, "dy": -1.0},
        dims=("time", "y", "x"),
    )

    rch = RechargeLayers(
        rate=rate,
        recharge_layer=rate.copy(),
        concentration=rate.copy(),
        save_budget=False,
    )
    return rch


@pytest.fixture(scope="module")
def recharge_ha(request):
    datetimes = pd.date_range("2000-01-01", "2000-01-05")
    y = np.arange(4.5, 0.0, -1.0)
    x = np.arange(0.5, 5.0, 1.0)
    rate = xr.DataArray(
        np.full((5, 5, 5), 1.0),
        coords={"time": datetimes, "y": y, "x": x, "dx": 1.0, "dy": -1.0},
        dims=("time", "y", "x"),
    )

    rch = RechargeHighestActive(rate=rate, concentration=rate.copy(), save_budget=False)
    return rch


def test_render__highest_top(recharge_top):
    rch = recharge_top
    directory = pathlib.Path(".")
    compare = (
        "[rch]\n"
        "    nrchop = 1\n"
        "    irchcb = 0\n"
        "    rech_p1 = rate_20000101000000.idf\n"
        "    rech_p2 = rate_20000102000000.idf\n"
        "    rech_p3 = rate_20000103000000.idf\n"
        "    rech_p4 = rate_20000104000000.idf\n"
        "    rech_p5 = rate_20000105000000.idf"
    )

    assert rch._render(directory, globaltimes=rch.time.values) == compare


def test_render__layers(recharge_layers):
    rch = recharge_layers
    directory = pathlib.Path(".")
    compare = (
        "[rch]\n"
        "    nrchop = 2\n"
        "    irchcb = 0\n"
        "    rech_p1 = rate_20000101000000.idf\n"
        "    rech_p2 = rate_20000102000000.idf\n"
        "    rech_p3 = rate_20000103000000.idf\n"
        "    rech_p4 = rate_20000104000000.idf\n"
        "    rech_p5 = rate_20000105000000.idf\n"
        "    irch_p1 = recharge_layer_20000101000000.idf\n"
        "    irch_p2 = recharge_layer_20000102000000.idf\n"
        "    irch_p3 = recharge_layer_20000103000000.idf\n"
        "    irch_p4 = recharge_layer_20000104000000.idf\n"
        "    irch_p5 = recharge_layer_20000105000000.idf"
    )

    assert rch._render(directory, globaltimes=rch.time.values) == compare


def test_render__highest_active(recharge_ha):
    rch = recharge_ha
    directory = pathlib.Path(".")
    compare = (
        "[rch]\n"
        "    nrchop = 3\n"
        "    irchcb = 0\n"
        "    rech_p1 = rate_20000101000000.idf\n"
        "    rech_p2 = rate_20000102000000.idf\n"
        "    rech_p3 = rate_20000103000000.idf\n"
        "    rech_p4 = rate_20000104000000.idf\n"
        "    rech_p5 = rate_20000105000000.idf"
    )

    assert rch._render(directory, globaltimes=rch.time.values) == compare

