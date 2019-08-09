from imod.mf6.pkgbase import BoundaryCondition


class GeneralHeadBoundary(BoundaryCondition):
    _pkg_id = "ghb"
    _binary_data = ("head", "conductance")

    def __init__(
        self,
        head,
        conductance,
        print_input=False,
        print_flows=False,
        save_flows=False,
        observations=None,
    ):
        self["head"] = head
        self["conductance"] = conductance
        self["print_input"] = print_input
        self["print_flows"] = print_flows
        self["save_flows"] = save_flows
        self["observations"] = observations
        self._initialize_template()
