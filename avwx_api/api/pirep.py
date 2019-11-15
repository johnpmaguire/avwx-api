"""
Michael duPont - michael@mdupont.com
avwx_api.api.pirep - PIREP API endpoints
"""

from avwx_api import app, structs, validate
from avwx_api.api import Report, Parse

_key_remv = ["direction"]


@app.route("/api/pirep/<location>")
class Pirep(Report):

    report_type = "pirep"
    loc_param = "location"
    plan_types = ("pro", "enterprise")
    struct = structs.ReportLocationParams
    validator = validate.report_location

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._key_remv = _key_remv


@app.route("/api/parse/pirep")
class PirepParse(Parse):

    report_type = "pirep"
    plan_types = ("pro", "enterprise")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._key_remv = _key_remv
