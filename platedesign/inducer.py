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

class InducerBase(object):
    """
    Generic class that represents one or more doses of an inducer.

    This class is meant to be inherited by a class representing a concrete
    inducer type. Functions that don't save files here raise a
    NotImplementedError to force the child class to implement its own
    version. Functions that save files are implemented as empty functions,
    such that a child class only needs to redefine the necessary functions
    depending on which files it has to save.

    Attributes
    ----------
    name : str
        Name of the inducer.
    doses_table : DataFrame
        Table with information of each inducer dose.

    Methods
    -------
    set_vol_from_shots
        Set volume to prepare from number of shots and replicates.
    shuffle
        Apply random shuffling to the dose table.
    save_exp_setup_instructions
        Save instructions for the Experiment Setup stage.
    save_exp_setup_files
        Save additional files for the Experiment Setup stage.
    save_rep_setup_instructions
        Save instructions for the Replicate Setup stage.
    save_rep_setup_files
        Save additional files for the Replicate Setup stage.

    """
    def __init__(self, name):
        # Store name
        self.name = name

        # Initialize dose table
        self.doses_table = pandas.DataFrame()

    def set_vol_from_shots(self,
                           n_shots,
                           n_replicates=1):
        """
        Set volume to prepare from number of shots and replicates.

        """
        raise NotImplementedError

    def shuffle(self):
        """
        Apply random shuffling to the dose table.

        """
        raise NotImplementedError

    def save_exp_setup_instructions(self, file_name=None, workbook=None):
        """
        Calculate and save instructions for the Experiment Setup stage.

        Parameters
        ----------
        file_name : str, optional
            Name of the Excel file to save.
        workbook : Workbook, optional
            If not None, `file_name` is ignored, and a sheet with the
            instructions is directly added to workbook `workbook`.

        """
        pass

    def save_exp_setup_files(self, path='.'):
        """
        Save additional files required for the experiment setup stage.

        Parameters
        ----------
        path : str
            Folder in which to save files.

        """
        pass

    def save_rep_setup_instructions(self, file_name=None, workbook=None):
        """
        Calculate and save instructions for the Replicate Setup stage.

        Parameters
        ----------
        file_name : str, optional
            Name of the Excel file to save.
        workbook : Workbook, optional
            If not None, `file_name` is ignored, and a sheet with the
            instructions is directly added to workbook `workbook`.

        """
        pass

    def save_rep_setup_files(self, path='.'):
        """
        Save additional files required for the experiment setup stage.

        Parameters
        ----------
        path : str
            Folder in which to save files.

        """
        pass


class ChemicalInducer(InducerBase):
    """
    Object that represents different concentrations of a chemical inducer.

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
    id_offset : int, optional
        Offset from which to generate the ID that identifies each inducer
        dilution. Default: 0 (no offset).

    Attributes
    ----------
    name : str
        Name of the inducer.
    units : str
        Units in which the inducer's concentration is expressed.
    id_prefix : str
        Prefix to be used for the ID that identifies each inducer
        concentration.
    id_offset : int
        Offset from which to generate the ID that identifies each inducer
        concentration.
    stock_conc : float
        Concentration of the stock solution of the inducer.
    media_vol : float
        Volume of sample media in which the inducer will be added.
    shot_vol : float
        Volume of inducer to add to each sample.
    total_vol : float
        Total volume of inducer to make per dose.
    replicate_vol : float
        Volume of inducer to make for each experiment replicate, per dose.
    concentrations : array
        Inducer concentrations.
    doses_table : DataFrame
        Table containing information of all the inducer concentrations.

    Methods
    -------
    set_gradient
        Set inducer concentrations from a specified gradient.
    set_vol_from_shots
        Set volume to prepare from number of shots and replicates.
    shuffle
        Apply random shuffling to the dose table.
    save_exp_setup_instructions
        Save instructions for the Experiment Setup stage.

    Other Attributes
    ----------------
    vol_safety_factor : float
        Safety factor used when calculating the total inducer volume to
        prepare.
    min_stock_vol : float
        Minimum volume of stock inducer to use when preparing dilutions
        during the experiment setup stage.
    max_stock_vol : float
        Maximum volume of stock inducer to use when preparing dilutions
        during the experiment setup stage.
    stock_dilution_step : float
        Dilution ratio to make from the stock solution on each dilution
        step.
    stock_decimals : int
        Number of decimals to use for the volume of stock inducer.
    water_decimals : int
        Number of decimals to use for the volume of water.
    shuffled_idx : list
        Randomized indices that result in the current shuffling of
        dilutions.

    """
    def __init__(self, name, units, id_prefix=None, id_offset=0):
        # Store name and units
        self.name = name
        self.units = units

        # Store ID modifiers for dose table
        if id_prefix is None:
            id_prefix=name[0]
        self.id_prefix=id_prefix
        self.id_offset=id_offset

        # Initialize main properties used for calculations
        self.stock_conc = None
        self.media_vol = None
        self.shot_vol = None
        self.total_vol = None
        self.replicate_vol = None

        # Initialize secondary properties used for calculations
        self.vol_safety_factor = 1.2
        self.min_stock_vol = 1.5
        self.max_stock_vol = 20.
        self.stock_dilution_step = 10.
        self.stock_decimals = 2
        self.water_decimals = 1

        # The following initializes an empty dose table
        self.dose = [0]
        # Remove shuffling
        self.shuffled_idx = None

    @property
    def concentrations_header(self):
        """
        Header to be used in the dose table to specify concentration.

        """
        return "{} Concentration ({})".format(self.name, self.units)

    @property
    def concentrations(self):
        """
        Inducer concentrations.

        Reading from this attribute will return the contents of the
        "Concentration" column from the dose table. Writing to this
        attribute will reinitialize the doses table with the specified
        concentrations. Any columns that are not the concentrations or
        IDs will be lost.

        """
        return self.doses_table[self.concentrations_header].values

    @concentrations.setter
    def concentrations(self, value):
        # Initialize dataframe with doses info
        ids = ['{}{:03d}'.format(self.id_prefix, i)
               for i in range(self.id_offset + 1,
                              len(value) + self.id_offset + 1)]
        self._doses_table = pandas.DataFrame({'ID': ids})
        self._doses_table.set_index('ID', inplace=True)
        self._doses_table[self.concentrations_header] = value

    @property
    def doses_table(self):
        """
        Table containing information of all the inducer concentrations.

        """
        if self.shuffled_idx is None:
            return self._doses_table
        else:
            return self._doses_table.iloc[self.shuffled_idx]

    def set_gradient(self,
                     min,
                     max,
                     n,
                     scale='linear',
                     use_zero=False,
                     n_repeat=1):
        """
        Set inducer concentrations from a specified gradient.

        Using this function will reset the dose table and populate the
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
            self.concentrations = numpy.linspace(min, max, n/n_repeat)
            self.concentrations = numpy.repeat(self.concentrations, n_repeat)
        elif scale == 'log':
            if use_zero:
                self.concentrations = numpy.logspace(numpy.log10(min),
                                                     numpy.log10(max),
                                                     (n/n_repeat - 1))
                self.concentrations = \
                    numpy.concatenate(([0], self.concentrations))
            else:
                self.concentrations = numpy.logspace(numpy.log10(min),
                                                     numpy.log10(max),
                                                     n/n_repeat)
            self.concentrations = numpy.repeat(self.concentrations, n_repeat)
        else:
            raise ValueError("scale {} not recognized".format(scale))

    def set_vol_from_shots(self,
                           n_shots,
                           n_replicates=1):
        """
        Set volume to prepare from number of shots and replicates.

        This calculation is based on a specified number of shots and
        replicates. Results are stored in the ``replicate_vol`` and
        ``total_vol`` attributes. The attribute ``vol_safety_factor``
        should be set for this function.

        Parameters
        ----------
        n_shots : int
            Number of samples in which to add inducer, per dose, per
            replicate.
        n_replicates : int, optional
            Number of experimental replicates. Default is one.

        """
        # Check for the presence of required attributes
        if self.vol_safety_factor is None:
            raise AttributeError("vol_safety_factor should be set")

        # Calculate volume with safety factor for a replicate
        inducer_rep_vol = n_shots*self.shot_vol
        inducer_rep_vol = inducer_rep_vol*self.vol_safety_factor
        inducer_rep_vol = platedesign.math._ceil_log(inducer_rep_vol)

        if n_replicates > 1:
            # Calculate total amount of inducer
            self.total_vol = inducer_rep_vol*n_replicates
            # Apply safety factor and round again
            self.total_vol = platedesign.math._ceil_log(
                self.total_vol*self.vol_safety_factor)
            # Store aliquot volume
            self.replicate_vol = inducer_rep_vol
        else:
            # Store replicate volume as total volume
            self.total_vol = inducer_rep_vol
            self.replicate_vol = None

    def shuffle(self):
        """
        Apply random shuffling to the dose table.

        """
        # Create list of indices, shuffle, and store.
        shuffled_idx = range(len(self.doses_table))
        random.shuffle(shuffled_idx)
        self.shuffled_idx = shuffled_idx

    def save_exp_setup_instructions(self, file_name=None, workbook=None):
        """
        Calculate and save instructions for the Experiment Setup stage.

        During the replicate setup stage, the indicated concentrations of
        inducer will be achieved by pipetting a volume "shot_vol" of
        intermediate inducer dilution into a sample with a volume of
        "media_vol". These intermediate dilutions are to be prepared during
        the experiment setup stage, according to the instructions generated
        by this function.

        The instructions are saved to a single Excel sheet, named after
        the inducer. To prepare the dilutions, the stock solution should be
        diluted by the factor specified in "Stock dilution". Next, the
        volume of stock dilution indicated in "Inducer volume (uL)" should
        be mixed with a volume of water specified in "Water volume (uL)".

        Additional class properties that need to be set are "stock_conc"
        and "total_vol". This function modifies the specified
        concentrations to reflect the finite resolution of the pipettes, as
        specified by the class properties "stock_decimals" and
        "water_decimals".

        Parameters
        ----------
        file_name : str, optional
            Name of the Excel file to save.
        workbook : Workbook, optional
            If not None, `file_name` is ignored, and a sheet with the
            instructions is directly added to workbook `workbook`.

        """
        # Check for the presence of required attributes
        if self.stock_conc is None:
            raise AttributeError("stock_conc should be set")
        if self.media_vol is None:
            raise AttributeError("media_vol should be set")
        if self.shot_vol is None:
            raise AttributeError("shot_vol should be set")
        if self.total_vol is None:
            raise AttributeError("total_vol should be set")

        # Initialize relevant arrays
        target_concs = self.concentrations
        stock_dils = numpy.zeros_like(target_concs)
        inducer_vols = numpy.zeros_like(target_concs)
        water_vols = numpy.zeros_like(target_concs)
        actual_concs = numpy.zeros_like(target_concs)

        # Iterate over concentrations
        for i, target_conc in enumerate(target_concs):
            # If concentration is zero, skip
            if target_conc == 0:
                stock_dils[i] = 0
                inducer_vols[i] = 0
                water_vols[i] = self.total_vol
                continue
            # Determine the appropriate dilution to use
            # We start with a high dilution, and scale down until we reach a
            # volume that is acceptable (lower than max_stock_volume)
            stock_dil = self.stock_dilution_step**10
            while True:
                inducer_vol = (target_conc*self.media_vol/self.shot_vol) * \
                    self.total_vol / (self.stock_conc/stock_dil)
                if (inducer_vol < self.max_stock_vol):
                    break
                if stock_dil/self.stock_dilution_step < 1:
                    break
                stock_dil = stock_dil/self.stock_dilution_step
            # Round inducer volume to the specified precision
            inducer_vol = numpy.round(inducer_vol,
                                      decimals=self.stock_decimals)
            # Water volume is the remaining volume
            water_vol = numpy.round(self.total_vol - inducer_vol,
                                    decimals=self.water_decimals)
            # Actual concentration achieved
            actual_conc = self.stock_conc/stock_dil * \
                          inducer_vol/(inducer_vol + water_vol) * \
                          (self.shot_vol/self.media_vol)
            # Accumulate
            stock_dils[i] = stock_dil
            inducer_vols[i] = inducer_vol
            water_vols[i] = water_vol
            actual_concs[i] = actual_conc

        # Build table with instructions
        instructions = self._doses_table.copy()

        instructions[self.concentrations_header] = actual_concs
        instructions['Stock dilution'] = stock_dils
        instructions['Inducer volume (uL)'] = inducer_vols
        instructions['Water volume (uL)'] = water_vols

        if workbook is not None:
            # First, check that a sheet with the inducer name doesn't exist
            sheet_name = self.name
            if sheet_name in [ws.title for ws in workbook.worksheets]:
                raise ValueError("sheet \"{}\"already present in workbook".\
                    format(sheet_name))
            # Generate pandas writer and reassign workbook
            writer = pandas.ExcelWriter('temp', engine='openpyxl')
            writer.book = workbook
        else:
            # Generate pandas writer to a new file
            writer = pandas.ExcelWriter(file_name, engine='openpyxl')

        # Save instructions table
        instructions.to_excel(writer, sheet_name=sheet_name)
        # Add message about aliquots
        if self.replicate_vol is not None:
            message = "Distribute in aliquots of {}uL." \
                .format(self.replicate_vol)
            worksheet = writer.sheets[sheet_name]
            worksheet.cell(row=len(instructions) + 3,
                           column=1,
                           value=message)

        # Save file if necessary
        if workbook is None:
            # Actually save
            writer.save()

        # Update concentration array in class
        self._doses_table[self.concentrations_header] = actual_concs