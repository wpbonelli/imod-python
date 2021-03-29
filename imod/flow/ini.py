"""Some basic support for iMOD ini files here
"""
import collections
import jinja2
import abc
import imod.util


class IniFile(collections.UserDict, abc.ABC):
    # TODO: Create own key mapping to avoid keys like "edate"?
    _template = jinja2.Template(
        "{%- for key, value in settings %}\n" "{{key}}={{value}}\n" "{%- endfor %}\n"
    )

    def _format_datetimes(self):
        for timekey in ["sdate", "edate"]:
            if timekey in self.keys():
                # If not string assume it is in some kind of datetime format
                if type(self[timekey]) != str:
                    self[timekey] = imod.util._compose_timestring(self[timekey])

    def render(self):
        self._format_datetimes()
        return self._template.render(settings=self.items())


class ImodflowConversion(IniFile):
    def __init__(self, **kwargs):
        super(__class__, self).__init__(**kwargs)
        self["function"] = "runfile"
        self["sim_type"] = 1


class Modflow2005Conversion(IniFile):
    def __init__(self, **kwargs):
        super(__class__, self).__init__(**kwargs)
        self["function"] = "runfile"
        self["sim_type"] = 2


class Modflow6Conversion(IniFile):
    def __init__(self, **kwargs):
        super(__class__, self).__init__(**kwargs)
        self["function"] = "runfile"
        self["sim_type"] = 3
