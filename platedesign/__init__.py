"""
Tools for designing plate experiments

"""

# Versions should comply with PEP440. For a discussion on single-sourcing
# the version across setup.py and the project code, see
# https://packaging.python.org/en/latest/single_source_version.html
__version__ = '1.0.0'

from . import experiment
from . import inducer
from . import plate

# Change pandas header style
import pandas
import pandas.io.formats.excel
pandas.io.formats.excel.header_style = {"font": {"bold": True,
                                                 "color": "FF1F497D"}}
