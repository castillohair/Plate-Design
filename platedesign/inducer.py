"""
Module that contains inducer classes.

"""

import copy
import os
import random

import numpy
import openpyxl
import pandas

import platedesign.math

class Inducer(object):
    """
    Generic class that represents an inducer.

    """
    def __init__(self, name, units, id_prefix=None, id_offset=0):
        # Store name and units
        self.name = name
        self.units = units

        # Store ID modifiers for dilutions table
        if id_prefix is None:
            id_prefix=name[0]
        self.id_prefix=id_prefix
        self.id_offset=id_offset

    @property
    def conc(self):
        """
        Inducer concentration of each dilution.

        """
        raise NotImplementedError

    def set_gradient(self,
                     min,
                     max,
                     n,
                     scale='linear',
                     use_zero=False,
                     n_repeat=1):
        """
        Set the dilutions concentrations from a specified gradient.

        """
        raise NotImplementedError

    def calculate_vol(self,
                      n_samples,
                      n_replicates=1,
                      safety_factor=1.2):
        """
        Calculate inducer total and per-aliquot volumes.

        """
        raise NotImplementedError

    def calculate_recipe(self):
        """
        Calculate instructions to prepare each inducer dilution.

        """
        raise NotImplementedError

    def save_files(self,
                   file_name,
                   sheet_name=None,
                   path='.',
                   ):
        """
        Save the (unshuffled) dilutions table into an Excel file.

        """
        raise NotImplementedError

    def generate_shufflings(self, n_shufflings):
        """
        Generate and store random shufflings for the dilutions table.

        """
        raise NotImplementedError

    def shuffle(self, shuffling=None):
        """
        Apply random shuffling to the dilutions table.

        """
        raise NotImplementedError

    def split(self, n_splits, split_shuffled=False):
        """
        Create inducer objects from a subset of this object's dilutions.

        """
        raise NotImplementedError


class ChemicalInducer(Inducer):
    """
    Object that represents a series of dilutions of a chemical inducer.

    Parameters
    ----------
    name : str
        Name of the inducer, to be used in generated files.
    units : str
        Units in which the inducer's concentration is expressed. This is
        used in generated files.
    id_prefix : str, optional
        Prefix to be used for the ID that identifies each inducer dilution.
        If None, use the first letter of the inducer's name.
    if_offset : int, optional
        Offset from which to generate the ID that identifies each inducer
        dilution. Default: 0 (no offset).

    Attributes
    ----------
    name : str
        Name of the inducer, to be used in generated files.
    units : str
        Units in which the inducer's concentration is expressed.
    id_prefix : str
        Prefix to be used for the ID that identifies each inducer dilution.
    id_offset : int
        Offset from which to generate the ID that identifies each inducer
        dilution.
    stock_conc : float
        Concentration of the stock solution of the inducer.
    sample_vol : float
        Volume of cell sample in which the inducer will be inoculated.
    inoculation_vol : float
        Volume of inducer to inoculate in each cell sample.
    total_vol : float
        Total volume of inducer to make per dilution.
    replicate_vol : float
        Volume of inducer to make for each experiment replicate, per
        dilution.
    min_stock_vol : float
        Minimum volume of stock inducer to use when preparing the
        dilutions.
    max_stock_vol : float
        Maximum volume of stock inducer to use when preparing the
        dilutions.
    stock_dilution_step : float
        Dilution ratio to make from the stock solution on each dilution
        step.
    stock_decimals : int
        Number of decimals to use for the volume of stock inducer.
    water_decimals : int
        Number of decimals to use for the volume of water.
    dilutions : DataFrame
        Table containing information of all the inducer dilutions.
    shufflings : list
        List of randomized indices to use when shuffling the dilutions
        table.
    current_shuffling : list
        Randomized indices that result in the current shuffling of
        dilutions.

    Methods
    -------
    reset
        Delete the dilutions table and shufflings.
    set_gradient
        Set inducer concentrations from a specified gradient.
    calculate_vol
        Calculate inducer total and per-aliquot volumes.
    calculate_recipe
        Calculate instructions to prepare each inducer dilution.
    save_dilutions_table
        Save the dilutions table into an Excel file.
    generate_shufflings
        Generate and store random shufflings for the dilutions table.
    shuffle
        Apply random shuffling to the dilutions table.
    split
        Create inducer objects from a subset of this object's dilutions.


    """
    def __init__(self, name, units, id_prefix=None, id_offset=0):
        # Store name and units
        self.name = name
        self.units = units

        # Store ID modifiers for dilutions table
        if id_prefix is None:
            id_prefix=name[0]
        self.id_prefix=id_prefix
        self.id_offset=id_offset

        # Initialize main properties used for calculations
        # Stock concentration of inducer
        self.stock_conc = None
        # Volume of cell sample
        self.sample_vol = None
        # Volume of inducer dilution that will go into each cell sample
        self.inoculation_vol = None

        # Total volume of inducer to make
        self.total_vol = None
        # Volume to aliquot
        self.replicate_vol = None

        # Initialize secondary properties used for calculations
        self.min_stock_vol = 1.5
        self.max_stock_vol = 20.
        self.stock_dilution_step = 10.
        self.stock_decimals = 2
        self.water_decimals = 1

        # Reset all structures
        self.reset()

    def __str__(self):
        return "{}, {} different concentration(s)".format(
            self.name,
            len(self.dilutions))

    @property
    def conc_header(self):
        """
        Header to be used in the dilutions table to specify concentration.

        """
        return "Concentration ({})".format(self.units)

    @property
    def conc(self):
        """
        Inducer concentration of each dilution.

        Reading from this attribute will return the contents of the
        "Concentration" column from the dilutions table. Writing to this
        attribute will reinitialize the dilutions table with the specified
        concentrations. Any columns that are not the concentrations or
        IDs will be lost.

        """
        return self.dilutions[self.conc_header].values

    @conc.setter
    def conc(self, value):
        # Initialize dataframe with dilutions info
        ids = ['{}{:03d}'.format(self.id_prefix, i)
               for i in range(self.id_offset + 1,
                              len(value) + self.id_offset + 1)]
        self._dilutions = pandas.DataFrame({'ID': ids})
        self._dilutions.set_index('ID', inplace=True)
        self._dilutions[self.conc_header] = value

    @property
    def dilutions(self):
        """
        Table containing information of all the inducer dilutions.

        """
        if self.current_shuffling is None:
            return self._dilutions
        else:
            return self._dilutions.iloc[self.shufflings[self.current_shuffling]]

    def reset(self):
        """
        Delete the dilutions table and shufflings.

        """
        # The following initializes an empty dilutions table
        self.conc = [0]
        # Shuffling indices
        self.shufflings = None
        # Remove current shuffling
        self.current_shuffling = None

    def set_gradient(self,
                     min,
                     max,
                     n,
                     scale='linear',
                     use_zero=False,
                     n_repeat=1):
        """
        Set inducer concentrations from a specified gradient.

        Using this function will reset the dilutions table and populate the
        "Concentration" column with the specified gradient.

        Parameters
        ----------
        min, max : float
            Minimum and maximum values on the gradient.
        n : int
            Number of points to use for the gradient.
        scale : {'linear', 'log'}, optional
            Whether to generate the gradient with linear or logarithmic
            spacing.
        use_zero : bool, optional.
            If ``scale`` is 'log', use zero as well. Ignored if ``scale``
            is 'linear'.
        n_repeat : int, optional
            How many times to repeat each concentration. Default: 1 (no
            repeat). Should be an exact divisor of ``n``.

        """
        # Check that n_repeat is an exact divisor of n
        if n%n_repeat != 0:
            raise ValueError("n should be a multiple of n_repeat")

        # Calculate gradient
        if scale == 'linear':
            self.conc = numpy.linspace(min, max, n/n_repeat)
            self.conc = numpy.repeat(self.conc, n_repeat)
        elif scale == 'log':
            if use_zero:
                self.conc = numpy.logspace(numpy.log10(min),
                                           numpy.log10(max),
                                           (n/n_repeat - 1))
                self.conc = numpy.concatenate(([0], self.conc))
            else:
                self.conc = numpy.logspace(numpy.log10(min),
                                           numpy.log10(max),
                                           n/n_repeat)
            self.conc = numpy.repeat(self.conc, n_repeat)
        else:
            raise ValueError("scale {} not recognized".format(scale))

    def calculate_vol(self,
                      n_samples,
                      n_replicates=1,
                      safety_factor=1.2):
        """
        Calculate inducer total and per-aliquot volumes.

        This calculation is based on a specified number of samples and
        replicates. Results are stored in the ``replicate_vol`` and
        ``total_vol`` attributes.

        Parameters
        ----------
        n_samples : int
            Number of samples per replicate.
        n_replicates : int, optional
            Number of experimental replicates. Default is one.
        safety_factor : float, optional
            Should be greater than one. The calculated volumes will be
            multiplied by this number to have a little excess liquid when
            pipetting.

        """
        # Calculate volume with safety factor for a replicate
        inducer_rep_vol = n_samples*self.inoculation_vol
        inducer_rep_vol = inducer_rep_vol*safety_factor
        inducer_rep_vol = platedesign.math._ceil_log(inducer_rep_vol)

        if n_replicates > 1:
            # Calculate total amount of inducer
            self.total_vol = inducer_rep_vol*n_replicates
            # Apply safety factor and round again
            self.total_vol = platedesign.math._ceil_log(
                self.total_vol*safety_factor)
            # Store aliquot volume
            self.replicate_vol = inducer_rep_vol
        else:
            # Store replicate volume as total volume
            self.total_vol = inducer_rep_vol
            self.replicate_vol = None

    def calculate_recipe(self):
        """
        Calculate instructions to prepare each inducer dilution.

        The indicated concentrations are achieved when pipetting a volume
        "inoculation_vol" of dilution into a sample with a volume of
        "sample_vol". Additional attributes that need to be set are
        "stock_conc" and "total_vol". Instructions are stored in the
        dilutions table, in columns "Stock dilution",
        "Inducer volume (uL)", and "Water volume (uL)". To prepare the
        dilutions, the stock solution is expected to be diluted by the
        factor specified in "Stock dilution". Next, a volume of this
        indicated in the column "Inducer volume (uL)" is expected to be
        mixed with water, as specified in "Water volume (uL)". In addition,
        the concentrations are updated to reflect the finite resolution of
        the pipettes, as specified by the properties "stock_decimals" and
        "water_decimals".

        """
        # Check for the presence of required attributes
        if self.stock_conc is None:
            raise AttributeError("stock_conc should be set")
        if self.sample_vol is None:
            raise AttributeError("sample_vol should be set")
        if self.inoculation_vol is None:
            raise AttributeError("inoculation_vol should be set")
        if self.total_vol is None:
            raise AttributeError("total_vol should be set")

        # Initialize relevant arrays
        concentrations = self._dilutions[self.conc_header].values
        inducer_vols = numpy.zeros_like(concentrations)
        inducer_dils = numpy.zeros_like(concentrations)
        water_vols = numpy.zeros_like(concentrations)
        actual_concs = numpy.zeros_like(concentrations)

        # Iterate over concentrations
        for i, conc in enumerate(concentrations):
            # If concentration is zero, skip
            if conc == 0:
                inducer_dils[i] = 0
                inducer_vols[i] = 0
                water_vols[i] = self.total_vol
                continue
            # Determine the appropriate dilution to use
            # We start with a high dilution, and scale down until we reach a
            # volume that is acceptable (lower than max_stock_volume)
            dilution = self.stock_dilution_step**10
            while True:
                inducer_vol = (conc*self.sample_vol/self.inoculation_vol) * \
                    self.total_vol / (self.stock_conc/dilution)
                if (inducer_vol < self.max_stock_vol):
                    break
                if dilution/self.stock_dilution_step < 1:
                    break
                dilution = dilution/self.stock_dilution_step
            # Round inducer volume to the specified precision
            inducer_vol = numpy.round(inducer_vol,
                                      decimals=self.stock_decimals)
            # Water volume is the remaining volume
            water_vol = numpy.round(self.total_vol - inducer_vol,
                                    decimals=self.water_decimals)
            # Actual concentration achieved
            actual_conc = self.stock_conc/dilution * \
                          inducer_vol/(inducer_vol + water_vol) * \
                          (self.inoculation_vol/self.sample_vol)
            # Accumulate
            inducer_dils[i] = dilution
            inducer_vols[i] = inducer_vol
            water_vols[i] = water_vol
            actual_concs[i] = actual_conc

        # Append to dilutions table
        self._dilutions[self.conc_header] = actual_concs
        self._dilutions['Stock dilution'] = inducer_dils
        self._dilutions['Inducer volume (uL)'] = inducer_vols
        self._dilutions['Water volume (uL)'] = water_vols

    def save_files(self,
                   file_name,
                   sheet_name=None,
                   path='.',
                   ):
        """
        Save the (unshuffled) dilutions table into an Excel file.

        Parameters
        ----------
        file_name : str
            Name of the Excel file on which to save the dilutions table.
        sheet_name : str, optional
            Name of the sheet on which to save the dilutions table. If not
            specified, use the inducer's name.
        path : str, optional
            Path of the directory in which to save the dilutions file.

        """
        # Autogenerate sheet name if necessary
        if sheet_name is None:
            sheet_name = self.name
        # Generate full file name
        full_file_name = os.path.join(path, file_name)
        # Generate pandas writer
        writer = pandas.ExcelWriter(full_file_name, engine='openpyxl')
        # If file already exists, open and copy all previous data
        if os.path.isfile(full_file_name):
            workbook = openpyxl.load_workbook(full_file_name)
            writer.book = workbook
            writer.sheets = dict((ws.title, ws)
                                 for ws in workbook.worksheets)
        # Convert dilutions table to excel sheet
        self._dilutions.to_excel(writer, sheet_name=sheet_name)
        # Add message about aliquots
        if self.replicate_vol is not None:
            message = "Distribute in aliquots of {}uL." \
                .format(self.replicate_vol)
            worksheet = writer.sheets[sheet_name]
            worksheet.cell(row=len(self._dilutions) + 3,
                           column=1,
                           value=message)
        # Actually save
        writer.save()

    def generate_shufflings(self, n_shufflings):
        """
        Generate and store random shufflings for the dilutions table.

        Each shuffling is stored as a list of randomized indices for the
        dilutions table.

        Parameters
        ----------
        n_shufflings : int
            Number of shufflings to generate.

        """
        # Generate random shufflings
        self.shufflings = []
        for i in range(n_shufflings):
            l = range(len(self.dilutions))
            random.shuffle(l)
            self.shufflings.append(l)

    def shuffle(self, shuffling=None):
        """
        Apply random shuffling to the dilutions table.

        Does nothing if `generate_shufflings()` hasn't been called yet.

        Parameters
        ----------
        shuffling : int
            Index of the random shuffling to use. Values are from 0 to
            ``n_shufflings - 1``, where ``n_shufflings`` is the argument of
            ``generate_shufflings()``. If None, use the unshuffled
            dilutions table.

        """
        # If shufflings has not been initialized, shuffling is not possible.
        if self.shufflings is None:
            return
        # Check for range of shuffling
        if (shuffling is not None) and \
                ((shuffling >= len(self.shufflings)) or (shuffling < 0)):
            raise ValueError("shuffling should be between zero and {}".format(
                len(self.shufflings) - 1))

        self.current_shuffling = shuffling

    def split(self, n_splits, split_shuffled=False):
        """
        Create inducer objects from a subset of this object's dilutions.

        The resulting objects are identical to the current one, but contain
        a subset of the dilutions made by splitting the dilutions table
        into ``n_splits`` parts. The "id_offset" attribute is not
        preserved.

        Parameters
        ----------
        n_splits : int
            Number of split inducer objects to create.
        split_shuffled : bool
            Whether to split the shuffled or unshuffled table.

        Returns
        -------
        splits : list
            List of chemical inducer objects, made from splitting the
            dilutions of this object.

        """
        # Trivial case: one split
        if n_splits==1:
            return [copy.deepcopy(self)]

        # Initialize list to accumulate splits
        splits = []
        # length of dilutions table per split
        split_length = len(self.dilutions)/n_splits
        for i in range(n_splits):
            # Copy inducer object
            split = copy.deepcopy(self)
            # Slice dilutions table
            if split_shuffled:
                split._dilutions = \
                    split.dilutions.iloc[i*split_length:(i+1)*split_length]
            else:
                split._dilutions = \
                    split._dilutions.iloc[i*split_length:(i+1)*split_length]
            # Shuffling information is no longer valid, delete
            split.current_shuffling = None
            split.shufflings = None
            # Delete id_offset
            split.id_offset = None
            # Accumulate
            splits.append(split)

        return splits