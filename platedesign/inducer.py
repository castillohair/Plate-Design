# -*- coding: UTF-8 -*-
"""
Module that contains inducer classes.

"""

import random

import numpy
import openpyxl
import pandas

import platedesign.math

class InducerBase(object):
    """
    Generic class that represents one or more doses of an inducer.

    This class is meant to be inherited by a class representing a concrete
    inducer type. Functions that save files are implemented as empty
    functions, such that a child class only needs to redefine the necessary
    functions depending on which files it has to save.

    Parameters
    ----------
    name : str
        Name of the inducer, to be used in generated files.
    units : str
        Units in which the inducer's dose is expressed.

    Attributes
    ----------
    name : str
        Name of the inducer.
    units : str
        Units in which the inducer's dose is expressed.
    doses_table : DataFrame
        Table containing information of all the inducer doses.

    Other Attributes
    ----------------
    shuffling_enabled : bool
        Whether shuffling of the doses table is enabled. If False, the
        `shuffle` function will not change the order of the rows in the
        doses table.
    shuffled_idx : list
        Randomized indices that result in the current shuffling of
        doses.
    shuffling_sync_list : list
        List of inducers with which shuffling should be synchronized.

    """
    def __init__(self, name, units):
        # Store name and units
        self.name = name
        self.units = units

        # Initialize dose table
        self._doses_table = pandas.DataFrame()
        # Enable shuffling by default, but start with no shuffling and an
        # empty list of inducers to synchronize shuffling with.
        self.shuffling_enabled = True
        self.shuffled_idx = None
        self.shuffling_sync_list = []

    @property
    def doses_table(self):
        """
        Table containing information of all the inducer concentrations.

        """
        if self.shuffled_idx is None:
            return self._doses_table
        else:
            return self._doses_table.iloc[self.shuffled_idx]

    def shuffle(self):
        """
        Apply random shuffling to the dose table.

        Shuffling can only be applied if ``shuffling_enabled`` is True.

        """
        if self.shuffling_enabled:
            # Create list of indices, shuffle, and store.
            shuffled_idx = list(range(len(self.doses_table)))
            random.shuffle(shuffled_idx)
            self.shuffled_idx = shuffled_idx
            # Write shuffled indices on inducers to synchronize with
            for inducer in self.shuffling_sync_list:
                inducer.shuffled_idx = self.shuffled_idx

    def unshuffle(self):
        """
        Reset dose table to its unshuffled state.

        Unshuffling can only be performed if ``shuffling_enabled`` is True.

        """
        if self.shuffling_enabled:
            self.shuffled_idx = None
            # Reset shuffling on inducers to synchronize with
            for inducer in self.shuffling_sync_list:
                inducer.shuffled_idx = None

    def sync_shuffling(self, inducer):
        """
        Register an inducer to synchronize shuffling with.

        Inducers whose shuffling is synchronized should have the same
        number of doses (i.e. the length of their doses table should be the
        same). Shuffling synchronization is based on the controlling
        inducer being able to directly modify the shuffling indices of the
        controlled inducers. Therefore, this function sets the flag
        ``shuffling_enabled`` in `inducer` to ``False``.

        Parameters
        ----------
        inducer : Inducer
            Inducer to synchronize shuffling with.

        """
        # Check length of doses table
        if len(self.doses_table) != len(inducer.doses_table):
            raise ValueError("inducers to synchronize should have the same "
                "number of doses")
        # Disable shuffling flag
        inducer.shuffling_enabled = False
        # Add to list of inducers to synchronize with
        self.shuffling_sync_list.append(inducer)

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

class ChemicalInducerBase(InducerBase):
    """
    Generic class that represents one or more doses of a chemical inducer.

    This class is meant to be inherited by a class representing a concrete
    chemicalinducer type. Functions that save files are implemented as
    empty functions, such that a child class only needs to redefine the
    necessary functions depending on which files it has to save. Function
    ``set_vol_from_shots()`` raises a ``NotImplementedError``, so a child
    class should redefine it.

    Parameters
    ----------
    name : str
        Name of the inducer, to be used in generated files.
    units : str
        Units in which the inducer's dose is expressed.

    Attributes
    ----------
    name : str
        Name of the inducer.
    units : str
        Units in which the inducer's dose is expressed.
    media_vol : float
        Volume of sample media in which the inducer will be added.
    doses_table : DataFrame
        Table containing information of all the inducer doses.

    Other Attributes
    ----------------
    shuffling_enabled : bool
        Whether shuffling of the doses table is enabled. If False, the
        `shuffle` function will not change the order of the rows in the
        doses table.
    shuffled_idx : list
        Randomized indices that result in the current shuffling of
        doses.
    shuffling_sync_list : list
        List of inducers with which shuffling should be synchronized.

    """
    def __init__(self, name, units):
        # Parent's __init__ stores name, units, initializes doses table, and
        # sets shuffling parameters.
        super(ChemicalInducerBase, self).__init__(name=name, units=units)

        # Initialize media volume
        self.media_vol = None

    def set_vol_from_shots(self,
                           n_shots,
                           n_replicates=1):
        """
        Set volume to prepare from number of shots and replicates.

        """
        raise NotImplementedError

class ChemicalInducer(ChemicalInducerBase):
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
    min_replicate_vol : float
        Minimum volume per replicate to be set when calling
        ``set_vol_from_shots()``.
    min_total_vol : float
        Minimum total volume to be set when calling
        ``set_vol_from_shots()``.
    shuffling_enabled : bool
        Whether shuffling of the doses table is enabled. If False, the
        `shuffle` function will not change the order of the rows in the
        doses table.
    shuffled_idx : list
        Randomized indices that result in the current shuffling of
        doses.
    shuffling_sync_list : list
        List of inducers with which shuffling should be synchronized.

    """
    def __init__(self, name, units, id_prefix=None, id_offset=0):
        # Parent's __init__ stores name, units, initializes doses table, and
        # sets shuffling parameters.
        super(ChemicalInducer, self).__init__(name=name, units=units)

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
        self.min_replicate_vol = 0
        self.min_total_vol = 0

    @property
    def _concentrations_header(self):
        """
        Header to be used in the dose table to specify concentration.

        """
        return u"{} Concentration ({})".format(self.name, self.units)

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
        return self.doses_table[self._concentrations_header].values

    @concentrations.setter
    def concentrations(self, value):
        # Make sure that value is a float array
        value = numpy.array(value, dtype=numpy.float)
        # Initialize dataframe with doses info
        ids = ['{}{:03d}'.format(self.id_prefix, i)
               for i in range(self.id_offset + 1,
                              len(value) + self.id_offset + 1)]
        self._doses_table = pandas.DataFrame({'ID': ids})
        self._doses_table.set_index('ID', inplace=True)
        self._doses_table[self._concentrations_header] = value

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
        else:
            raise ValueError("scale {} not recognized".format(scale))

        # Repeat if necessary
        self.concentrations = numpy.repeat(self.concentrations, n_repeat)

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
        # Compare to minimum and set, if necessary
        inducer_rep_vol = max(inducer_rep_vol, self.min_replicate_vol)

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
        # Compare to minimum total volume and set if necessary
        self.total_vol = max(self.total_vol, self.min_total_vol)

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
        volume of stock dilution indicated in "Inducer volume (µL)" should
        be mixed with a volume of water specified in "Water volume (µL)".

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

        # Check that at least one of the parameters has been specified
        if (file_name is None) and (workbook is None):
            raise ValueError("either file_name or workbook should be specified")

        # Convert concentrations to a set, such that each requested
        # concentration appears once.
        target_concs = self._doses_table[self._concentrations_header].unique()
        target_concs.sort()
        # Get indices of doses for each group with the same concentration
        doses_idx = []
        for c in target_concs:
            doses_idx.append(numpy.where(self.concentrations == c)[0])
        # Get number of doses on each group
        n_doses = numpy.array([len(d) for d in doses_idx])

        # Initialize relevant arrays
        stock_dils = numpy.zeros_like(target_concs)
        inducer_vols = numpy.zeros_like(target_concs)
        water_vols = numpy.zeros_like(target_concs)
        actual_concs = numpy.zeros_like(target_concs)
        total_vols = n_doses*self.total_vol

        # Iterate over concentrations
        for i, target_conc in enumerate(target_concs):
            total_vol = total_vols[i]
            # If concentration is zero, skip
            if target_conc == 0:
                stock_dils[i] = 1
                inducer_vols[i] = 0
                water_vols[i] = total_vol
                continue
            # Determine the appropriate dilution to use
            # We start with a high dilution, and scale down until we reach a
            # volume that is acceptable (lower than max_stock_volume)
            stock_dil = self.stock_dilution_step**10
            while True:
                inducer_vol = (target_conc*self.media_vol/self.shot_vol) * \
                    total_vol / (self.stock_conc/stock_dil)
                # Check if inducer volume is larger than total volume.
                # If so, force another iteration
                if inducer_vol > total_vol:
                    stock_dil = stock_dil/self.stock_dilution_step
                    continue
                # Check end conditions
                if (inducer_vol < self.max_stock_vol):
                    break
                if stock_dil/self.stock_dilution_step < 1:
                    break
                stock_dil = stock_dil/self.stock_dilution_step
            # Round inducer volume to the specified precision
            inducer_vol = numpy.round(inducer_vol,
                                      decimals=self.stock_decimals)
            # Water volume is the remaining volume
            water_vol = numpy.round(total_vol - inducer_vol,
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
        instructions = pandas.DataFrame()
        instructions[self._concentrations_header] = actual_concs
        instructions[u'Stock dilution'] = stock_dils
        instructions[u'Inducer volume (µL)'] = inducer_vols
        instructions[u'Water volume (µL)'] = water_vols
        instructions[u'Total volume (µL)'] = total_vols
        instructions[u'Aliquot IDs'] = [", ".join(self._doses_table.index[idx])
                                        for idx in doses_idx]

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
            # Default sheet name
            sheet_name = self.name

        # Save instructions table
        instructions.to_excel(writer, sheet_name=sheet_name, index=False)
        # Add message about aliquot volume
        if self.replicate_vol is not None:
            aliquot_message = u"Distribute in aliquots of {} µL." \
                .format(self.replicate_vol)
        else:
            aliquot_message = u"Distribute in aliquots of {} µL." \
                .format(self.total_vol)
        worksheet = writer.sheets[sheet_name]
        worksheet.cell(row=len(instructions) + 3,
                       column=1,
                       value=aliquot_message)

        # Save file if necessary
        if workbook is None:
            writer.save()

        # Regenerate doses table based on actual concentrations
        actual_doses = numpy.zeros_like(self.concentrations)
        for idx, conc in zip(doses_idx, actual_concs):
            actual_doses[idx] = conc
        self.concentrations = actual_doses

class ChemicalGeneExpression(ChemicalInducer):
    """
    Object representing gene expression from a chemically-inducible system.

    Expression of the gene of interest is assumed to be controlled by a
    chemical inducer, which will be physically dosed into each sample
    during the replicate setup stage. The relationship between the inducer
    concentration ``x`` and the resulting expression level ``y`` is assumed
    to be given by a Hill Equation of the form::

        y = y0 + dy* (x^n)/(K^n + x^n)

    where ``y0`` is the basal expression in the absence of inducer, ``dy``
    is the expression range that the inducer regulates, ``K`` is the
    inducer amount necessary to drive expression to half of its regulated
    level, and ``n`` is the Hill coefficient.

    Parameters
    ----------
    name : str
        Name of the gene to be expressed, used in generated files.
    units : str
        Units in which the expressed gene is quantified. This is used in
        generated files.
    inducer_name : str
        Name of the inducer, to be used in generated files.
    inducer_units : str
        Units in which the inducer's concentration is expressed. This is
        used in generated files.
    hill_params : dict
        Contains four key:value pairs, with keys ``dy``, ``y0``, ``n``, and
        ``K``. These are the parameters used for calculations converting
        inducer concentrations into gene expression and viceversa.
    id_prefix : str, optional
        Prefix to be used for the ID that identifies each inducer dilution.
        If None, use the first letter of the inducer's name.
    id_offset : int, optional
        Offset from which to generate the ID that identifies each inducer
        dilution. Default: 0 (no offset).

    Attributes
    ----------
    name : str
        Name of the gene to be expressed.
    units : str
        Units in which the expressed gene is quantified.
    inducer_name : str
        Name of the inducer.
    inducer_units : str
        Units in which the inducer's concentration is expressed.
    id_prefix : str
        Prefix to be used for the ID that identifies each inducer
        concentration.
    id_offset : int
        Offset from which to generate the ID that identifies each inducer
        concentration.
    hill_params : dict
        Contains four key:value pairs, with keys ``y0``, ``dy``, ``n``, and
        ``K``. These are the parameters used for calculations converting
        inducer concentrations into gene expression and viceversa.
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
    doses_table : DataFrame
        Table containing information of all the inducer concentrations.

    """
    def __init__(self,
                 name,
                 units,
                 inducer_name,
                 inducer_units,
                 hill_params,
                 id_prefix=None,
                 id_offset=0):
        # Parent's __init__ stores name, units, and id modifiers, initializes
        # doses table, shuffling parameters, and media properties for
        # calculations.
        super(ChemicalGeneExpression, self).__init__(name,
                                                     units,
                                                     id_prefix,
                                                     id_offset)

        # Store inducer names and units
        self.inducer_name = inducer_name
        self.inducer_units = inducer_units

        # Verify hill parameters
        if set(hill_params.keys()) != set(['y0', 'dy', 'K', 'n']):
            raise ValueError('hill_params should be a dictionary with keys '
                '"y0", "dy", "n", and "K"')
        # Set hill parameters
        self.hill_params = hill_params

    def _hill(self, x):
        """
        Convert from an inducer concentration to a gene expression level.

        Parameters
        ----------
        x : float or array
            Concentration value(s) to convert.

        Returns
        -------
        float or array
            Gene expression levels.

        """
        dy = float(self.hill_params['dy'])
        y0 = float(self.hill_params['y0'])
        K = float(self.hill_params['K'])
        n = float(self.hill_params['n'])
        return y0 + dy*(x**n)/(x**n + K**n)

    def _hill_inverse(self, y):
        """
        Convert from a gene expression level to an inducer concentration.

        Parameters
        ----------
        y : float or array
            Gene expression levels to convert.

        Returns
        -------
        float or array
            Inducer concentration.

        """
        dy = float(self.hill_params['dy'])
        y0 = float(self.hill_params['y0'])
        K = float(self.hill_params['K'])
        n = float(self.hill_params['n'])
        # Check that y is between ``y0`` and ``dy + y0``
        if numpy.any(y < y0):
            raise ValueError('expression should be higher than y0 = {}'.\
                format(y0))
        if numpy.any(y > dy + y0):
            raise ValueError('expression should be lower than dy + y0 = {}'.\
                format(dy + y0))
        # Compute inducer concentration
        if hasattr(y, '__iter__'):
            # Initialize array x
            x = numpy.zeros_like(y)
            # Apply inverse hill equation for y values between y0 and y0 + dy
            y_non_limit_ind = numpy.logical_and(y>y0, y<(y0+dy))
            z = (y[y_non_limit_ind] - y0)/dy
            x[y_non_limit_ind] = K*(z/(1.-z))**(1./n)
            # Set limit values to zero or inf
            x[y==y0] = 0.
            x[y==(y0 + dy)] = numpy.inf
        else:
            if y==y0:
                x = 0.
            elif y==(y0 + dy):
                x = numpy.inf
            else:
                z = (y - y0)/dy
                x = K*(z/(1.-z))**(1./n)

        return x

    @property
    def _concentrations_header(self):
        """
        Header to be used in the dose table to specify concentration.

        """
        return u"{} Concentration ({})".format(self.inducer_name,
                                              self.inducer_units)

    @property
    def _expression_levels_header(self):
        """
        Header to be used in the dose table to specify gene expression.

        """
        return u"{} Expression ({})".format(self.name, self.units)

    @property
    def concentrations(self):
        """
        Inducer concentrations.

        Reading from this attribute will return the contents of the
        "Concentration" column from the dose table. Writing to this
        attribute will reinitialize the doses table with the specified
        concentrations. An additional column will be populated with
        matching expression levels. Any columns that are not the
        concentrations, expression levels, or IDs will be lost.

        """
        return self.doses_table[self._concentrations_header].values

    @concentrations.setter
    def concentrations(self, value):
        # Make sure that value is a float array
        value = numpy.array(value, dtype=numpy.float)
        # Initialize dataframe with doses info
        ids = ['{}{:03d}'.format(self.id_prefix, i)
               for i in range(self.id_offset + 1,
                              len(value) + self.id_offset + 1)]
        df = pandas.DataFrame({'ID': ids})
        df.set_index('ID', inplace=True)
        df[self._concentrations_header] = value
        df[self._expression_levels_header] = self._hill(value)
        self._doses_table = df

    @property
    def expression_levels(self):
        """
        Gene expression levels.

        Reading from this attribute will return the contents of the
        "Expression" column from the dose table. Writing to this attribute
        will reinitialize the doses table with the specified gene
        expression levels. An additional column will be populated with
        matching inducer concentrations. Any columns that are not the
        concentrations, expression levels, or IDs will be lost.

        """
        return self.doses_table[self._expression_levels_header].values

    @expression_levels.setter
    def expression_levels(self, value):
        # Make sure that value is a float array
        value = numpy.array(value, dtype=numpy.float)
        # Initialize dataframe with doses info
        ids = ['{}{:03d}'.format(self.id_prefix, i)
               for i in range(self.id_offset + 1,
                              len(value) + self.id_offset + 1)]
        df = pandas.DataFrame({'ID': ids})
        df.set_index('ID', inplace=True)
        df[self._concentrations_header] = self._hill_inverse(value)
        df[self._expression_levels_header] = value
        self._doses_table = df

    def set_gradient(self,
                     n,
                     min=None,
                     max=None,
                     min_inducer=None,
                     max_inducer=None,
                     scale='linear',
                     n_repeat=1):
        """
        Set expression levels from dy specified gradient.

        Using this function will reset the dose table and populate the
        "Expression" column with the specified gradient.

        Parameters
        ----------
        n : int
            Number of points to use for the gradient.
        min : float, optional
            Minimum value on the gradient. Should be between Hill
            parameters ``y0`` and ``dy + y0``. If None, derive from
            `min_inducer` (if specified) or use Hill parameter ``y0``.
        max : float, optional
            Maximum value on the gradient. Should be between Hill
            parameters ``y0`` and ``dy + y0``. If None, derive from
            `max_inducer`. One of these parameters should be specified.
        min_inducer : float, optional
            Inducer concentration corresponding to the minimum expression
            level on the gradient. Ignored if `min` is specified.
        max_inducer : float, optional
            Inducer concentration corresponding to the maximum expression
            level on the gradient. Ignored if `max` is specified.
        scale : {'linear', 'log'}, optional
            Whether to generate the gradient with linear or logarithmic
            spacing.
        n_repeat : int, optional
            How many times to repeat each concentration. Default: 1 (no
            repeat). Should be an exact divisor of ``n``.

        """
        # Check that n_repeat is an exact divisor of n
        if n%n_repeat != 0:
            raise ValueError("n should be a multiple of n_repeat")

        # If not specified, compute min and max expression levels from minimum
        # and maximum inducer concentrations. Otherwise, use ``y0`` for the
        # minimum, or raise an error for the maximum.
        if min is None:
            if min_inducer is not None:
                min = self._hill(min_inducer)
            else:
                min = self.hill_params['y0']
        if max is None:
            if max_inducer is not None:
                max = self._hill(max_inducer)
            else:
                # The maximum expression level is ``dy + y0``. However, this
                # requires infinite inducer. Therefore, raise error.
                raise ValueError('maximum expression or inducer level should be'
                    ' specified')

        # Check limits
        if min < self.hill_params['y0']:
            raise ValueError('min should be greater than y0 = {}'.\
                format(self.hill_params['y0']))
        if max >= self.hill_params['y0'] + self.hill_params['dy']:
            raise ValueError('max should be lower than y0 + dy = {}'.\
                format(self.hill_params['y0'] + self.hill_params['dy']))

        # Calculate gradient
        if scale == 'linear':
            self.expression_levels = numpy.linspace(min, max, n/n_repeat)
        elif scale == 'log':
            self.expression_levels = numpy.logspace(numpy.log10(min),
                                                    numpy.log10(max),
                                                    n/n_repeat)
        else:
            raise ValueError("scale {} not recognized".format(scale))

        # Repeat if necessary
        self.expression_levels = numpy.repeat(self.expression_levels, n_repeat)
