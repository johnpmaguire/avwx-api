"""
Michael duPont - michael@mdupont.com
avwx_api.api.station - Station API endpoints
"""

# stdlib
from dataclasses import asdict

# library
from quart import Response
from quart_openapi.cors import crossdomain

# module
import avwx
from avwx_api import app, structs, validate
from avwx_api.api import Base, HEADERS, parse_params, token_check


@app.route("/api/station/<station>")
class Station(Base):
    """
    Returns station details for ICAO and coordinates
    """

    validator = validate.station
    struct = structs.StationParams
    report_type = "station"

    @crossdomain(origin="*", headers=HEADERS)
    @parse_params
    @token_check
    async def get(self, params: structs.Params) -> Response:
        """
        Returns raw station info if available
        """
        await app.station.add(params.station.icao, "station")
        return self.make_response(asdict(params.station), params.format)


@app.route("/api/station/near/<coord>")
class Near(Base):
    """
    Returns stations near a coordinate pair
    """

    validator = validate.coord_search
    struct = structs.CoordSearchParams
    report_type = "station"
    loc_param = "coord"
    example = "stations_near"
    plan_types = ("pro", "enterprise")

    @crossdomain(origin="*", headers=HEADERS)
    @parse_params
    @token_check
    async def get(self, params: structs.Params) -> Response:
        """
        Returns raw station info if available
        """
        stations = avwx.station.nearest(
            *params.coord, params.n, params.airport, params.reporting, params.maxdist
        )
        if isinstance(stations, dict):
            stations = [stations]
        for i, stn in enumerate(stations):
            stations[i]["station"] = asdict(stn["station"])
        return self.make_response(stations, params.format)
