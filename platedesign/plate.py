"""
Module that contains plate classes.

"""

import collections
import copy
import os
import random

import numpy
import openpyxl
import pandas

import platedesign.math

# Create cell styles for the plate area
plate_fill = [openpyxl.styles.PatternFill(fill_type='solid',
                                          start_color='FFDCE6F1',
                                          end_color='FFDCE6F1'),
              openpyxl.styles.PatternFill(fill_type='solid',
                                          start_color='FFB8CCE4',
                                          end_color='FFB8CCE4'),
              ]
plate_alignment = openpyxl.styles.Alignment(wrapText=True,
                                            horizontal='center')
plate_border = openpyxl.styles.Border(
    left=openpyxl.styles.Side(style='thin', color='FF4F81BD'), 
    right=openpyxl.styles.Side(style='thin', color='FF4F81BD'), 
    top=openpyxl.styles.Side(style='thin', color='FF4F81BD'), 
    bottom=openpyxl.styles.Side(style='thin', color='FF4F81BD'))

class PlateBase(object):
    """
    Generic class that represents a plate.

    This class is meant to be inherited by a class representing a concrete
    plate type. Functions that don't save files here raise a
    NotImplementedError to force the child class to implement its own
    version. Functions that save files are implemented as empty functions,
    such that a child class only needs to redefine the necessary functions
    depending on which files it has to save.

    Attributes
    ----------
    name : str
        Name of the inducer.
    samples_table : DataFrame
        Table with information of each sample in the plate.

    Methods
    -------
    start_replicate
        Initialize an empty samples table and inducers dictionary.
    apply_inducer_media_vol
        Get the media volume to which an inducer will be applied.
    apply_inducer_n_shots
        Get number of samples that each inducer dose will be applied to.
    apply_inducer
        Apply an inducer to the plate.
    save_rep_setup_instructions
        Calculate and save instructions for the Replicate Setup stage.

    """
    def __init__(self, name):
        # Store name
        self.name = name

        # Initialize dose table
        self.samples_table = pandas.DataFrame()

    def start_replicate(self):
        """
        Initialize an empty samples table and inducers dictionary.

        """
        raise NotImplementedError

    def apply_inducer_media_vol(self, apply_to):
        """
        Get the media volume to which an inducer will be applied.

        Parameters
        ----------
        apply_to : {'rows', 'cols', 'wells', 'media'}
            "rows" applies the specified inducer to all rows equally.
            "cols" applies to all columns equally. "wells" applies to each
            well individually. 'media' applies inducer to the media at the
            beginning of the replicate setup stage.

        """
        raise NotImplementedError

    def apply_inducer_n_doses(self, apply_to):
        """
        Get number of samples that each inducer dose will be applied to.

        Parameters
        ----------
        apply_to : {'rows', 'cols', 'wells', 'media'}
            "rows" applies the specified inducer to all rows equally.
            "cols" applies to all columns equally. "wells" applies to each
            well individually. 'media' applies inducer to the media at the
            beginning of the replicate setup stage.

        """
        raise NotImplementedError

    def apply_inducer(self, inducer, apply_to='wells'):
        """
        Apply an inducer to the plate.

        This function stores the specified inducer in the `inducers`
        attribute and updates the `samples_table` attribute.

        Parameters
        ----------
        inducer : Inducer object
            The inducer to apply to the plate.
        apply_to : {'rows', 'cols', 'wells', 'media'}
            "rows" applies the specified inducer to all rows equally.
            "cols" applies to all columns equally. "wells" applies to each
            well individually. 'media' applies inducer to the media at the
            beginning of the replicate setup stage.

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
        Save additional files required for the replicate setup stage.

        Parameters
        ----------
        path : str
            Folder in which to save files.

        """
        pass

class Plate(PlateBase):
    """
    Object that represents a plate.

    This class manages inducers that can be applied to individual rows,
    columns, wells, or to all the media in the plate. These are used to
    generate instructions for inducer inoculation during the Replicate
    Setup stage. In addition, a list of samples with the corresponding
    inducer concentrations are generated for the Replicate Measurement
    stage.

    Parameters
    ----------
    name : str
        Name of the plate, to be used in generated files.
    n_rows : int
        Number of rows in the plate, optional.
    n_cols : int
        Number of columns in the plate, optional.
    id_prefix : str, optional
        Prefix to be used for the ID that identifies each sample. Default:
        'S'.
    id_offset : int, optional
        Offset from which to generate the ID that identifies each sample.
        Default: 0 (no offset).

    Attributes
    ----------
    name : str
        Name of the plate, to be used in generated files.
    n_rows : int
        Number of rows in the plate.
    n_cols : int
        Number of columns in the plate.
    id_prefix : str
        Prefix to be used for the ID that identifies each sample.
    id_offset : int
        Offset from which to generate the ID that identifies each sample.
    samples_to_measure : int
        Number of samples to be measured.
    sample_vol : float
        Volume of media per sample (well).
    media_vol : float
        Starting total volume of media, to be added to the plate.
    metadata : OrderedDict
        A column in the samples table will be created for each ``(key,
        value)`` pair in this dictionary. ``key`` will be the name of the
        column, with all rows set to ``value``.
    samples_table : DataFrame
        Table containing information of all samples.

    Methods
    -------
    start_replicate
        Initialize an empty samples table and inducers dictionary.
    apply_inducer_media_vol
        Get the media volume to which an inducer will be applied.
    apply_inducer_n_shots
        Get number of samples that each inducer dose will be applied to.
    apply_inducer
        Apply an inducer to the plate.
    save_rep_setup_instructions
        Calculate and save instructions for the Replicate Setup stage.

    """
    def __init__(self,
                 name,
                 n_rows=4,
                 n_cols=6,
                 id_prefix='S',
                 id_offset=0):
        # Store name
        self.name = name
        # Store dimensions
        self.n_rows = n_rows
        self.n_cols = n_cols
        # Store ID modifiers for samples table
        self.id_prefix = id_prefix
        self.id_offset = id_offset

        # Measure all samples by default
        self.samples_to_measure = n_rows*n_cols
        # Initialize sample and media volumes
        self.sample_vol = None
        self.media_vol = None

        # Initialize metadata dictionary
        self.metadata = collections.OrderedDict()

        # Initialize samples table and inducers dictionary
        self.start_replicate()

    def start_replicate(self):
        """
        Initialize an empty samples table and inducers dictionary.

        """
        # Initialize dataframe with sample IDs
        ids = ['{}{:03d}'.format(self.id_prefix, i)
               for i in range(self.id_offset + 1,
                              self.n_rows*self.n_cols + self.id_offset + 1)]
        self.samples_table = pandas.DataFrame({'ID': ids})
        self.samples_table.set_index('ID', inplace=True)
        # Add metadata
        for k, v in self.metadata.iteritems():
            self.samples_table[k] = v
        # Add plate name
        self.samples_table['Plate'] = self.name
        # Add row and column numbers
        self.samples_table['Row'] = numpy.nan
        self.samples_table['Column'] = numpy.nan
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                self.samples_table.set_value(
                    self.samples_table.index[i*self.n_cols + j],
                    'Row',
                    i + 1)
                self.samples_table.set_value(
                    self.samples_table.index[i*self.n_cols + j],
                    'Column',
                    j + 1)
        # Only preserve table rows that will be measured
        self.samples_table = self.samples_table.iloc[:self.samples_to_measure]
        # Start list of inducers to apply
        self.inducers = {'rows': [], 'cols': [], 'wells': [], 'media': []}

    def apply_inducer_media_vol(self, apply_to):
        """
        Get the media volume to which an inducer will be applied.

        Parameters
        ----------
        apply_to : {'rows', 'cols', 'wells', 'media'}
            "rows" applies the specified inducer to all rows equally.
            "cols" applies to all columns equally. "wells" applies to each
            well individually. 'media' applies inducer to the media at the
            beginning of the replicate setup stage.

        """
        # Check "apply_to" input
        if apply_to not in ['rows', 'cols', 'wells', 'media']:
            raise ValueError('"{}"" not recognized'.format(apply_to))
        # Only "wells" or "media" supported if not measuring full plate
        if (self.samples_to_measure != self.n_cols*self.n_rows) and\
                (apply_to not in ['wells', 'media']):
            raise ValueError('"{}" not possible if not measuring all wells'.\
                format(apply_to))

        # Calculate number of samples to apply
        if apply_to in ['rows', 'cols', 'wells']:
            return self.sample_vol
        elif apply_to=='media':
            return self.media_vol

    def apply_inducer_n_shots(self, apply_to):
        """
        Get number of samples that each inducer dose will be applied to.

        Parameters
        ----------
        apply_to : {'rows', 'cols', 'wells', 'media'}
            "rows" applies the specified inducer to all rows equally.
            "cols" applies to all columns equally. "wells" applies to each
            well individually. 'media' applies inducer to the media at the
            beginning of the replicate setup stage.

        """
        # Check "apply_to" input
        if apply_to not in ['rows', 'cols', 'wells', 'media']:
            raise ValueError('"{}"" not recognized'.format(apply_to))
        # Only "wells" or "media" supported if not measuring full plate
        if (self.samples_to_measure != self.n_cols*self.n_rows) and\
                (apply_to not in ['wells', 'media']):
            raise ValueError('"{}" not possible if not measuring all wells'.\
                format(apply_to))

        # Calculate number of samples to apply
        if apply_to=='rows':
            return self.n_rows
        elif apply_to=='cols':
            return self.n_cols
        elif apply_to=='wells':
            return 1
        elif apply_to=='media':
            return 1

    def apply_inducer(self, inducer, apply_to='wells'):
        """
        Apply an inducer to the plate.

        This function stores the specified inducer in the `inducers`
        attribute and updates the `samples_table` attribute.

        Parameters
        ----------
        inducer : Inducer object
            The inducer to apply to the plate.
        apply_to : {'rows', 'cols', 'wells', 'media'}
            "rows" applies the specified inducer to all rows equally.
            "cols" applies to all columns equally. "wells" applies to each
            well individually. 'media' applies inducer to the media at the
            beginning of the replicate setup stage.

        """
        # Check "apply_to" input
        if apply_to not in ['rows', 'cols', 'wells', 'media']:
            raise ValueError('"{}"" not recognized'.format(apply_to))
        # Only "wells" or "media" supported if not measuring full plate
        if (self.samples_to_measure != self.n_cols*self.n_rows) and\
                (apply_to not in ['wells', 'media']):
            raise ValueError('"{}"" not possible if not measuring all wells'.\
                format(apply_to))

        # Check that the inducer has the appropriate number of samples
        n_wells = self.samples_to_measure
        if (apply_to=='rows' and (len(inducer.doses_table)!=self.n_cols)) or \
           (apply_to=='cols' and (len(inducer.doses_table)!=self.n_rows)) or \
           (apply_to=='wells' and (len(inducer.doses_table)!=n_wells)) or \
           (apply_to=='media' and (len(inducer.doses_table)!=1)):
                raise ValueError('inducer does not have the appropriate' + \
                    ' number of doses')

        # Fill well info
        if apply_to=='rows':
            for column in inducer.doses_table.columns:
                for i in range(self.n_rows):
                    for j in range(self.n_cols):
                        self.samples_table.set_value(
                            self.samples_table.index[i*self.n_cols + j],
                            column,
                            inducer.doses_table.iloc[j][column])
        elif apply_to=='cols':
            for column in inducer.doses_table.columns:
                for i in range(self.n_rows):
                    for j in range(self.n_cols):
                        self.samples_table.set_value(
                            self.samples_table.index[i*self.n_cols + j],
                            column,
                            inducer.doses_table.iloc[i][column])
        elif apply_to=='wells':
            for column in inducer.doses_table.columns:
                self.samples_table[column] = inducer.doses_table[column].values
        elif apply_to=='media':
            for column in inducer.doses_table.columns:
                self.samples_table[column] = inducer.doses_table[column].value

        # Store inducer to apply
        self.inducers[apply_to].append(inducer)

    def save_rep_setup_instructions(self, file_name=None, workbook=None):
        """
        Calculate and save instructions for the Replicate Setup stage.

        Two sheets are generated, named "Inducers for Plate [plate name]"
        and "Cells for Plate [plate name]", with instructions on how to add
        inducers and cells to the plates, respectively.

        Parameters
        ----------
        file_name : str, optional
            Name of the Excel file to save.
        workbook : Workbook, optional
            If not None, `file_name` is ignored, and a sheet with the
            instructions is directly added to workbook `workbook`.

        """
        # Create workbook if not provided
        if workbook is None:
            # Create and remove empty sheet created by default
            workbook = openpyxl.Workbook()
            workbook.remove_sheet(workbook.active)
            save_workbook = True
        else:
            save_workbook = False

        # Add sheets
        self.add_inducer_setup_instructions(
            workbook,
            "Inducers for Plate {}".format(self.name))
        self.add_cell_setup_instructions(
            workbook,
            "Inducers for Plate {}".format(self.name))

        # Save
        if save_workbook:
            workbook.save(filename=file_name)

    def add_inducer_setup_instructions(self, workbook, sheet_name):
        """
        Add sheet with inducer pipetting instructions to specified workbook.

        Parameters
        ----------
        workbook : Workbook
            Workbook where to add sheet.
        sheet_name : str
            Name to give to the new sheet.

        """
        # Skip if no inducers are present
        if not(self.inducers['rows'] or self.inducers['cols'] or \
                self.inducers['wells'] or self.inducers['media']):
            return

        # Check that a sheet with the specified name doesn't exist
        if sheet_name in [ws.title for ws in workbook.worksheets]:
            raise ValueError("sheet \"{}\"already present in workbook".\
                format(sheet_name))

        # Only "wells" or "media" supported if not measuring full plate
        if (self.samples_to_measure != self.n_cols*self.n_rows) and \
                self.inducers['rows']:
            raise ValueError('"rows" not possible for a non-full plate')
        if (self.samples_to_measure != self.n_cols*self.n_rows) and \
                self.inducers['cols']:
            raise ValueError('"cols" not possible for a non-full plate')

        # Initialize inducer instructions table
        ind_layout = []
        ind_layout_rows = self.n_rows + len(self.inducers['rows']) + \
            len(self.inducers['media']) + 1
        ind_layout_cols = self.n_cols + len(self.inducers['cols'])
        for i in range(ind_layout_rows):
            ind_layout.append(['']*(ind_layout_cols))

        # Add well coordinates
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                row = i + len(self.inducers['rows'])
                col = j + len(self.inducers['cols'])
                ind_layout[row][col] += "({}, {})".format(i + 1, j + 1)
        # Add row inducer information
        for i, inducer in enumerate(self.inducers['rows']):
            for j, val in enumerate(inducer.doses_table.index):
                row = i
                col = j + len(self.inducers['cols'])
                ind_layout[row][col] = str(val)
        # Add column inducer information
        for j, inducer in enumerate(self.inducers['cols']):
            for i, val in enumerate(inducer.doses_table.index):
                row = i + len(self.inducers['rows'])
                col = j
                ind_layout[row][col] = str(val)
        # Add individual well inducer information
        for k, inducer in enumerate(self.inducers['wells']):
            for i in range(self.n_rows):
                for j in range(self.n_cols):
                    if (i*self.n_cols + j) >= self.samples_to_measure:
                        break
                    row = i + len(self.inducers['rows'])
                    col = j + len(self.inducers['cols'])
                    ind_layout[row][col] += "\n{}".format(
                        inducer.doses_table.index[i*self.n_cols + j])
        # Add information about inducers added to the media
        for l, inducer in enumerate(self.inducers['media']):
            row = self.n_rows + len(self.inducers['rows']) + 1 + l
            ind_layout[row][0] = "Add {:.2f}uL of {} to media".format(
                inducer.dose_vol, inducer.name)

        # Plate area
        plate_min_row = len(self.inducers['rows'])
        plate_max_row = len(self.inducers['rows']) + self.n_rows
        plate_min_col = len(self.inducers['cols'])
        plate_max_col = len(self.inducers['cols']) + self.n_cols

        # Create and populate worksheet
        worksheet = workbook.create_sheet(title=sheet_name)
        for i in range(len(ind_layout)):
            for j in range(len(ind_layout[i])):
                cell = worksheet.cell(row=i+1, column=j+1)
                # Write value
                cell.value = ind_layout[i][j]
                # Apply styles
                if (i >= plate_min_row) and (i < plate_max_row) and\
                        (j >= plate_min_col) and (j < plate_max_col):
                    cell.fill = plate_fill[0]
                    cell.border = plate_border
                    cell.alignment = plate_alignment

    def add_cell_setup_instructions(self, workbook, sheet_name):
        """
        Add sheet with cell inoculation instructions to specified workbook.

        Parameters
        ----------
        workbook : Workbook
            Workbook where to add sheet.
        sheet_name : str
            Name to give to the new sheet.

        """

        # Check that a sheet with the specified name doesn't exist
        if sheet_name in [ws.title for ws in workbook.worksheets]:
            raise ValueError("sheet \"{}\"already present in workbook".\
                format(sheet_name))
        pass

class PlateArray(Plate):
    """
    """
    pass
    def __init__(self,
                 name,
                 array_n_rows,
                 array_n_cols,
                 plate_names,
                 plate_n_rows=4,
                 plate_n_cols=6,
                 id_prefix='S',
                 id_offset=0):
        # Store name
        self.name = name
        # Store dimensions
        self.array_n_rows = array_n_rows
        self.array_n_cols = array_n_cols
        self.plate_n_rows = plate_n_rows
        self.plate_n_cols = plate_n_cols
        # Verify that we have the appropriate amount of plate names, and store
        if len(plate_names) != array_n_rows*array_n_cols:
            raise ValueError("plate_names should have {} elements".format(
                array_n_rows*array_n_cols))
        self.plate_names = plate_names
        # Mea
        # Store ID modifiers for samples table
        self.id_prefix = id_prefix
        self.id_offset = id_offset

        # Measure all samples by default
        self.samples_to_measure = self.n_rows*self.n_cols
        # Initialize sample and media volumes
        self.sample_vol = None
        self.media_vol = None

        # Initialize metadata dictionary
        self.metadata = collections.OrderedDict()

        # Initialize samples table and inducers dictionary
        self.start_replicate()

    @property
    def n_rows(self):
        return self.array_n_rows*self.plate_n_rows

    @property
    def n_cols(self):
        return self.array_n_cols*self.plate_n_cols

    def start_replicate(self):
        """
        Initialize an empty samples table and inducers dictionary.

        """
        # Initialize dataframe with sample IDs
        ids = ['{}{:03d}'.format(self.id_prefix, i)
               for i in range(self.id_offset + 1,
                              self.n_rows*self.n_cols + self.id_offset + 1)]
        self.samples_table = pandas.DataFrame({'ID': ids})
        self.samples_table.set_index('ID', inplace=True)
        # Add metadata
        for k, v in self.metadata.iteritems():
            self.samples_table[k] = v
        # Add plate array name
        self.samples_table["Plate Array"] = self.name
        # Add plate name, and row and column numbers
        self.samples_table['Plate'] = ''
        self.samples_table['Row'] = numpy.nan
        self.samples_table['Column'] = numpy.nan
        samples_table_idx = 0
        for i in range(self.array_n_rows):
            for j in range(self.array_n_cols):
                for k in range(self.plate_n_rows):
                    for l in range(self.plate_n_cols):
                        self.samples_table.set_value(
                            self.samples_table.index[samples_table_idx],
                            'Plate',
                            self.plate_names[i*self.array_n_cols + j])
                        self.samples_table.set_value(
                            self.samples_table.index[samples_table_idx],
                            'Row',
                            k + 1)
                        self.samples_table.set_value(
                            self.samples_table.index[samples_table_idx],
                            'Column',
                            l + 1)
                        samples_table_idx += 1
        # Only preserve table rows that will be measured
        self.samples_table = self.samples_table.iloc[:self.samples_to_measure]
        # Start list of inducers to apply
        self.inducers = {'rows': [], 'cols': [], 'wells': [], 'media': []}

    def save_rep_setup_instructions(self, file_name=None, workbook=None):
        """
        Calculate and save instructions for the Replicate Setup stage.

        Two sheets are generated, named "Inducers for Plate Array [plate
        array name]" and "Cells for Plate Array [plate array name]", with
        instructions on how to add inducers and cells to the plates,
        respectively.

        Parameters
        ----------
        file_name : str, optional
            Name of the Excel file to save.
        workbook : Workbook, optional
            If not None, `file_name` is ignored, and a sheet with the
            instructions is directly added to workbook `workbook`.

        """
        # Create workbook if not provided
        if workbook is None:
            # Create and remove empty sheet created by default
            workbook = openpyxl.Workbook()
            workbook.remove_sheet(workbook.active)
            save_workbook = True
        else:
            save_workbook = False

        # Add sheets
        self.add_inducer_setup_instructions(
            workbook,
            "Inducers for Plate Array {}".format(self.name))
        self.add_cell_setup_instructions(
            workbook,
            "Inducers for Plate Array {}".format(self.name))

        # Save
        if save_workbook:
            workbook.save(filename=file_name)

    def add_inducer_setup_instructions(self, workbook, sheet_name):
        """
        Add sheet with inducer pipetting instructions to specified workbook.

        Parameters
        ----------
        workbook : Workbook
            Workbook where to add sheet.
        sheet_name : str
            Name to give to the new sheet.

        """
        # Skip if no inducers are present
        if not(self.inducers['rows'] or self.inducers['cols'] or \
                self.inducers['wells'] or self.inducers['media']):
            return

        # Check that a sheet with the specified name doesn't exist
        if sheet_name in [ws.title for ws in workbook.worksheets]:
            raise ValueError("sheet \"{}\"already present in workbook".\
                format(sheet_name))

        # Only "wells" or "media" supported if not measuring full plate
        if (self.samples_to_measure != self.n_cols*self.n_rows) and \
                self.inducers['rows']:
            raise ValueError('"rows" not possible for a non-full plate')
        if (self.samples_to_measure != self.n_cols*self.n_rows) and \
                self.inducers['cols']:
            raise ValueError('"cols" not possible for a non-full plate')

        # Initialize inducer instructions table
        ind_layout = []
        ind_layout_rows = self.n_rows + len(self.inducers['rows']) + \
            len(self.inducers['media']) + 1
        ind_layout_cols = self.n_cols + len(self.inducers['cols'])
        for i in range(ind_layout_rows):
            ind_layout.append(['']*(ind_layout_cols))

        # Add well coordinates
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                array_i = i/(self.plate_n_rows)
                array_j = j/(self.plate_n_cols)
                plate_i = i%(self.plate_n_rows)
                plate_j = j%(self.plate_n_cols)
                row = i + len(self.inducers['rows'])
                col = j + len(self.inducers['cols'])
                ind_layout[row][col] += "{} ({}, {})".format(
                    self.plate_names[array_i*self.array_n_cols + array_j],
                    plate_i + 1,
                    plate_j + 1)
        # Add row inducer information
        for i, inducer in enumerate(self.inducers['rows']):
            for j, val in enumerate(inducer.doses_table.index):
                row = i
                col = j + len(self.inducers['cols'])
                ind_layout[row][col] = str(val)
        # Add column inducer information
        for j, inducer in enumerate(self.inducers['cols']):
            for i, val in enumerate(inducer.doses_table.index):
                row = i + len(self.inducers['rows'])
                col = j
                ind_layout[row][col] = str(val)
        # Add individual well inducer information
        for k, inducer in enumerate(self.inducers['wells']):
            for i in range(self.n_rows):
                for j in range(self.n_cols):
                    if (i*self.n_cols + j) >= self.samples_to_measure:
                        break
                    row = i + len(self.inducers['rows'])
                    col = j + len(self.inducers['cols'])
                    ind_layout[row][col] += "\n{}".format(
                        inducer.doses_table.index[i*self.n_cols + j])
        # Add information about inducers added to the media
        for l, inducer in enumerate(self.inducers['media']):
            row = self.n_rows + len(self.inducers['rows']) + 1 + l
            ind_layout[row][0] = "Add {:.2f}uL of {} to media".format(
                inducer.dose_vol, inducer.name)

        # Plate area
        plate_min_row = len(self.inducers['rows'])
        plate_max_row = len(self.inducers['rows']) + self.n_rows
        plate_min_col = len(self.inducers['cols'])
        plate_max_col = len(self.inducers['cols']) + self.n_cols

        # Create and populate worksheet
        worksheet = workbook.create_sheet(title=sheet_name)
        for i in range(len(ind_layout)):
            for j in range(len(ind_layout[i])):
                cell = worksheet.cell(row=i+1, column=j+1)
                # Write value
                cell.value = ind_layout[i][j]
                # Apply styles
                if (i >= plate_min_row) and (i < plate_max_row) and\
                        (j >= plate_min_col) and (j < plate_max_col):
                    array_i = (i - plate_min_row) / self.plate_n_rows
                    array_j = (j - plate_min_col) / self.plate_n_cols
                    cell.fill = plate_fill[(array_i + array_j)%2]
                    cell.border = plate_border
                    cell.alignment = plate_alignment
