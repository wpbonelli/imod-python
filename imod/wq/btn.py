import jinja2

from imod.wq.pkgbase import Package


class BasicTransport(Package):
    """
    Handles basic tasks that are required by the entire transport model. Among
    these tasks are definition of the problem, specification of the boundary and
    initial conditions, determination of the stepsize, preparation of mass
    balance information, and printout of the simulation results.

    Parameters
    ----------
    icbund: xr.DataArray
        is an integer array specifying the boundary condition type (inactive,
        constant-concentration, or active) for every model cell. For
        multi-species simulation, ICBUND defines the boundary condition type
        shared by all species. Note that different species are allowed to have
        different constant-concentration conditions through an option in the
        Source and Sink Mixing Package.
        ICBUND=0, the cell is an inactive concentration cell for all species.
        Note that no-flow or “dry” cells are automatically converted into
        inactive concentration cells. Furthermore, active cells in terms of flow
        can be treated as inactive concentration cells to minimize the area
        needed for transport simulation, as long as the solute transport is
        insignificant near those cells.
        ICBUND<0, the cell is a constant-concentration cell for all species. The
        starting concentration of each species remains the same at the cell
        throughout the simulation. (To define different constantconcentration
        conditions for different species at the same cell location, refer to the
        Sink/Source Mixing Package.) Also note that unless explicitly defined as
        a constant-concentration cell, a constant-head cell in the flow model is
        not treated as a constantconcentration cell.
        If ICBUND>0, the cell is an active (variable) concentration cell where
        the concentration value will be calculated.
    starting_concentration: float or array of floats (xr.DataArray)
        is the starting concentration (initial condition) at the beginning of
        the simulation (unit: ML-3) (SCONC). For multispecies simulation, the
        starting concentration must be specified for all species, one species at
        a time.
    porosity: float
        is the “effective” porosity of the porous medium in a single porosity
        system (PRSITY).
        Default value is 0.3.
    n_species:
        Default value is 1.

    inactive_concentration:
        Default value is 1.0e30

    minimum_active_thickness:
        Default value is 0.01.
    """
    _pkg_id = "btn"

    _mapping = (("icbund", "icbund"), ("dz", "thickness"), ("prsity", "porosity"))

    _template = jinja2.Template(
        "[btn]\n"
        "    thkmin = {{minimum_active_thickness}}\n"
        "    cinact = {{inactive_concentration}}\n"
        "    {%- for layer, value in starting_concentration.items() %}\n"
        "    sconc_t1_l{{layer}} = {{value}}\n"
        "    {%- endfor -%}\n"
        "    {%- for name, dictname in mapping -%}\n"
        "        {%- for layer, value in dicts[dictname].items() %}\n"
        "    {{name}}_l{{layer}} = {{value}}\n"
        "        {%- endfor -%}\n"
        "    {%- endfor -%}\n"
    )

    def __init__(
        self,
        icbund,
        starting_concentration,
        porosity=0.35,
        n_species=1,
        inactive_concentration=1.0e30,
        minimum_active_thickness=0.01,
    ):
        super(__class__, self).__init__()
        self["icbund"] = icbund
        self["starting_concentration"] = starting_concentration
        self["porosity"] = porosity
        self["n_species"] = n_species
        self["inactive_concentration"] = inactive_concentration
        self["minimum_active_thickness"] = minimum_active_thickness

    def _render(self, directory, thickness):
        """
        Renders part of [btn] section that does not depend on time,
        and can be inferred without checking the BoundaryConditions.

        Parameters
        ----------
        directory : str
        thickness : xr.DataArray
            Taken from BasicFlow

        Returns
        -------
        rendered : str
        """
        d = {}
        dicts = {}
        d["mapping"] = self._mapping
        # Starting concentration also includes a species, and can't be written
        # in the same way as the other variables; _T? in the runfile
        d["starting_concentration"] = self._compose_values_layer(
            "starting_concentration", directory
        )

        # Collect which entries are complex (multi-dim)
        data_vars = [t[1] for t in self._mapping]
        for varname in self.data_vars.keys():
            if varname == "starting_concentration":
                continue  # skip it, as mentioned above
            if varname in data_vars:  # multi-dim entry
                dicts[varname] = self._compose_values_layer(varname, directory)
            else:  # simple entry, just get the scalar value
                d[varname] = self[varname].values

        # Add these from the outside, thickness from BasicFlow
        # layer_type from LayerPropertyFlow
        dicts["thickness"] = self._compose_values_layer(
            "thickness", directory, da=thickness
        )
        d["dicts"] = dicts
        return self._template.render(d)
