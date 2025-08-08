"""
`dew_gwdata` provides internal access to DEW groundwater databases

"""

from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass

from .sageodata_database import *
from .sageodata_database import connect as connect_to_sageodata

sageodata = connect_to_sageodata

from .sageodata_datamart import get_sageodata_datamart_connection

from .wilma_reports import *

from ._gtslogs import *
from ._hydstra import *
from ._aquarius_ts import *
from ._aquarius_wp import *
from ._wde import *
from ._sagd_api import *
from .extraction_data import *
from .gwdata import *
from .utils import *

from .charts import *


register_aq_password("timeseries", "timeseries")
