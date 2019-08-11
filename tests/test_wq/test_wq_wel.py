import pathlib
import shutil

import numpy as np
import pandas as pd
import pytest

from imod.wq import Well


@pytest.fixture(scope="module")
def well(request):
    datetimes = pd.date_range("2000-01-01", "2000-01-05")
    y = np.arange(4.5, 0.0, -1.0)
    x = np.arange(0.5, 5.0, 1.0)
    wel = Well(id_name="well", x=x, y=y, rate=5.0, layer=2, time=datetimes)

    def teardown():
        shutil.rmtree("well", ignore_errors=True)

    request.addfinalizer(teardown)
    return wel


def test_render(well):
    wel = well
    directory = pathlib.Path("well")
    path = pathlib.Path("well").joinpath("well")
    compare = (
        "\n"
        "    wel_p1_s1_l2 = {path}_20000101000000_l2.ipf\n"
        "    wel_p2_s1_l2 = {path}_20000102000000_l2.ipf\n"
        "    wel_p3_s1_l2 = {path}_20000103000000_l2.ipf\n"
        "    wel_p4_s1_l2 = {path}_20000104000000_l2.ipf\n"
        "    wel_p5_s1_l2 = {path}_20000105000000_l2.ipf"
    ).format(path=path)
    actual = wel._render(directory, globaltimes=wel["time"].values, system_index=1)
    assert actual == compare


def test_render__notime_nolayer(well):
    # Necessary because using drop return a pandas.DataFrame instead of a Well
    # object
    d = {k: v for k, v in well.copy().drop("layer").drop("time").items()}
    path = pathlib.Path("well").joinpath("well")
    wel = Well(**d)
    directory = pathlib.Path("well")
    compare = "\n" "    wel_p?_s1_l? = {path}.ipf".format(path=path)
    actual = wel._render(directory, globaltimes=["?"], system_index=1)
    assert actual == compare


def test_render__notime_layer(well):
    d = {k: v for k, v in well.copy().drop("time").items()}
    d["layer"] = [1, 2, 3, 4, 5]
    wel = Well(**d)
    directory = pathlib.Path("well")
    path = pathlib.Path("well").joinpath("well")
    compare = (
        "\n"
        "    wel_p?_s1_l1 = {path}_l1.ipf\n"
        "    wel_p?_s1_l2 = {path}_l2.ipf\n"
        "    wel_p?_s1_l3 = {path}_l3.ipf\n"
        "    wel_p?_s1_l4 = {path}_l4.ipf\n"
        "    wel_p?_s1_l5 = {path}_l5.ipf"
    ).format(path=path)

    actual = wel._render(directory, globaltimes=["?"], system_index=1)
    assert actual == compare


def test_render__time_nolayer(well):
    d = {k: v for k, v in well.copy().drop("layer").items()}
    wel = Well(**d)
    directory = pathlib.Path("well")
    path = pathlib.Path("well").joinpath("well")
    compare = (
        "\n"
        "    wel_p1_s1_l? = {path}_20000101000000.ipf\n"
        "    wel_p2_s1_l? = {path}_20000102000000.ipf\n"
        "    wel_p3_s1_l? = {path}_20000103000000.ipf\n"
        "    wel_p4_s1_l? = {path}_20000104000000.ipf\n"
        "    wel_p5_s1_l? = {path}_20000105000000.ipf"
    ).format(path=path)

    assert (
        wel._render(directory, globaltimes=wel["time"].values, system_index=1)
        == compare
    )


def test_render__time_layer(well):
    d = {k: v for k, v in well.items()}
    d["layer"] = [1, 2, 3, 4, 5]
    wel = Well(**d)
    directory = pathlib.Path("well")
    path = pathlib.Path("well").joinpath("well")
    compare = (
        "\n"
        "    wel_p1_s1_l1 = {path}_20000101000000_l1.ipf\n"
        "    wel_p2_s1_l2 = {path}_20000102000000_l2.ipf\n"
        "    wel_p3_s1_l3 = {path}_20000103000000_l3.ipf\n"
        "    wel_p4_s1_l4 = {path}_20000104000000_l4.ipf\n"
        "    wel_p5_s1_l5 = {path}_20000105000000_l5.ipf"
    ).format(path=path)

    actual = wel._render(directory, globaltimes=wel["time"].values, system_index=1)
    assert actual == compare


def test_save(well):
    wel = well
    directory = pathlib.Path("well")
    wel.save(directory)

    files = [
        "well_20000101000000_l2.ipf",
        "well_20000102000000_l2.ipf",
        "well_20000103000000_l2.ipf",
        "well_20000104000000_l2.ipf",
        "well_20000105000000_l2.ipf",
    ]
    for file in files:
        assert pathlib.Path("well").joinpath(file).exists()


def test_save__time_nolayer(well):
    d = {k: v for k, v in well.copy().drop("layer").items()}
    wel = Well(**d)
    directory = pathlib.Path("well")
    path = pathlib.Path("well").joinpath("well")
    wel.save(directory)

    files = [
        "well_20000101000000.ipf",
        "well_20000102000000.ipf",
        "well_20000103000000.ipf",
        "well_20000104000000.ipf",
        "well_20000105000000.ipf",
    ]
    for file in files:
        assert pathlib.Path("well").joinpath(file).exists()
