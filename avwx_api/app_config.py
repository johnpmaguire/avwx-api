"""
Michael duPont - michael@mdupont.com
avwx_api.__init__ - High-level Quart application
"""

# stdlib
from os import environ

# library
import rollbar
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from quart import got_request_exception
from quart_openapi import Pint
from rollbar.contrib.quart import report_exception

# module
from avwx import exceptions as avwx_exceptions
from avwx_api_core.app import add_cors, CustomJSONEncoder
from avwx_api_core.cache import CacheManager
from avwx_api_core.token import TokenManager
from avwx_api.station_counter import StationCounter


load_dotenv()


CACHE_EXPIRES = {"metar": 1, "taf": 1, "awdata": 60 * 24}
MONGO_URI = environ.get("MONGO_URI")


app = Pint(__name__)
app.json_encoder = CustomJSONEncoder
app.after_request(add_cors)


@app.before_serving
async def init_helpers():
    """Init API helpers

    Need async to connect helpers to event loop
    """
    app.mdb = AsyncIOMotorClient(MONGO_URI) if MONGO_URI else None
    app.cache = CacheManager(app, expires=CACHE_EXPIRES)
    app.token = TokenManager(app)
    app.station = StationCounter(app)
    app.cache_only = {}


@app.before_first_request
def init_rollbar():
    """Initialize Rollbar exception logging"""
    key = environ.get("LOG_KEY")
    if not (key and app.env == "production"):
        return
    rollbar.init(key, root="avwx_api", allow_logging_basic_config=False)
    got_request_exception.connect(report_exception, app, weak=False)

    def exception_intercept(exception: Exception, **extra: dict) -> None:
        rollbar.report_exc_info(exception, extra_data=extra)

    avwx_exceptions.exception_intercept = exception_intercept


@app.before_first_request
async def init_cache_only_map():
    """Fetch cache-only station lists for the duration of the worker"""
    if app.mdb is None:
        return
    for table in ("awos",):
        codes = await app.mdb.cache[table].distinct("_id")
        app.cache_only.update({code: table for code in codes})
