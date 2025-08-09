# from pkg_resources import get_distribution, DistributionNotFound

# try:
#     __version__ = get_distribution("atpdataset").version
# except DistributionNotFound:
#     # package is not installed
#     __version__ = None
#     pass

# from importlib.metadata import version

from . import dataframe, io
from .csv_object import Csv
from .dataset_ts_long import AtpDatasetTsLong
from .dict_default import DictDefault
from .histogram import HistogramContinue
from .records import Records
# __version__ = version("atpdataset")
