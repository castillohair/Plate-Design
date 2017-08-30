# -*- coding: UTF-8 -*-
"""
Module that contains plate classes.

"""

import collections

import numpy
import openpyxl
import pandas

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
header_alignment = openpyxl.styles.Alignment(wrapText=True,
                                            horizontal='center')
header_font = openpyxl.styles.Font(bold=True, color="FF1F497D")

class Plate(object):
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
    n_rows, n_cols : int, optional
        Number of rows and columns in the plate.
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
    n_rows, n_cols : int
        Number of rows and columns in the plate.
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
    cell_strain_name : str
        Name of the cell strain to be inoculated in this plate.
    cell_setup_method : {None, 'fixed_volume', 'fixed_od600'}
        Method used to determine how much volume of cells to inoculate.
    cell_predilution : float
        Dilution factor for the cell preculture before inoculating.
    cell_predilution_vol : float
        Volume of diluted preculture to make in µL.
    cell_initial_od600 : float
        Target initial OD600 for inoculating cells. Only used if
        `cell_setup_method` is "fixed_od600".
    cell_shot_vol : float
        Volume of diluted preculture to inoculate in media. Only used if
        `cell_setup_method` is "fixed_volume".
    metadata : OrderedDict
        A column in the samples table will be created for each ``(key,
        value)`` pair in this dictionary. ``key`` will be the name of the
        column, with all rows set to ``value``.
    inducers : OrderedDict
        Keys in this dictionary represent how each inducer is applied
        ("rows", "cols", "wells", "media"), and the values are lists of
        inducers to be applied as specified by the key.
    samples_table : DataFrame
        Table containing information of all samples.

    Methods
    -------
    apply_inducer_media_vol
        Get the media volume to which an inducer will be applied.
    apply_inducer_n_shots
        Get number of samples that each inducer dose will be applied to.
    apply_inducer
        Apply an inducer to the plate.
    save_exp_setup_instructions
        Calculate and save instructions for the Experiment Setup stage.
    save_exp_setup_files
        Save additional files required for the Experiment Setup stage.
    save_rep_setup_instructions
        Calculate and save instructions for the Replicate Setup stage.
    add_inducer_setup_instructions
        Add sheet with inducer pipetting instructions to specified workbook.
    add_cell_setup_instructions
        Add sheet with cell inoculation instructions to specified workbook.
    save_rep_setup_files
        Save additional files required for the Replicate Setup stage.
    update_samples_table
        Update samples table.

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

        # Initialize parameters for cell setup
        self.cell_strain_name = None
        self.cell_setup_method = None
        self.cell_predilution = 1
        self.cell_predilution_vol = None
        self.cell_initial_od600 = None
        self.cell_shot_vol = None

        # Initialize metadata dictionary
        self.metadata = collections.OrderedDict()

        # Initialize list of inducers
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
        attribute, after verifying consistency.

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

        # Check that the inducer is not repeated
        if inducer in self.inducers[apply_to]:
            raise ValueError("inducer already in plate's inducer list")

        # Store inducer
        self.inducers[apply_to].append(inducer)

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
        Save additional files required for the Experiment Setup stage.

        Parameters
        ----------
        path : str
            Folder in which to save files.

        """
        pass

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
            "Cells for Plate {}".format(self.name))

        # Save
        if save_workbook:
            workbook.save(filename=file_name)

    def add_inducer_setup_instructions(self, workbook, sheet_name):
        """
        Add sheet with inducer pipetting instructions to specified workbook.

        Only add instructions for an inducer if it has the attribute
        ``shot_vol``.

        Parameters
        ----------
        workbook : Workbook
            Workbook where to add sheet.
        sheet_name : str
            Name to give to the new sheet.

        """
        # Get only inducers that have ``shot_vol``
        inducers_rows = [ind
                         for ind in self.inducers['rows']
                         if hasattr(ind, 'shot_vol')]
        inducers_cols = [ind
                         for ind in self.inducers['cols']
                         if hasattr(ind, 'shot_vol')]
        inducers_wells = [ind
                          for ind in self.inducers['wells']
                          if hasattr(ind, 'shot_vol')]
        inducers_media = [ind
                          for ind in self.inducers['media']
                          if hasattr(ind, 'shot_vol')]

        # Skip if no inducers are present
        if not(inducers_rows or inducers_cols or \
                inducers_wells or inducers_media):
            return

        # Check that a sheet with the specified name doesn't exist
        if sheet_name in [ws.title for ws in workbook.worksheets]:
            raise ValueError("sheet \"{}\"already present in workbook".\
                format(sheet_name))

        # Only "wells" or "media" supported if not measuring full plate
        if (self.samples_to_measure != self.n_cols*self.n_rows) and \
                inducers_rows:
            raise ValueError('"rows" not possible for a non-full plate')
        if (self.samples_to_measure != self.n_cols*self.n_rows) and \
                inducers_cols:
            raise ValueError('"cols" not possible for a non-full plate')

        # Initialize inducer instructions table
        ind_layout = []
        ind_layout_rows = self.n_rows + len(inducers_rows) + \
            len(inducers_media) + 1
        ind_layout_cols = self.n_cols + len(inducers_cols)
        for i in range(ind_layout_rows):
            ind_layout.append(['']*(ind_layout_cols))

        # Add well coordinates
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                row = i + len(inducers_rows)
                col = j + len(inducers_cols)
                ind_layout[row][col] += "({}, {})".format(i + 1, j + 1)
        # Add row inducer information
        for i, inducer in enumerate(inducers_rows):
            for j, val in enumerate(inducer.doses_table.index):
                row = i
                col = j + len(inducers_cols)
                ind_layout[row][col] = str(val)
        # Add column inducer information
        for j, inducer in enumerate(inducers_cols):
            for i, val in enumerate(inducer.doses_table.index):
                row = i + len(inducers_rows)
                col = j
                ind_layout[row][col] = str(val)
        # Add individual well inducer information
        for k, inducer in enumerate(inducers_wells):
            for i in range(self.n_rows):
                for j in range(self.n_cols):
                    if (i*self.n_cols + j) >= self.samples_to_measure:
                        break
                    row = i + len(inducers_rows)
                    col = j + len(inducers_cols)
                    ind_layout[row][col] += "\n{}".format(
                        inducer.doses_table.index[i*self.n_cols + j])
        # Add information about inducers added to the media
        for l, inducer in enumerate(inducers_media):
            row = self.n_rows + len(inducers_rows) + 1 + l
            ind_layout[row][0] = "Add {:.2f}µL of {} to media".format(
                inducer.shot_vol, inducer.name)

        # Plate area
        plate_min_row = len(inducers_rows)
        plate_max_row = len(inducers_rows) + self.n_rows
        plate_min_col = len(inducers_cols)
        plate_max_col = len(inducers_cols) + self.n_cols

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

        # Do nothing if cell starting method has not been defined.
        if self.cell_setup_method is None:
            return

        # Create sheet
        worksheet = workbook.create_sheet(title=sheet_name)
        # Add setup instructions
        if self.cell_setup_method=='fixed_od600':
            # Set width
            worksheet.column_dimensions['A'].width = 22
            worksheet.column_dimensions['B'].width = 7
            worksheet.column_dimensions['C'].width = 5
            # Info about strain
            worksheet.cell(row=1, column=1).value = "Strain Name"
            worksheet.cell(row=1, column=2).value = self.cell_strain_name
            if self.cell_predilution != 1:
                # Instructions for making predilution
                worksheet.cell(row=2, column=1).value = "Predilution"
                worksheet.cell(row=2, column=1).alignment = header_alignment
                worksheet.cell(row=2, column=1).font = header_font
                worksheet.merge_cells(start_row=2,
                                      end_row=2,
                                      start_column=1,
                                      end_column=3)

                worksheet.cell(row=3, column=1).value = "Predilution factor"
                worksheet.cell(row=3, column=2).value = self.cell_predilution
                worksheet.cell(row=3, column=3).value = "x"

                media_vol = self.cell_predilution_vol / \
                    float(self.cell_predilution)
                worksheet.cell(row=4, column=1).value = "Media volume"
                worksheet.cell(row=4, column=2).value = media_vol
                worksheet.cell(row=4, column=3).value = "µL"

                cell_vol = self.cell_predilution_vol - media_vol
                worksheet.cell(row=5, column=1).value = "Preculture volume"
                worksheet.cell(row=5, column=2).value = cell_vol
                worksheet.cell(row=5, column=3).value = "µL"

                worksheet.cell(row=6, column=1).value = "Predilution OD600"
                worksheet.cell(row=6, column=2).fill = plate_fill[0]

                # Instructions for inoculating into plate media
                worksheet.cell(row=7, column=1).value = "Inoculation"
                worksheet.cell(row=7, column=1).alignment = header_alignment
                worksheet.cell(row=7, column=1).font = header_font
                worksheet.merge_cells(start_row=7,
                                      end_row=7,
                                      start_column=1,
                                      end_column=3)

                worksheet.cell(row=8, column=1).value = "Target OD600"
                worksheet.cell(row=8, column=2).value = self.cell_initial_od600

                worksheet.cell(row=9, column=1).value = "Predilution volume"
                worksheet.cell(row=9, column=2).value = "={}/B6".format(
                    self.media_vol*self.cell_initial_od600)
                worksheet.cell(row=9, column=3).value = "µL"

                worksheet.cell(row=10, column=1).value = \
                    "Add into {:.0f}mL media, ".format(self.media_vol/1000.) + \
                    "and distribute into plate wells."
            else:
                worksheet.cell(row=2, column=1).value = "Preculture OD600"
                worksheet.cell(row=2, column=2).fill = plate_fill[0]

                worksheet.cell(row=3, column=1).value = "Target OD600"
                worksheet.cell(row=3, column=2).value = self.cell_initial_od600

                worksheet.cell(row=4, column=1).value = "Predilution volume"
                worksheet.cell(row=4, column=2).value = "={}/B2".format(
                    self.media_vol*self.cell_initial_od600)
                worksheet.cell(row=4, column=3).value = "µL"

                worksheet.cell(row=5, column=1).value = \
                    "Add into {:.0f}mL media, ".format(self.media_vol/1000.) + \
                    "and distribute into plate wells."

        elif self.cell_setup_method=='fixed_volume':
            # Set width
            worksheet.column_dimensions['A'].width = 22
            worksheet.column_dimensions['B'].width = 7
            worksheet.column_dimensions['C'].width = 5
            # Info about strain
            worksheet.cell(row=1, column=1).value = "Strain Name"
            worksheet.cell(row=1, column=2).value = self.cell_strain_name
            if self.cell_predilution != 1:
                # Instructions for making predilution
                worksheet.cell(row=2, column=1).value = "Predilution"
                worksheet.cell(row=2, column=1).alignment = header_alignment
                worksheet.cell(row=2, column=1).font = header_font
                worksheet.merge_cells(start_row=2,
                                      end_row=2,
                                      start_column=1,
                                      end_column=3)

                worksheet.cell(row=3, column=1).value = "Predilution factor"
                worksheet.cell(row=3, column=2).value = self.cell_predilution
                worksheet.cell(row=3, column=3).value = "x"

                media_vol = self.cell_predilution_vol / \
                    float(self.cell_predilution)
                worksheet.cell(row=4, column=1).value = "Media volume"
                worksheet.cell(row=4, column=2).value = media_vol
                worksheet.cell(row=4, column=3).value = "µL"

                cell_vol = self.cell_predilution_vol - media_vol
                worksheet.cell(row=5, column=1).value = "Preculture volume"
                worksheet.cell(row=5, column=2).value = cell_vol
                worksheet.cell(row=5, column=3).value = "µL"

                # Instructions for inoculating into plate media
                worksheet.cell(row=6, column=1).value = "Inoculation"
                worksheet.cell(row=6, column=1).alignment = header_alignment
                worksheet.cell(row=6, column=1).font = header_font
                worksheet.merge_cells(start_row=6,
                                      end_row=6,
                                      start_column=1,
                                      end_column=3)

                worksheet.cell(row=7, column=1).value = "Predilution volume"
                worksheet.cell(row=7, column=2).value = self.cell_shot_vol
                worksheet.cell(row=7, column=3).value = "µL"

                worksheet.cell(row=8, column=1).value = \
                    "Add into {:.0f}mL media, ".format(self.media_vol/1000.) + \
                    "and distribute into plate wells."
            else:
                # Instructions for inoculating into plate media
                worksheet.cell(row=2, column=1).value = "Preculture volume"
                worksheet.cell(row=2, column=2).value = self.cell_shot_vol
                worksheet.cell(row=2, column=3).value = "µL"

                worksheet.cell(row=3, column=1).value = \
                    "Add into {:.0f}mL media, ".format(self.media_vol/1000.) + \
                    "and distribute into plate wells."
        else:
            raise ValueError("cell setup method {} not recognized".format(
                self.cell_setup_method))

    def save_rep_setup_files(self, path='.'):
        """
        Save additional files required for the Replicate Setup stage.

        Parameters
        ----------
        path : str
            Folder in which to save files.

        """
        pass

    def close_plates(self):
        """
        Create ClosedPlate objects and fill their table of samples

        """
        # Initialize samples table as a dataframe
        ids = ['{}{:03d}'.format(self.id_prefix, i)
               for i in range(self.id_offset + 1,
                              self.n_rows*self.n_cols + self.id_offset + 1)]
        samples_table = pandas.DataFrame({'ID': ids})
        samples_table.set_index('ID', inplace=True)

        # Add plate metadata
        # The following try-catch block is needed to ensure compatibility with
        # both python2 and python3.
        try:
            items = self.metadata.iteritems()
        except AttributeError:
            items = self.metadata.items()
        for k, v in items:
            samples_table[k] = v

        # Add plate name, row and column number for each sample
        samples_table['Plate'] = self.name
        # Add row and column numbers
        samples_table['Row'] = numpy.nan
        samples_table['Column'] = numpy.nan
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                samples_table.set_value(
                    samples_table.index[i*self.n_cols + j],
                    'Row',
                    i + 1)
                samples_table.set_value(
                    samples_table.index[i*self.n_cols + j],
                    'Column',
                    j + 1)
        # Only preserve table rows that will be measured
        samples_table = samples_table.iloc[:self.samples_to_measure]

        # Add cell info
        samples_table['Strain'] = self.cell_strain_name
        if self.cell_setup_method=='fixed_od600':
            samples_table['Cell Predilution'] = self.cell_predilution
            samples_table['Initial OD600'] = self.cell_initial_od600
        elif self.cell_setup_method=='fixed_volume':
            samples_table['Cell Predilution'] = self.cell_predilution
            samples_table['Cell Inoculated Vol.'] = self.cell_shot_vol

        # Add inducer info
        # The following try-catch block is needed to ensure compatibility with
        # both python2 and python3.
        try:
            items = self.inducers.iteritems()
        except AttributeError:
            items = self.inducers.items()
        for apply_to, inducers in items:
            for inducer in inducers:
                if apply_to=='rows':
                    for column in inducer.doses_table.columns:
                        for i in range(self.n_rows):
                            for j in range(self.n_cols):
                                samples_table.set_value(
                                    samples_table.index[i*self.n_cols + j],
                                    column,
                                    inducer.doses_table.iloc[j][column])
                elif apply_to=='cols':
                    for column in inducer.doses_table.columns:
                        for i in range(self.n_rows):
                            for j in range(self.n_cols):
                                samples_table.set_value(
                                    samples_table.index[i*self.n_cols + j],
                                    column,
                                    inducer.doses_table.iloc[i][column])
                elif apply_to=='wells':
                    for column in inducer.doses_table.columns:
                        samples_table[column] = \
                            inducer.doses_table[column].values
                elif apply_to=='media':
                    for column in inducer.doses_table.columns:
                        samples_table[column] = \
                            inducer.doses_table[column].value

        # Create closed plate object
        closed_plate = ClosedPlate(id_prefix = self.id_prefix,
                                   id_offset = self.id_offset,
                                   samples_table = samples_table)
        closed_plates = [closed_plate]

        return closed_plates

class PlateArray(Plate):
    """
    Object that represents an array of plates.

    This class manages inducers that can be applied to individual rows,
    columns, wells, or to all the media in the array. These are used to
    generate instructions for inducer inoculation during the Replicate
    Setup stage. In addition, a list of samples with the corresponding
    inducer concentrations are generated for the Replicate Measurement
    stage.

    Parameters
    ----------
    name : str
        Name of the plate array, to be used in generated files.
    array_n_rows, array_n_cols : int
        Number of rows and columns in the plate array.
    plate_names : list
        Names of the plates, to be used in generated files.
    plate_n_rows, plate_n_cols : int, optional
        Number of rows and columns in each plate.
    id_prefix : str, optional
        Prefix to be used for the ID that identifies each sample. Default:
        'S'.
    id_offset : int, optional
        Offset from which to generate the ID that identifies each sample.
        Default: 0 (no offset).

    Attributes
    ----------
    name : str
        Name of the plate array, to be used in generated files.
    array_n_rows, array_n_cols : int
        Number of rows and columns in the plate array.
    plate_names : list
        Names of the plates, to be used in generated files.
    plate_n_rows, plate_n_cols : int
        Number of rows and columns in each plate.        
    n_rows, n_cols : int
        Total number of rows and columns in the plate array.
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
    cell_strain_name : str
        Name of the cell strain to be inoculated in this plate.
    cell_setup_method : {None, 'fixed_volume', 'fixed_od600'}
        Method used to determine how much volume of cells to inoculate.
    cell_predilution : float
        Dilution factor for the cell preculture before inoculating.
    cell_predilution_vol : float
        Volume of diluted preculture to make in µL.
    cell_initial_od600 : float
        Target initial OD600 for inoculating cells. Only used if
        `cell_setup_method` is "fixed_od600".
    cell_shot_vol : float
        Volume of diluted preculture to inoculate in media. Only used if
        `cell_setup_method` is "fixed_volume".
    metadata : OrderedDict
        A column in the samples table will be created for each ``(key,
        value)`` pair in this dictionary. ``key`` will be the name of the
        column, with all rows set to ``value``.
    samples_table : DataFrame
        Table containing information of all samples.
    inducers : OrderedDict
        Keys in this dictionary represent how each inducer is applied
        ("rows", "cols", "wells", "media"), and the values are lists of
        inducers to be applied as specified by the key.

    Methods
    -------
    apply_inducer_media_vol
        Get the media volume to which an inducer will be applied.
    apply_inducer_n_shots
        Get number of samples that each inducer dose will be applied to.
    apply_inducer
        Apply an inducer to the plate.
    save_rep_setup_instructions
        Calculate and save instructions for the Replicate Setup stage.
    add_inducer_setup_instructions
        Add sheet with inducer pipetting instructions to specified workbook.
    add_cell_setup_instructions
        Add sheet with cell inoculation instructions to specified workbook.
    update_samples_table
        Update samples table.

    """
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

        # Initialize parameters for cell setup
        self.cell_strain_name = None
        self.cell_setup_method = None
        self.cell_predilution = 1
        self.cell_predilution_vol = None
        self.cell_initial_od600 = None
        self.cell_shot_vol = None

        # Initialize metadata dictionary
        self.metadata = collections.OrderedDict()

        # Initialize list of inducers
        self.inducers = {'rows': [], 'cols': [], 'wells': [], 'media': []}

    @property
    def n_rows(self):
        """
        Total number of rows in the plate array.

        """
        return self.array_n_rows*self.plate_n_rows

    @property
    def n_cols(self):
        """
        Total number of columns in the plate array.
        
        """
        return self.array_n_cols*self.plate_n_cols

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
            "Cells for Plate Array {}".format(self.name))

        # Save
        if save_workbook:
            workbook.save(filename=file_name)

    def add_inducer_setup_instructions(self, workbook, sheet_name):
        """
        Add sheet with inducer pipetting instructions to specified workbook.

        Only add instructions for an inducer if it has the attribute
        ``shot_vol``.

        Parameters
        ----------
        workbook : Workbook
            Workbook where to add sheet.
        sheet_name : str
            Name to give to the new sheet.

        """
        # Get only inducers that have ``shot_vol``
        inducers_rows = [ind
                         for ind in self.inducers['rows']
                         if hasattr(ind, 'shot_vol')]
        inducers_cols = [ind
                         for ind in self.inducers['cols']
                         if hasattr(ind, 'shot_vol')]
        inducers_wells = [ind
                          for ind in self.inducers['wells']
                          if hasattr(ind, 'shot_vol')]
        inducers_media = [ind
                          for ind in self.inducers['media']
                          if hasattr(ind, 'shot_vol')]

        # Skip if no inducers are present
        if not(inducers_rows or inducers_cols or \
                inducers_wells or inducers_media):
            return

        # Check that a sheet with the specified name doesn't exist
        if sheet_name in [ws.title for ws in workbook.worksheets]:
            raise ValueError("sheet \"{}\"already present in workbook".\
                format(sheet_name))

        # Only "wells" or "media" supported if not measuring full plate
        if (self.samples_to_measure != self.n_cols*self.n_rows) and \
                inducers_rows:
            raise ValueError('"rows" not possible for a non-full plate')
        if (self.samples_to_measure != self.n_cols*self.n_rows) and \
                inducers_cols:
            raise ValueError('"cols" not possible for a non-full plate')

        # Initialize inducer instructions table
        ind_layout = []
        ind_layout_rows = self.n_rows + len(inducers_rows) + \
            len(inducers_media) + 1
        ind_layout_cols = self.n_cols + len(inducers_cols)
        for i in range(ind_layout_rows):
            ind_layout.append(['']*(ind_layout_cols))

        # Add well coordinates
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                array_i = i/(self.plate_n_rows)
                array_j = j/(self.plate_n_cols)
                plate_i = i%(self.plate_n_rows)
                plate_j = j%(self.plate_n_cols)
                row = i + len(inducers_rows)
                col = j + len(inducers_cols)
                ind_layout[row][col] += "{} ({}, {})".format(
                    self.plate_names[array_i*self.array_n_cols + array_j],
                    plate_i + 1,
                    plate_j + 1)
        # Add row inducer information
        for i, inducer in enumerate(inducers_rows):
            for j, val in enumerate(inducer.doses_table.index):
                row = i
                col = j + len(inducers_cols)
                ind_layout[row][col] = str(val)
        # Add column inducer information
        for j, inducer in enumerate(inducers_cols):
            for i, val in enumerate(inducer.doses_table.index):
                row = i + len(inducers_rows)
                col = j
                ind_layout[row][col] = str(val)
        # Add individual well inducer information
        for k, inducer in enumerate(inducers_wells):
            for i in range(self.n_rows):
                for j in range(self.n_cols):
                    if (i*self.n_cols + j) >= self.samples_to_measure:
                        break
                    row = i + len(inducers_rows)
                    col = j + len(inducers_cols)
                    ind_layout[row][col] += "\n{}".format(
                        inducer.doses_table.index[i*self.n_cols + j])
        # Add information about inducers added to the media
        for l, inducer in enumerate(inducers_media):
            row = self.n_rows + len(inducers_rows) + 1 + l
            ind_layout[row][0] = "Add {:.2f}µL of {} to media".format(
                inducer.shot_vol, inducer.name)

        # Plate area
        plate_min_row = len(inducers_rows)
        plate_max_row = len(inducers_rows) + self.n_rows
        plate_min_col = len(inducers_cols)
        plate_max_col = len(inducers_cols) + self.n_cols

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

    def close_plates(self):
        """
        Create ClosedPlate objects and fill their table of samples

        """
        # Initialize dataframe with sample IDs
        ids = ['{}{:03d}'.format(self.id_prefix, i)
               for i in range(self.id_offset + 1,
                              self.n_rows*self.n_cols + self.id_offset + 1)]
        samples_table = pandas.DataFrame({'ID': ids})
        samples_table.set_index('ID', inplace=True)
        # Add metadata
        # The following try-catch block is needed to ensure compatibility with
        # both python2 and python3.
        try:
            items = self.metadata.iteritems()
        except AttributeError:
            items = self.metadata.items()
        for k, v in items:
            samples_table[k] = v
        # Add plate array name
        samples_table["Plate Array"] = self.name
        # Add plate name, and row and column numbers
        samples_table['Plate'] = ''
        samples_table['Row'] = numpy.nan
        samples_table['Column'] = numpy.nan
        samples_table_idx = 0
        for i in range(self.array_n_rows):
            for j in range(self.array_n_cols):
                for k in range(self.plate_n_rows):
                    for l in range(self.plate_n_cols):
                        samples_table.set_value(
                            samples_table.index[samples_table_idx],
                            'Plate',
                            self.plate_names[i*self.array_n_cols + j])
                        samples_table.set_value(
                            samples_table.index[samples_table_idx],
                            'Row',
                            k + 1)
                        samples_table.set_value(
                            samples_table.index[samples_table_idx],
                            'Column',
                            l + 1)
                        samples_table_idx += 1
        # Only preserve table rows that will be measured
        samples_table = samples_table.iloc[:self.samples_to_measure]

        # Add cell info
        samples_table['Strain'] = self.cell_strain_name
        if self.cell_setup_method=='fixed_od600':
            samples_table['Cell Predilution'] = self.cell_predilution
            samples_table['Initial OD600'] = self.cell_initial_od600
        elif self.cell_setup_method=='fixed_volume':
            samples_table['Cell Predilution'] = self.cell_predilution
            samples_table['Cell Inoculated Vol.'] = self.cell_shot_vol

        # Add inducer info
        # The following try-catch block is needed to ensure compatibility with
        # both python2 and python3.
        try:
            items = self.inducers.iteritems()
        except AttributeError:
            items = self.inducers.items()
        for apply_to, inducers in items:
            for inducer in inducers:
                if apply_to=='rows':
                    for column in inducer.doses_table.columns:
                        for i in range(self.n_rows):
                            for j in range(self.n_cols):
                                samples_table.set_value(
                                    samples_table.index[i*self.n_cols + j],
                                    column,
                                    inducer.doses_table.iloc[j][column])
                elif apply_to=='cols':
                    for column in inducer.doses_table.columns:
                        for i in range(self.n_rows):
                            for j in range(self.n_cols):
                                samples_table.set_value(
                                    samples_table.index[i*self.n_cols + j],
                                    column,
                                    inducer.doses_table.iloc[i][column])
                elif apply_to=='wells':
                    for column in inducer.doses_table.columns:
                        samples_table[column] = \
                            inducer.doses_table[column].values
                elif apply_to=='media':
                    for column in inducer.doses_table.columns:
                        samples_table[column] = \
                            inducer.doses_table[column].value

        # Create closed plate objects
        closed_plates = []
        for i in range(self.array_n_rows):
            for j in range(self.array_n_cols):
                # Filter samples table using the plate name
                plate_name = self.plate_names[i*self.array_n_cols + j]
                plate_samples_table = \
                    samples_table[samples_table['Plate']==plate_name]
                # Extract id info directly from index
                plate_id_prefix = plate_samples_table.index[0][:-3]
                plate_id_offset = int(plate_samples_table.index[0][-3:])
                # Create closed plate
                closed_plate = ClosedPlate(id_prefix=plate_id_prefix,
                                           id_offset=plate_id_offset,
                                           samples_table=plate_samples_table)
                closed_plates.append(closed_plate)

        return closed_plates

class ClosedPlate(object):
    def __init__(self, id_prefix, id_offset, samples_table):
        # Store id prefix and offset
        self.id_prefix = id_prefix
        self.id_offset = id_offset
        # Sanity checks on samples table
        plate_name = samples_table.iloc[0]['Plate']
        if not (samples_table['Plate']==plate_name).all():
            raise ValueError('values of "Plate" column should be identical')
        # Save samples table
        self.samples_table = samples_table

    @property
    def name(self):
        """
        Plate name.

        """
        return self.samples_table.iloc[0]['Plate']

    @property
    def location(self):
        """
        Name of assigned location. Returns None if location not set.

        """
        if 'Location' in self.samples_table.columns:
            return self.samples_table.iloc[0]['Location']
        else:
            return None

    @location.setter
    def location(self, value):
        self.samples_table['Location'] = value

    def update_ids(self):
        """
        Update ids in samples table from id_offset and id_prefix

        """
        # Recreate IDs
        ids = ['{}{:03d}'.format(self.id_prefix, i)
               for i in range(self.id_offset + 1,
                              len(self.samples_table) + self.id_offset + 1)]
        self.samples_table.index = ids
