from imod.flow.pkgbase import BoundaryCondition

class ConstantHead(BoundaryCondition):
    """
    The Constant Head package. The Time-Variant Specified-Head package is used
    to simulate specified head boundaries that can change within or between
    stress periods.

    Parameters
    ----------
    stage: xr.DataArray of floats
        is the head at the boundary
    """

    _pkg_id = "chd"
    _variable_order = ["head"]

    def __init__(self, head=None):
        super(__class__, self).__init__()
        self.dataset["head"] = head