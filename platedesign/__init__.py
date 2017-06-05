"""
Tools for designing plate experiments

"""

# Versions should comply with PEP440. For a discussion on single-sourcing
# the version across setup.py and the project code, see
# https://packaging.python.org/en/latest/single_source_version.html
__version__ = '0.4.0'

import packaging
import packaging.version

from . import experiment
from . import inducer
from . import plate

# Change pandas header style
import pandas
if packaging.version.parse(pandas.__version__) \
        < packaging.version.parse('0.18'):
    format_module = pandas.core.format
elif packaging.version.parse(pandas.__version__) \
        < packaging.version.parse('0.20'):
    format_module = pandas.formats.format
else:
    import pandas.io.formats.excel
    format_module = pandas.io.formats.excel

format_module.header_style = {"font": {"bold": True,
                                       "color": "FF1F497D"}}
