from imod.pkg.pkgbase import BoundaryCondition

class ConstantHead(BoundaryCondition):
    _pkg_id = "chd"
    def __init__(self, head_start, head_end, conc):
        super(__class__, self).__init__()
