import pathlib

import numpy as np
import pandas as pd
import xugrid as xu

from imod.mf6.pkgbase import Package


class VerticesDiscretization(Package):
    """

    Parameters
    ----------
    top: array of floats (xu.UgridDataArray)
    bottom: array of floats (xu.UgridDataArray)
    idomain: array of integers (xu.UgridDataArray)
    """

    _pkg_id = "disv"
    _grid_data = {"top": np.float64, "bottom": np.float64, "idomain": np.int32}
    _keyword_map = {"bottom": "botm"}
    _template = Package._initialize_template(_pkg_id)

    def __init__(self, top, bottom, idomain):
        super(__class__, self).__init__(locals())
        self.dataset["idomain"] = idomain
        self.dataset["top"] = top
        self.dataset["bottom"] = bottom

    def render(self, directory, pkgname, *args, **kwargs):
        disdirectory = directory / pkgname
        d = {}
        grid = self.dataset.ugrid.grid
        d["xorigin"] = grid.node_x.min()
        d["yorigin"] = grid.node_y.min()
        d["nlay"] = self.dataset["idomain"].coords["layer"].size
        facedim = grid.face_dimension
        d["ncpl"] = self.dataset["idomain"].coords[facedim].size
        d["nvert"] = grid.node_x.size

        _, d["top"] = self._compose_values(self.dataset["top"], disdirectory, "top")
        d["botm_layered"], d["botm"] = self._compose_values(
            self["bottom"], disdirectory, "botm"
        )
        d["idomain_layered"], d["idomain"] = self._compose_values(
            self["idomain"], disdirectory, "idomain"
        )
        return self._template.render(d)

    def _verts_dataframe(self) -> pd.DataFrame:
        grid = self.dataset.ugrid.grid
        df = pd.DataFrame(grid.node_coordinates)
        df.index += 1
        return df

    def _cell2d_dataframe(self) -> pd.DataFrame:
        grid = self.dataset.ugrid.grid
        df = pd.DataFrame(grid.face_coordinates)
        df.index += 1
        # modflow requires clockwise; ugrid requires ccw
        face_nodes = grid.face_node_connectivity[:, ::-1] + 1
        df[2] = (face_nodes != grid.fill_value).sum(axis=1)
        for i, column in enumerate(face_nodes.T):
            # Use extension array to write empty values
            # Should be more effcient than mixed column?
            df[3 + i] = pd.arrays.IntegerArray(
                values=column,
                mask=(column == grid.fill_value),
            )
        return df

    def write_blockfile(self, directory, pkgname, *args):
        dir_for_render = pathlib.Path(directory.stem)
        content = self.render(dir_for_render, pkgname, *args)
        filename = directory / f"{pkgname}.{self._pkg_id}"
        with open(filename, "w") as f:
            f.write(content)
            f.write("\n\n")

            f.write("begin vertices\n")
            self._verts_dataframe().to_csv(
                f, header=False, sep=" ", line_terminator="\n"
            )
            f.write("end vertices\n\n")

            f.write("begin cell2d\n")
            self._cell2d_dataframe().to_csv(
                f, header=False, sep=" ", line_terminator="\n"
            )
            f.write("end cell2d\n")
        return
