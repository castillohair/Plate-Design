"""
Module that contains the experiment class.

"""

import copy
import os

import numpy
import openpyxl
import pandas

class Experiment(object):
    """
    Object that represents a plate experiment.

    A plate experiment can include one or more plates and several inducers
    that are applied to these plates. An experiment is performed in
    replicates: one or more repetitions of the same protocol. Some
    conditions can be randomized in each replicate, such as which samples
    have which inducer concentrations.

    Setting up a plate experiment is performed in several stages:
        - Experiment setup: Inducers and plates are prepared and stored.
          Media is prepared if necessary. No cells are cultured during this
          stage.
        - Replicate setup: Plates are set up with the indicated amount of
          of inducer, inoculated with cells, and placed under growth
          conditions for a specified amount of time.
        - Replicate measurement: Plates are placed in growth-arresting
          conditions, and measurements of each sample are conducted. These
          can be absorbance or fluorescence from plate readers,
          fluorescence from flow cytometers, etc.

    The major purpose of this class is to generate instruction files for
    each one of these stages, given specifications on the inducers and
    plates. For example:
        - Experiment setup: Instructions for preparing inducer dilutions
          and media.
        - Replicate setup: Instructions for inoculating inducers and cells.
        - Replicate measurement: Table with list of samples to measure.

    Attributes
    ----------
    n_replicates : int
        Number of replicates.
    randomize_inducer : bool
        Whether to randomize inducer concentrations for each replicate.
    plates : list
        Plates in the experiment.
    inducers : list
        Inducers in the experiment.
    measurement_template : str
        Name of a file to be used as template for the replicate measurement
        table. Sheets other than "Samples" will be copied unmodified. If a
        "Samples" sheet is present, all columns will be added to the final
        "Samples" sheet, and filled with the values present in the first
        row.
    plate_measurements : list
        Each element of this list is the name of a measurement to record
        at the end of the experiment for each plate. An empty table in
        which to record these values will be created in the replicate
        measurement file, sheet "Plate Measurements".

    Methods
    -------
    add_plate
        Add plate to experiment.
    add_inducer
        Add inducer to experiment.
    generate
        Generate instruction files for all stages of the experiment.

    """
    def __init__(self):
        # Initialize properties
        self.n_replicates = 3
        self.randomize = False
        # Initialize containers of plates and inducers.
        self.plates = []
        self.inducers = []
        # Template for table of samples for measurement.
        self.measurement_template = None
        # List of measurements per plate to take
        self.plate_measurements = []

    def add_plate(self, plate):
        """
        Add plate to experiment.

        Parameters
        ----------
        plate : Plate
            Plate to add.

        """
        self.plates.append(plate)

    def add_inducer(self, inducer):
        """
        Add inducer to experiment.

        Parameters
        ----------
        inducer : Inducer
            Inducer to add.

        """
        self.inducers.append(inducer)

    def generate(self, path='.'):
        """
        Generate instruction files for all stages of the experiment.

        This function creates files with instructions for all the stages of
        an experiment. Experiment setup files are stored in `path`. Then,
        separate folders are created for each one of the replicates, and
        files for the replicate setup and replicate measurement stages are
        created therein.

        Parameters
        ----------
        path : str, optional
            Folder in which to create all experiment files.

        """
        # Create folders for each replicate
        replicate_folders = [os.path.join(path,
                                          'replicate_{:03d}'.format(i + 1))
                             for i in range(self.n_replicates)]
        # First, check if folders already exist. If so, abort.
        for folder in replicate_folders:
            if os.path.exists(folder):
                raise IOError("folder {} already exists".format(folder))
        # Create folders
        for folder in replicate_folders:
            os.makedirs(folder)

        ###
        # Experiment Setup Stage
        ###
        # Check if spreadsheet already exists
        wb_exp_setup_filename = os.path.join(path, 'experiment_setup.xlsx')
        if os.path.exists(wb_exp_setup_filename):
            raise IOError("file {} already exists".format(
                wb_exp_setup_filename))
        # Create single spreadsheet for all experiment setup instructions
        wb_exp_setup = openpyxl.Workbook()
        # Remove sheet created by default
        wb_exp_setup.remove_sheet(wb_exp_setup.active)
        # Run Experiment Setup for inducers
        for inducer in self.inducers:
            # Get inducer applications on all plates
            ind_applications = []
            for plate in self.plates:
                # The following try-catch block is needed to ensure
                # compatibility with both python2 and python3.
                try:
                    items = plate.inducers.iteritems()
                except AttributeError:
                    items = plate.inducers.items()
                for apply_to, plate_inducers in items:
                    if inducer in plate_inducers:
                        ind_applications.append({'apply_to': apply_to,
                                                 'plate': plate})

            # Consistency check: inducers should be applied to all plates
            # identically.
            apply_to_all = [a['apply_to'] for a in ind_applications]
            if not all([a==apply_to_all[0] for a in apply_to_all]):
                raise ValueError("inducer can only be applied to the same"
                    " dimension on all plates")
            apply_to = apply_to_all[0]

            # Consistency check: inducers should be applied to samples with
            # identical volumes in all plates
            media_vol_all = [a['plate'].apply_inducer_media_vol(apply_to)
                             for a in ind_applications]
            if not all([m==media_vol_all[0] for m in media_vol_all]):
                raise ValueError("inducer can only be applied to the same"
                    " media volume on all plates")
            # Set media volume in inducer object
            inducer.media_vol = media_vol_all[0]

            # Calculate total amount of inducer to make from number of shots
            # and replicates
            n_shots = sum([a['plate'].apply_inducer_n_shots(apply_to)
                           for a in ind_applications])
            inducer.set_vol_from_shots(n_shots=n_shots,
                                       n_replicates=self.n_replicates)

            # Save files
            inducer.save_exp_setup_instructions(workbook=wb_exp_setup)
            inducer.save_exp_setup_files(path=path)

        # Run Experiment Setup for plates
        for plate in self.plates:
            plate.save_exp_setup_instructions(workbook=wb_exp_setup)
            plate.save_exp_setup_files(path=path)

        # Save spreadsheet
        wb_exp_setup.save(filename=wb_exp_setup_filename)

        # Iterate over replicates
        for replicate_idx in range(self.n_replicates):
            ###
            # Replicate Setup Stage
            ###
            # Create single spreadsheet for all replicate setup instructions
            wb_rep_setup = openpyxl.Workbook()
            # Remove sheet created by default
            wb_rep_setup.remove_sheet(wb_rep_setup.active)

            # Shuffle inducer and save replicate setup files
            for inducer in self.inducers:
                if self.randomize:
                    inducer.shuffle()
                inducer.save_rep_setup_instructions(workbook=wb_rep_setup)
                inducer.save_rep_setup_files(path=path)

            # Run all plate calculations
            for plate in self.plates:
                # Save files
                plate.save_rep_setup_instructions(workbook=wb_rep_setup)
                plate.save_rep_setup_files(path=path)

            # Save spreadsheet
            wb_rep_setup_filename = os.path.join(
                replicate_folders[replicate_idx],
                'replicate_{:03d}_setup.xlsx'.format(replicate_idx + 1))
            wb_rep_setup.save(filename=wb_rep_setup_filename)

            ###
            # Replicate Measurement Stage
            ###

            # Plate measurements table
            plate_measurements_table = pandas.DataFrame()
            plate_measurements_table['Plate'] = [p.name for p in self.plates]
            for m in self.plate_measurements:
                plate_measurements_table[m] = numpy.nan
            # Plate column should be the index
            plate_measurements_table.set_index('Plate', inplace=True)

            # Samples table
            samples_table = pandas.DataFrame()
            samples_table_columns = []

            for plate in self.plates:
                # Set the plate offset from the number of samples so far
                plate.id_offset = len(samples_table)
                # Update samples table
                plate.update_samples_table()
                # The following is necessary to preserve the order of the
                # columns when appending
                for column in plate.samples_table.columns:
                    if column not in samples_table_columns:
                        samples_table_columns.append(column)
                # Append plate's samples table to samples table
                samples_table = samples_table.append(plate.samples_table)
                # Sort columns
                samples_table = samples_table[samples_table_columns]

            # File name for replicate measurement file
            wb_rep_measurement_filename = os.path.join(
                replicate_folders[replicate_idx],
                'replicate_{:03d}_measurement.xlsx'.format(replicate_idx + 1))
            # Generate pandas writer
            writer = pandas.ExcelWriter(wb_rep_measurement_filename,
                                        engine='openpyxl')
            
            # Add information from template file, if specified
            if self.measurement_template is not None:
                workbook_template = openpyxl.load_workbook(
                    self.measurement_template)
                for ws in workbook_template.worksheets:
                    if ws.title != "Samples":
                        # Create new sheet
                        ws_new = writer.book.create_sheet(ws.title)
                        # Copy all cells' content and style
                        for row in ws.iter_rows():
                            for cell in row:
                                new_cell = ws_new.cell(row=cell.row,
                                                       column=cell.col_idx)
                                new_cell.value = cell.value
                                if cell.has_style:
                                    new_cell.font = \
                                        copy.copy(cell.font)
                                    new_cell.border = \
                                        copy.copy(cell.border)
                                    new_cell.fill = \
                                        copy.copy(cell.fill)
                                    new_cell.number_format = \
                                        copy.copy(cell.number_format)
                                    new_cell.protection = \
                                        copy.copy(cell.protection)
                                    new_cell.alignment = \
                                        copy.copy(cell.alignment)
                    else:
                        # Read with pandas
                        samples_extra = pandas.read_excel(
                            self.measurement_template,
                            sheetname="Samples")
                        # Extract first row
                        samples_extra = samples_extra.iloc[0]
                        # Add columns to samples_table
                        # The following try-catch block is needed to ensure
                        # compatibility with both python2 and python3.
                        try:
                            items = samples_extra.iteritems()
                        except AttributeError:
                            items = samples_extra.items()
                        for index, value in items:
                            try:
                                value = [value.format(i + 1)
                                         for i in range(len(samples_table))]
                            except AttributeError as e:
                                pass
                            samples_table[index] = value

            # Convert pandas tables to sheet and save
            samples_table.to_excel(writer, sheet_name='Samples')
            if len(plate_measurements_table.columns):
                plate_measurements_table.to_excel(
                    writer,
                    sheet_name='Plate Measurements')
            writer.save()
