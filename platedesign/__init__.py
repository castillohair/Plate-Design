"""
Tools for designing plate experiments

"""

# Versions should comply with PEP440. For a discussion on single-sourcing
# the version across setup.py and the project code, see
# https://packaging.python.org/en/latest/single_source_version.html
__version__ = '0.3.0'

import experiment
import inducer
import plate

# Change pandas header style
import pandas
pandas.formats.format.header_style = {"font": {"bold": True,
                                               "color": "FF1F497D"}}