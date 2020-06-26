from imod.mf6.pkgbase import BoundaryCondition
import numpy as np
import xarray as xr

class UnsaturatedZoneFlow(BoundaryCondition):
    """
    Unsaturated Zone Flow (UZF) package.
    
    TODO: Support timeseries file? Observations? Water Mover?
    
    Parameters
    ----------
    surface_depression_depth: array of floats (xr.DataArray)
        is the surface depression depth of the UZF cell.
    kv_sat: array of floats (xr.DataArray)
        is the vertical saturated hydraulic conductivity of the UZF cell.
        TODO: If nothing provided, select from vertical hydraulic conducivity npf
        TODO: Let user provide mapping with dim uzf_number, or an array with layer, y, x
    theta_r: array of floats (xr.DataArray)
        is the residual (irreducible) water content of the UZF cell.
    theta_sat: array of floats (xr.DataArray)
        is the saturated water content of the UZF cell.
    theta_init: array of floats (xr.DataArray)
        is the initial water content of the UZF cell.
    epsilon: array of floats (xr.DataArray)
        is the epsilon exponent of the UZF cell.
    infiltration_rate: array of floats (xr.DataArray)
        defines the applied infiltration rate of the UZF cell (LT -1).
    ET_pot: array of floats (xr.DataArray, optional)
        defines the potential evapotranspiration rate of the UZF cell and specified
        GWF cell. Evapotranspiration is first removed from the unsaturated zone and any remaining
        potential evapotranspiration is applied to the saturated zone. If IVERTCON is greater than zero
        then residual potential evapotranspiration not satisfied in the UZF cell is applied to the underlying
        UZF and GWF cells. PET is always specified, but is only used if SIMULATE ET is specified in the
        OPTIONS block.
    extinction_depth: array of floats (xr.DataArray, optional)
        defines the evapotranspiration extinction depth of the UZF cell. If
        IVERTCON is greater than zero and EXTDP extends below the GWF cell bottom then remaining
        potential evapotranspiration is applied to the underlying UZF and GWF cells. EXTDP is always
        specified, but is only used if SIMULATE ET is specified in the OPTIONS block.
    extinction_theta: array of floats (xr.DataArray, optional)
        defines the evapotranspiration extinction water content of the UZF
        cell. If specified, ET in the unsaturated zone will be simulated either as a function of the
        specified PET rate while the water content (THETA) is greater than the ET extinction water content
    air_entry_potential: array of floats (xr.DataArray, optional)
        defines the air entry potential (head) of the UZF cell. If specified, ET will be 
        simulated using a capillary pressure based formulation. 
        Capillary pressure is calculated using the Brooks-Corey retention function ("air_entry")
    root_potential: array of floats (xr.DataArray, optional)
        defines the root potential (head) of the UZF cell. If specified, ET will be 
        simulated using a capillary pressure based formulation. 
        Capillary pressure is calculated using the Brooks-Corey retention function ("air_entry"
    root_activity: array of floats (xr.DataArray, optional)
        defines the root activity function of the UZF cell. ROOTACT is
        the length of roots in a given volume of soil divided by that volume. Values range from 0 to about 3
        cm-2, depending on the plant community and its stage of development. If specified, ET will be 
        simulated using a capillary pressure based formulation. 
        Capillary pressure is calculated using the Brooks-Corey retention function ("air_entry"
    groundwater_ET_function: ({"linear", "square"}, optional)
        keyword specifying that groundwater evapotranspiration will be simulated using either
        the original ET formulation of MODFLOW-2005 ("linear"). Or by assuming a constant ET
        rate for groundwater levels between land surface (TOP) and land surface minus the ET extinction
        depth (TOP-EXTDP) ("square"). In the latter case, groundwater ET is smoothly reduced 
        from the PET rate to zero over a nominal interval at TOP-EXTDP.
    simulate_seepage: ({True, False}, optional)
        keyword specifying that groundwater discharge (GWSEEP) to land surface will be
        simulated. Groundwater discharge is nonzero when groundwater head is greater than land surface.
    print_input: ({True, False}, optional)
        keyword to indicate that the list of UZF information will be written to the listing file
        immediately after it is read.
        Default is False.
    print_flows: ({True, False}, optional)
        keyword to indicate that the list of UZF flow rates will be printed to the listing file for
        every stress period time step in which “BUDGET PRINT” is specified in Output Control. If there is
        no Output Control option and “PRINT FLOWS” is specified, then flow rates are printed for the last
        time step of each stress period.
        Default is False.
    save_flows: ({True, False}, optional)
        keyword to indicate that UZF flow terms will be written to the file specified with “BUDGET
        FILEOUT” in Output Control.
        Default is False.
    observations: [Not yet supported.]
        Default is None.
    water_mover: [Not yet supported.]
        Default is None.
    timeseries: [Not yet supported.]
        Default is None. 
        TODO: We could allow the user to either use xarray DataArrays to specify BCS or 
        use a pd.DataFrame and use the MF6 timeseries files to read input. The latter could
        save memory for laterally large-scale models, through efficient use of the UZF cell identifiers.
    """

    __slots__ = (
        "surface_depression_depth",
        "kv_sat",
        "theta_r",
        "theta_sat",
        "theta_init",
        "epsilon" "infiltration_rate",
        "et_pot",
        "extinction_depth",
        "extinction_theta",
        "air_entry_potential",
        "root_potential",
        "root_activity",
        "ntrailwaves",
        "nwavesets",
        "simulate_ET",
        "groundwater_ET_function",
        "simulate_seepage",
        "unsaturated_ET_function",
        "print_input",
        "print_flows",
        "save_flows",
        "observations",
        "water_mover",
        "timeseries",
        "landflag",
        "ivertcon",
        "iuzno",
    )

    _binary_data = (
        "infiltration_rate",
        "et_pot",
        "extinction_depth",
        "extinction_theta",
        "air_entry_potential",
        "root_potential",
        "root_activity",
    )

    _package_data = (
        "surface_depression_depth",
        "kv_sat",
        "theta_r",
        "theta_sat",
        "theta_init",
        "epsilon",
    )
    _pkg_id = "uzf"

    _template = BoundaryCondition._initialize_template(_pkg_id)

    def __init__(
        self,
        surface_depression_depth,
        kv_sat,
        theta_r,
        theta_sat,
        theta_init,
        epsilon,
        infiltration_rate,
        et_pot=None,
        extinction_depth=None,
        extinction_theta=None,
        air_entry_potential=None,
        root_potential=None,
        root_activity=None,
        ntrailwaves=7,  # Recommended in manual
        nwavesets=40,
        groundwater_ET_function="linear",
        simulate_groundwater_seepage=False,
        print_input=False,
        print_flows=False,
        save_flows=False,
        observations=None,
        water_mover=None,
        timeseries=None,
    ):
        super(__class__, self).__init__()
        #Package data
        self["surface_depression_depth"] = surface_depression_depth
        self["kv_sat"] = kv_sat
        self["theta_r"] = theta_r
        self["theta_sat"] = theta_sat
        self["theta_init"] = theta_init
        self["epsilon"] = epsilon
        
        #Stress period data
        self._check_options(groundwater_ET_function, 
                           et_pot, extinction_depth, 
                           extinction_theta, air_entry_potential,
                           root_potential, root_activity)
        
        self["infiltration_rate"] = infiltration_rate
        self["et_pot"] = et_pot
        self["extinction_depth"] = extinction_depth
        self["extinction_theta"] = extinction_theta
        self["air_entry_potential"] = air_entry_potential
        self["root_potential"] = root_potential
        self["root_activity"] = root_activity
        
        #Dimensions
        self["ntrailwaves"] = ntrailwaves
        self["nwavesets"] = nwavesets
        
        #Options
        self["groundwater_ET_function"] = groundwater_ET_function
        self["simulate_gwseep"] = simulate_groundwater_seepage
        self["print_input"] = print_input
        self["print_flows"] = print_flows
        self["save_flows"] = save_flows
        self["observations"] = observations
        self["water_mover"] = water_mover
        self["timeseries"] = timeseries

        #Additonal indices for Packagedata
        self["landflag"] = self._determine_landflag(kv_sat)

        self["iuzno"] = self._create_uzf_numbers(self["landflag"])
        self["iuzno"].name = "uzf_number"

        self["ivertcon"] = self._determine_vertical_connection(self["iuzno"])

    def fill_stress_perioddata(self):
        """Modflow6 requires something to be filled in the stress perioddata, 
        even though the data is not used in the current configuration. 
        Only an infiltration rate is required,
        the rest can be filled with dummy values.
        """
        for var in self._binary_data:
            if self[var].size == 1: #Prevent loading large arrays in memory
                if self[var].values[()] is None:
                    self[var] = xr.full_like(self["infiltration_rate"], 0.0)
                else:
                    raise ValueError("{} cannot be a scalar".format(var))

    def _check_options(self, groundwater_ET_function, 
                       et_pot, extinction_depth, 
                       extinction_theta, air_entry_potential,
                       root_potential, root_activity):
        
        simulate_et = [x is not None for x in [et_pot, extinction_depth]]
        unsat_etae = [x is not None for x in [air_entry_potential, root_potential, root_activity]]
        
        if all(simulate_et):
            self["simulate_et"] = True
        elif any(simulate_et):
            raise ValueError("To simulate ET, set both et_pot and extinction_depth")
        
        if extinction_theta is not None:
            self["unsat_etwc"] = True
        
        if all(unsat_etae):
            self["unsat_etae"] = True
        elif any(unsat_etae):
            raise ValueError(
                    "To simulate ET with a capillary based formulation, set air_entry_potential, root_potential, and root_activity"
                    )
        
        if groundwater_ET_function not in ["linear", "square", None]:
            raise ValueError("Groundwater ET function should be either 'linear','square' or None")
        elif groundwater_ET_function == "linear":
            self["linear_gwet"] = True
        elif groundwater_ET_function == "square":
            self["square_gwet"] = True

    def _create_uzf_numbers(self, landflag):
        """Create unique UZF ID's. Inactive cells equal 0
        """
        return np.cumsum(np.ravel(landflag)).reshape(landflag.shape) * landflag

    def _determine_landflag(self, kv_sat):
        return (np.isfinite(kv_sat)).astype(np.int32)

    def _determine_vertical_connection(self, uzf_number):
        return uzf_number.shift(layer=-1, fill_value=0)

    def get_packagedata(self):
        """Use parent.to_sparse to get cellids
        """
        notnull = self["landflag"].values == 1
        iuzno = self["iuzno"].values[notnull]
        landflag = self["landflag"].values[notnull]
        ivertcon = self["ivertcon"].values[notnull]

        ds = self[[*self._package_data]]

        layer = self._check_layer_presence(ds)
        arrays = self._ds_to_arrlist(ds)

        listarr = super(BoundaryCondition, self).to_sparse(arrays, layer)

        field_spec = self._get_field_spec_from_dtype(listarr)
        field_names = [i[0] for i in field_spec]

        index_spec = [("iuzno", np.int32)] + field_spec[:3]
        field_spec = (
            [("landflag", np.int32)] + [("ivertcon", np.int32)] + field_spec[3:]
        )

        sparse_dtype = np.dtype(index_spec + field_spec)

        listarr_new = np.empty(listarr.shape, dtype=sparse_dtype)
        listarr_new["iuzno"] = iuzno
        listarr_new["landflag"] = landflag
        listarr_new["ivertcon"] = ivertcon
        listarr_new[field_names] = listarr

        return listarr_new

    def render(self, directory, pkgname, globaltimes):
        """Render fills in the template only, doesn't write binary data"""
        d = {}

        # period = {1: f"{directory}/{self._pkg_id}-{i}.bin"}

        bin_ds = self[[*self._binary_data]]

        d["periods"] = self.period_paths(directory, pkgname, globaltimes, bin_ds)

        not_options = (
            list(self._binary_data) + list(self._package_data) + ["iuzno" + "ivertcon"]
        )
        # construct the rest (dict for render)
        d = self.get_options(d, not_options=not_options)

        path = directory / pkgname / f"{self._pkg_id}-pkgdata.bin"
        d["packagedata"] = path.as_posix()

        d["nuzfcells"] = self._max_active_n()

        return self._template.render(d)

    def to_sparse(self, arrlist, layer):
        """Convert from dense arrays to list based input, 
        since the perioddata does not require cellids but iuzno, we hgave to override"""
        # TODO add pkgcheck that period table aligns
        # Get the number of valid values
        notnull = self["landflag"].values == 1
        iuzno = self["iuzno"].values
        nrow = notnull.sum()
        # Define the numpy structured array dtype
        index_spec = [("iuzno", np.int32)]
        field_spec = [(f"f{i}", np.float64) for i in range(len(arrlist))]
        sparse_dtype = np.dtype(index_spec + field_spec)

        # Initialize the structured array
        listarr = np.empty(nrow, dtype=sparse_dtype)
        # Fill in the indices
        listarr["iuzno"] = iuzno[notnull]

        # Fill in the data
        for i, arr in enumerate(arrlist):
            values = arr[notnull].astype(np.float64)
            listarr[f"f{i}"] = values

        return listarr

    def write(self, directory, pkgname, globaltimes):
        # Write Stress Period data and Options
        self.fill_stress_perioddata()
        super().write(directory, pkgname, globaltimes)

        outpath = directory / pkgname / f"{self._pkg_id}-pkgdata.bin"
        outpath.parent.mkdir(exist_ok=True, parents=True)

        package_data = self.get_packagedata()

        # Write PackageData
        self.write_textfile(outpath, package_data)
