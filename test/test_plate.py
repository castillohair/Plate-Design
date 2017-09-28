# -*- coding: UTF-8 -*-
"""
Unit tests for plate classes

"""

import collections
import itertools
import os
import random
import shutil
import unittest

import numpy
import openpyxl
import pandas

import platedesign

class TestPlate(unittest.TestCase):
    """
    Tests for the Plate class

    """
    def setUp(self):
        # Directory where to save temporary files
        self.temp_dir = "test/temp_plate"
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
        # Set random seed
        random.seed(1)

    def tearDown(self):
        # Delete temporary directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_create(self):
        p = platedesign.plate.Plate(name='P1')

    def test_default_attributes(self):
        p = platedesign.plate.Plate(name='P1')
        # Check all attributes
        self.assertEqual(p.name, 'P1')
        self.assertEqual(p.n_rows, 4)
        self.assertEqual(p.n_cols, 6)
        self.assertEqual(p.samples_to_measure, 24)
        self.assertIsNone(p.sample_media_vol)
        self.assertIsNone(p.total_media_vol)
        self.assertIsNone(p.cell_strain_name)
        self.assertIsNone(p.cell_setup_method)
        self.assertEqual(p.cell_predilution, 1)
        self.assertIsNone(p.cell_predilution_vol)
        self.assertIsNone(p.cell_initial_od600)
        self.assertIsNone(p.cell_shot_vol)
        self.assertEqual(p.metadata, collections.OrderedDict())
        self.assertEqual(p.inducers, {'rows': [],
                                      'cols': [],
                                      'wells': [],
                                      'media': []})

    def test_non_default_attributes(self):
        p = platedesign.plate.Plate(name='P1', n_rows=8, n_cols=12)
        # Check all attributes
        self.assertEqual(p.name, 'P1')
        self.assertEqual(p.n_rows, 8)
        self.assertEqual(p.n_cols, 12)
        self.assertEqual(p.samples_to_measure, 96)
        self.assertIsNone(p.sample_media_vol)
        self.assertIsNone(p.total_media_vol)
        self.assertIsNone(p.cell_strain_name)
        self.assertIsNone(p.cell_setup_method)
        self.assertEqual(p.cell_predilution, 1)
        self.assertIsNone(p.cell_predilution_vol)
        self.assertIsNone(p.cell_initial_od600)
        self.assertIsNone(p.cell_shot_vol)
        self.assertEqual(p.metadata, collections.OrderedDict())
        self.assertEqual(p.inducers, {'rows': [],
                                      'cols': [],
                                      'wells': [],
                                      'media': []})

    def test_apply_inducer_media_vol_1(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Set media volume
        p.total_media_vol = 13000
        p.sample_media_vol = 500
        # Get media volume for inducer application
        self.assertEqual(p.apply_inducer_media_vol('rows'), 500)
        self.assertEqual(p.apply_inducer_media_vol('cols'), 500)
        self.assertEqual(p.apply_inducer_media_vol('wells'), 500)
        self.assertEqual(p.apply_inducer_media_vol('media'), 13000)

    def test_apply_inducer_media_vol_error_1(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Set media volume
        p.total_media_vol = 13000
        p.sample_media_vol = 500
        # Limit number of samples to measure
        p.samples_to_measure = 12
        # Get media volume for inducer application
        self.assertEqual(p.apply_inducer_media_vol('wells'), 500)
        self.assertEqual(p.apply_inducer_media_vol('media'), 13000)
        # Verify that exception is raised for 'rows' and 'cols'
        self.assertRaises(ValueError, p.apply_inducer_media_vol, 'rows')
        self.assertRaises(ValueError, p.apply_inducer_media_vol, 'cols')

    def test_apply_inducer_media_vol_error_2(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Set media volume
        p.total_media_vol = 13000
        p.sample_media_vol = 500
        # Verify that exception is raised for an invalid 'apply_to' argument
        self.assertRaises(ValueError, p.apply_inducer_media_vol, 'all')

    def test_apply_inducer_media_vol_error_3(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Only set total media volume
        p.total_media_vol = 13000
        # Verify that exception is raised
        self.assertRaises(AttributeError, p.apply_inducer_media_vol, 'rows')

    def test_apply_inducer_media_vol_error_4(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Only set sample media volume
        p.sample_media_vol = 500
        # Verify that exception is raised
        self.assertRaises(AttributeError, p.apply_inducer_media_vol, 'rows')

    def test_apply_inducer_media_vol_error_5(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Don't set any media volume
        # Verify that exception is raised
        self.assertRaises(AttributeError, p.apply_inducer_media_vol, 'rows')

    def test_apply_inducer_n_shots(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Get number of shots for inducer application
        self.assertEqual(p.apply_inducer_n_shots('rows'), 4)
        self.assertEqual(p.apply_inducer_n_shots('cols'), 6)
        self.assertEqual(p.apply_inducer_n_shots('wells'), 1)
        self.assertEqual(p.apply_inducer_n_shots('media'), 1)

    def test_apply_inducer_n_shots_error_1(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Limit number of samples to measure
        p.samples_to_measure = 12
        # Get number of shots for inducer application
        self.assertEqual(p.apply_inducer_n_shots('wells'), 1)
        self.assertEqual(p.apply_inducer_n_shots('media'), 1)
        # Verify that exception is raised for 'rows' and 'cols'
        self.assertRaises(ValueError, p.apply_inducer_n_shots, 'rows')
        self.assertRaises(ValueError, p.apply_inducer_n_shots, 'cols')

    def test_apply_inducer_n_shots_error_2(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Verify that exception is raised for an invalid 'apply_to' argument
        self.assertRaises(ValueError, p.apply_inducer_n_shots, 'all')

    def test_apply_inducer_rows(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Create inducer
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set concentrations from gradient
        iptg.set_gradient(min=1e-6, max=1e-3, n=6, scale='log')
        # Apply inducer to plate
        p.apply_inducer(iptg, apply_to='rows')
        # Check that inducers dictionary in plate has been updated
        self.assertEqual(p.inducers, {'rows': [iptg],
                                      'cols': [],
                                      'wells': [],
                                      'media': []})

    def test_apply_inducer_rows_error_1(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Create inducer
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set concentrations from gradient
        iptg.set_gradient(min=1e-6, max=1e-3, n=4, scale='log')
        # Apply inducer to plate
        self.assertRaises(ValueError, p.apply_inducer, iptg, apply_to='rows')
        # Check that inducers dictionary in plate has not been updated
        self.assertEqual(p.inducers, {'rows': [],
                                      'cols': [],
                                      'wells': [],
                                      'media': []})

    def test_apply_inducer_rows_error_2(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Limit number of samples to measure
        p.samples_to_measure = 12
        # Create inducer
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set concentrations from gradient
        iptg.set_gradient(min=1e-6, max=1e-3, n=6, scale='log')
        # Apply inducer to plate
        self.assertRaises(ValueError, p.apply_inducer, iptg, apply_to='rows')
        # Check that inducers dictionary in plate has not been updated
        self.assertEqual(p.inducers, {'rows': [],
                                      'cols': [],
                                      'wells': [],
                                      'media': []})

    def test_apply_inducer_cols(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Create inducer
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set concentrations from gradient
        iptg.set_gradient(min=1e-6, max=1e-3, n=4, scale='log')
        # Apply inducer to plate
        p.apply_inducer(iptg, apply_to='cols')
        # Check that inducers dictionary in plate has been updated
        self.assertEqual(p.inducers, {'rows': [],
                                      'cols': [iptg],
                                      'wells': [],
                                      'media': []})

    def test_apply_inducer_cols_error_1(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Create inducer
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set concentrations from gradient
        iptg.set_gradient(min=1e-6, max=1e-3, n=6, scale='log')
        # Apply inducer to plate
        self.assertRaises(ValueError, p.apply_inducer, iptg, apply_to='cols')
        # Check that inducers dictionary in plate has not been updated
        self.assertEqual(p.inducers, {'rows': [],
                                      'cols': [],
                                      'wells': [],
                                      'media': []})

    def test_apply_inducer_cols_error_2(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Limit number of samples to measure
        p.samples_to_measure = 12
        # Create inducer
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set concentrations from gradient
        iptg.set_gradient(min=1e-6, max=1e-3, n=4, scale='log')
        # Apply inducer to plate
        self.assertRaises(ValueError, p.apply_inducer, iptg, apply_to='cols')
        # Check that inducers dictionary in plate has not been updated
        self.assertEqual(p.inducers, {'rows': [],
                                      'cols': [],
                                      'wells': [],
                                      'media': []})

    def test_apply_inducer_wells(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Create inducer
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set concentrations from gradient
        iptg.set_gradient(min=1e-6, max=1e-3, n=24, scale='log')
        # Apply inducer to plate
        p.apply_inducer(iptg, apply_to='wells')
        # Check that inducers dictionary in plate has been updated
        self.assertEqual(p.inducers, {'rows': [],
                                      'cols': [],
                                      'wells': [iptg],
                                      'media': []})

    def test_apply_inducer_wells_2(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Limit number of samples to measure
        p.samples_to_measure = 12
        # Create inducer
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set concentrations from gradient
        iptg.set_gradient(min=1e-6, max=1e-3, n=12, scale='log')
        # Apply inducer to plate
        p.apply_inducer(iptg, apply_to='wells')
        # Check that inducers dictionary in plate has been updated
        self.assertEqual(p.inducers, {'rows': [],
                                      'cols': [],
                                      'wells': [iptg],
                                      'media': []})

    def test_apply_inducer_wells_error_1(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Create inducer
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set concentrations from gradient
        iptg.set_gradient(min=1e-6, max=1e-3, n=15, scale='log')
        # Apply inducer to plate
        self.assertRaises(ValueError, p.apply_inducer, iptg, apply_to='wells')
        # Check that inducers dictionary in plate has been updated
        self.assertEqual(p.inducers, {'rows': [],
                                      'cols': [],
                                      'wells': [],
                                      'media': []})

    def test_apply_inducer_wells_error_2(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Limit number of samples to measure
        p.samples_to_measure = 12
        # Create inducer
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set concentrations from gradient
        iptg.set_gradient(min=1e-6, max=1e-3, n=15, scale='log')
        # Apply inducer to plate
        self.assertRaises(ValueError, p.apply_inducer, iptg, apply_to='wells')
        # Check that inducers dictionary in plate has been updated
        self.assertEqual(p.inducers, {'rows': [],
                                      'cols': [],
                                      'wells': [],
                                      'media': []})

    def test_apply_inducer_media_1(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Create inducer
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set concentrations
        iptg.concentrations = [1]
        # Apply inducer to plate
        p.apply_inducer(iptg, apply_to='media')
        # Check that inducers dictionary in plate has been updated
        self.assertEqual(p.inducers, {'rows': [],
                                      'cols': [],
                                      'wells': [],
                                      'media': [iptg]})

    def test_apply_inducer_media_2(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Limit number of samples to measure
        p.samples_to_measure = 12
        # Create inducer
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set concentrations
        iptg.concentrations = [1]
        # Apply inducer to plate
        p.apply_inducer(iptg, apply_to='media')
        # Check that inducers dictionary in plate has been updated
        self.assertEqual(p.inducers, {'rows': [],
                                      'cols': [],
                                      'wells': [],
                                      'media': [iptg]})

    def test_apply_inducer_media_error_1(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Create inducer
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set concentrations
        iptg.concentrations = [1, 10]
        # Apply inducer to plate
        self.assertRaises(ValueError, p.apply_inducer, iptg, apply_to='media')
        # Check that inducers dictionary in plate has been updated
        self.assertEqual(p.inducers, {'rows': [],
                                      'cols': [],
                                      'wells': [],
                                      'media': []})

    def test_apply_inducer_error_1(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Create inducer
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set concentrations
        iptg.concentrations = [1]
        # Apply inducer to plate
        self.assertRaises(ValueError, p.apply_inducer, iptg, apply_to='all')
        # Check that inducers dictionary in plate has been updated
        self.assertEqual(p.inducers, {'rows': [],
                                      'cols': [],
                                      'wells': [],
                                      'media': []})

    def test_save_exp_setup_instructions_1(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Run save_exp_setup_instructions
        p.save_exp_setup_instructions(file_name=os.path.join(self.temp_dir,
                                                             'plate_exp.xlsx'))
        # save_exp_setup_instructions does not do anything in Plate. There is
        # no need to check for results.

    def test_save_exp_setup_instructions_2(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Create new spreadsheet
        wb_test = openpyxl.Workbook()
        # Remove sheet created by default
        wb_test.remove_sheet(wb_test.active)
        # Run save_exp_setup_instructions
        p.save_exp_setup_instructions(workbook=wb_test)
        # save_exp_setup_instructions does not do anything in Plate. There is
        # no need to check for results.

    def test_save_exp_setup_instructions_argument_error(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Run save_exp_setup_instructions with no arguments
        self.assertRaises(ValueError, p.save_exp_setup_instructions)

    def test_save_exp_setup_files(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Check that save_exp_setup_files runs successfully
        p.save_exp_setup_files()
        # save_exp_setup_files does not do anything in Plate. There is no need
        # to check for results.

    def test_save_rep_setup_instructions_empty(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Run save_rep_setup_instructions
        p.save_rep_setup_instructions(file_name=os.path.join(self.temp_dir,
                                                             'plate_rep.xlsx'))
        # Load spreadsheet
        wb = openpyxl.load_workbook(filename=os.path.join(self.temp_dir,
                                                          'plate_rep.xlsx'))
        # Spreadsheet should only contain an empty sheet named "Sheet 1"
        self.assertEqual(wb.sheetnames, ["Sheet 1"])

    def test_save_rep_setup_instructions_cell_setup_fixed_volume_1(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.total_media_vol = 15000.
        # Add some information for cell setup
        p.cell_strain_name = 'Test strain 1'
        p.cell_setup_method = 'fixed_volume'
        p.cell_shot_vol = 5
        # Run save_rep_setup_instructions
        p.save_rep_setup_instructions(file_name=os.path.join(self.temp_dir,
                                                             'plate_rep.xlsx'))
        # Load spreadsheet
        wb = openpyxl.load_workbook(filename=os.path.join(self.temp_dir,
                                                          'plate_rep.xlsx'))
        # Spreadsheet should contain one sheet
        self.assertEqual(wb.sheetnames, ["Cells for Plate P1"])
        # Check cell inoculation instructions
        ws = wb.get_sheet_by_name("Cells for Plate P1")
        self.assertEqual(ws.cell(row=1, column=1).value, "Strain Name")
        self.assertEqual(ws.cell(row=1, column=2).value, "Test strain 1")
        self.assertEqual(ws.cell(row=2, column=1).value, "Preculture volume")
        self.assertEqual(ws.cell(row=2, column=2).value, 5)
        self.assertEqual(ws.cell(row=2, column=3).value, u"µL")
        self.assertEqual(ws.cell(row=3, column=1).value, "Add into 15.00mL "
            "media, and distribute into plate wells.")

    def test_save_rep_setup_instructions_cell_setup_fixed_volume_2(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.total_media_vol = 15000.
        # Add some information for cell setup
        p.cell_strain_name = 'Test strain 1'
        p.cell_setup_method = 'fixed_volume'
        p.cell_predilution = 100
        p.cell_predilution_vol = 1000
        p.cell_shot_vol = 5
        # Run save_rep_setup_instructions
        p.save_rep_setup_instructions(file_name=os.path.join(self.temp_dir,
                                                             'plate_rep.xlsx'))
        # Load spreadsheet
        wb = openpyxl.load_workbook(filename=os.path.join(self.temp_dir,
                                                          'plate_rep.xlsx'))
        # Spreadsheet should contain one sheet
        self.assertEqual(wb.sheetnames, ["Cells for Plate P1"])
        # Check cell inoculation instructions
        ws = wb.get_sheet_by_name("Cells for Plate P1")
        self.assertEqual(ws.cell(row=1, column=1).value, "Strain Name")
        self.assertEqual(ws.cell(row=1, column=2).value, "Test strain 1")
        self.assertTrue('A2:C2' in ws.merged_cell_ranges)
        self.assertEqual(ws.cell(row=2, column=1).value, "Predilution")
        self.assertEqual(ws.cell(row=3, column=1).value, "Predilution factor")
        self.assertEqual(ws.cell(row=3, column=2).value, 100)
        self.assertEqual(ws.cell(row=3, column=3).value, "x")
        self.assertEqual(ws.cell(row=4, column=1).value, "Media volume")
        self.assertEqual(ws.cell(row=4, column=2).value, 990)
        self.assertEqual(ws.cell(row=4, column=3).value, u"µL")
        self.assertEqual(ws.cell(row=5, column=1).value, "Preculture volume")
        self.assertEqual(ws.cell(row=5, column=2).value, 10)
        self.assertEqual(ws.cell(row=5, column=3).value, u"µL")
        self.assertTrue('A6:C6' in ws.merged_cell_ranges)
        self.assertEqual(ws.cell(row=6, column=1).value, "Inoculation")
        self.assertEqual(ws.cell(row=7, column=1).value, "Predilution volume")
        self.assertEqual(ws.cell(row=7, column=2).value, 5)
        self.assertEqual(ws.cell(row=7, column=3).value, u"µL")
        self.assertEqual(ws.cell(row=8, column=1).value, "Add into 15.00mL "
            "media, and distribute into plate wells.")

    def test_save_rep_setup_instructions_cell_setup_fixed_volume_error_1(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.total_media_vol = 15000.
        # Add some information for cell setup
        # Do not include shot volume
        p.cell_strain_name = 'Test strain 1'
        p.cell_setup_method = 'fixed_volume'
        p.cell_predilution = 100
        p.cell_predilution_vol = 1000
        # Run save_rep_setup_instructions
        self.assertRaises(
            ValueError,
            p.save_rep_setup_instructions,
            file_name=os.path.join(self.temp_dir, 'plate_rep.xlsx'))

    def test_save_rep_setup_instructions_cell_setup_fixed_volume_error_2(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.total_media_vol = 15000.
        # Add some information for cell setup
        # Do not include predilution volume
        p.cell_strain_name = 'Test strain 1'
        p.cell_setup_method = 'fixed_volume'
        p.cell_predilution = 100
        p.cell_shot_vol = 5
        # Run save_rep_setup_instructions
        self.assertRaises(
            ValueError,
            p.save_rep_setup_instructions,
            file_name=os.path.join(self.temp_dir, 'plate_rep.xlsx'))

    def test_save_rep_setup_instructions_cell_setup_fixed_od600_1(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.total_media_vol = 15000.
        # Add some information for cell setup
        p.cell_strain_name = 'Test strain 1'
        p.cell_setup_method = 'fixed_od600'
        p.cell_initial_od600 = 1e-5
        # Run save_rep_setup_instructions
        p.save_rep_setup_instructions(file_name=os.path.join(self.temp_dir,
                                                             'plate_rep.xlsx'))
        # Load spreadsheet
        wb = openpyxl.load_workbook(filename=os.path.join(self.temp_dir,
                                                          'plate_rep.xlsx'))
        # Spreadsheet should contain one sheet
        self.assertEqual(wb.sheetnames, ["Cells for Plate P1"])
        # Check cell inoculation instructions
        ws = wb.get_sheet_by_name("Cells for Plate P1")
        self.assertEqual(ws.cell(row=1, column=1).value, "Strain Name")
        self.assertEqual(ws.cell(row=1, column=2).value, "Test strain 1")
        self.assertEqual(ws.cell(row=2, column=1).value, "Preculture OD600")
        self.assertEqual(ws.cell(row=2, column=2).value, None)
        self.assertEqual(ws.cell(row=2, column=3).value, None)
        self.assertEqual(ws.cell(row=3, column=1).value, "Target OD600")
        self.assertEqual(ws.cell(row=3, column=2).value, 1e-5)
        self.assertEqual(ws.cell(row=3, column=3).value, None)
        self.assertEqual(ws.cell(row=4, column=1).value, "Preculture volume")
        self.assertEqual(ws.cell(row=4, column=2).value, "=0.15/B2")
        self.assertEqual(ws.cell(row=4, column=3).value, u"µL")
        self.assertEqual(ws.cell(row=5, column=1).value, "Add into 15.00mL "
            "media, and distribute into plate wells.")

    def test_save_rep_setup_instructions_cell_setup_fixed_od600_2(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.total_media_vol = 15000.
        # Add some information for cell setup
        p.cell_strain_name = 'Test strain 1'
        p.cell_setup_method = 'fixed_od600'
        p.cell_predilution = 100
        p.cell_predilution_vol = 1000
        p.cell_initial_od600 = 1e-5
        # Run save_rep_setup_instructions
        p.save_rep_setup_instructions(file_name=os.path.join(self.temp_dir,
                                                             'plate_rep.xlsx'))
        # Load spreadsheet
        wb = openpyxl.load_workbook(filename=os.path.join(self.temp_dir,
                                                          'plate_rep.xlsx'))
        # Spreadsheet should contain one sheet
        self.assertEqual(wb.sheetnames, ["Cells for Plate P1"])
        # Check cell inoculation instructions
        ws = wb.get_sheet_by_name("Cells for Plate P1")
        self.assertEqual(ws.cell(row=1, column=1).value, "Strain Name")
        self.assertEqual(ws.cell(row=1, column=2).value, "Test strain 1")
        self.assertTrue('A2:C2' in ws.merged_cell_ranges)
        self.assertEqual(ws.cell(row=2, column=1).value, "Predilution")
        self.assertEqual(ws.cell(row=3, column=1).value, "Predilution factor")
        self.assertEqual(ws.cell(row=3, column=2).value, 100)
        self.assertEqual(ws.cell(row=3, column=3).value, "x")
        self.assertEqual(ws.cell(row=4, column=1).value, "Media volume")
        self.assertEqual(ws.cell(row=4, column=2).value, 990)
        self.assertEqual(ws.cell(row=4, column=3).value, u"µL")
        self.assertEqual(ws.cell(row=5, column=1).value, "Preculture volume")
        self.assertEqual(ws.cell(row=5, column=2).value, 10)
        self.assertEqual(ws.cell(row=5, column=3).value, u"µL")
        self.assertEqual(ws.cell(row=6, column=1).value, "Predilution OD600")
        self.assertEqual(ws.cell(row=6, column=2).value, None)
        self.assertEqual(ws.cell(row=6, column=3).value, None)
        self.assertTrue('A7:C7' in ws.merged_cell_ranges)
        self.assertEqual(ws.cell(row=7, column=1).value, "Inoculation")
        self.assertEqual(ws.cell(row=8, column=1).value, "Target OD600")
        self.assertEqual(ws.cell(row=8, column=2).value, 1e-5)
        self.assertEqual(ws.cell(row=8, column=3).value, None)
        self.assertEqual(ws.cell(row=9, column=1).value, "Predilution volume")
        self.assertEqual(ws.cell(row=9, column=2).value, "=0.15/B6")
        self.assertEqual(ws.cell(row=9, column=3).value, u"µL")
        self.assertEqual(ws.cell(row=10, column=1).value, "Add into 15.00mL "
            "media, and distribute into plate wells.")

    def test_save_rep_setup_instructions_cell_setup_fixed_od600_error_1(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.total_media_vol = 15000.
        # Add some information for cell setup
        # Do not include target od600
        p.cell_strain_name = 'Test strain 1'
        p.cell_setup_method = 'fixed_od600'
        p.cell_predilution = 100
        p.cell_predilution_vol = 1000
        # Run save_rep_setup_instructions
        self.assertRaises(
            ValueError,
            p.save_rep_setup_instructions,
            file_name=os.path.join(self.temp_dir, 'plate_rep.xlsx'))

    def test_save_rep_setup_instructions_cell_setup_fixed_od600_error_2(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.total_media_vol = 15000.
        # Add some information for cell setup
        # Do not include predilution volume
        p.cell_strain_name = 'Test strain 1'
        p.cell_setup_method = 'fixed_od600'
        p.cell_predilution = 100
        p.cell_initial_od600 = 1e-5
        # Run save_rep_setup_instructions
        self.assertRaises(
            ValueError,
            p.save_rep_setup_instructions,
            file_name=os.path.join(self.temp_dir, 'plate_rep.xlsx'))

    def test_save_rep_setup_instructions_inducer_rows_1(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Create inducer for plate rows
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.set_gradient(min=1e-6, max=1e-3, n=6, scale='log')
        p.apply_inducer(iptg, apply_to='rows')
        # Run save_rep_setup_instructions
        p.save_rep_setup_instructions(file_name=os.path.join(self.temp_dir,
                                                             'plate_rep.xlsx'))
        # Load spreadsheet
        wb = openpyxl.load_workbook(filename=os.path.join(self.temp_dir,
                                                          'plate_rep.xlsx'))
        # Spreadsheet should contain one sheet
        self.assertEqual(wb.sheetnames, ["Inducers for Plate P1"])
        # Check inducer inoculation instructions
        ws = wb.get_sheet_by_name("Inducers for Plate P1")
        self.assertEqual(ws.cell(row=1, column=1).value, "I001")
        self.assertEqual(ws.cell(row=1, column=2).value, "I002")
        self.assertEqual(ws.cell(row=1, column=3).value, "I003")
        self.assertEqual(ws.cell(row=1, column=4).value, "I004")
        self.assertEqual(ws.cell(row=1, column=5).value, "I005")
        self.assertEqual(ws.cell(row=1, column=6).value, "I006")
        self.assertEqual(ws.cell(row=2, column=1).value, "(1, 1)")
        self.assertEqual(ws.cell(row=2, column=2).value, "(1, 2)")
        self.assertEqual(ws.cell(row=2, column=3).value, "(1, 3)")
        self.assertEqual(ws.cell(row=2, column=4).value, "(1, 4)")
        self.assertEqual(ws.cell(row=2, column=5).value, "(1, 5)")
        self.assertEqual(ws.cell(row=2, column=6).value, "(1, 6)")
        self.assertEqual(ws.cell(row=3, column=1).value, "(2, 1)")
        self.assertEqual(ws.cell(row=3, column=2).value, "(2, 2)")
        self.assertEqual(ws.cell(row=3, column=3).value, "(2, 3)")
        self.assertEqual(ws.cell(row=3, column=4).value, "(2, 4)")
        self.assertEqual(ws.cell(row=3, column=5).value, "(2, 5)")
        self.assertEqual(ws.cell(row=3, column=6).value, "(2, 6)")
        self.assertEqual(ws.cell(row=4, column=1).value, "(3, 1)")
        self.assertEqual(ws.cell(row=4, column=2).value, "(3, 2)")
        self.assertEqual(ws.cell(row=4, column=3).value, "(3, 3)")
        self.assertEqual(ws.cell(row=4, column=4).value, "(3, 4)")
        self.assertEqual(ws.cell(row=4, column=5).value, "(3, 5)")
        self.assertEqual(ws.cell(row=4, column=6).value, "(3, 6)")
        self.assertEqual(ws.cell(row=5, column=1).value, "(4, 1)")
        self.assertEqual(ws.cell(row=5, column=2).value, "(4, 2)")
        self.assertEqual(ws.cell(row=5, column=3).value, "(4, 3)")
        self.assertEqual(ws.cell(row=5, column=4).value, "(4, 4)")
        self.assertEqual(ws.cell(row=5, column=5).value, "(4, 5)")
        self.assertEqual(ws.cell(row=5, column=6).value, "(4, 6)")

    def test_save_rep_setup_instructions_inducer_rows_2(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Create inducer for plate rows
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.set_gradient(min=1e-6, max=1e-3, n=6, scale='log')
        p.apply_inducer(iptg, apply_to='rows')
        # Create second inducer for plate rows
        atc = platedesign.inducer.ChemicalInducer(
            name='aTc',
            units=u'ng/µL')
        atc.set_gradient(min=0.5, max=50, n=6, scale='log')
        p.apply_inducer(atc, apply_to='rows')
        # Run save_rep_setup_instructions
        p.save_rep_setup_instructions(file_name=os.path.join(self.temp_dir,
                                                             'plate_rep.xlsx'))
        # Load spreadsheet
        wb = openpyxl.load_workbook(filename=os.path.join(self.temp_dir,
                                                          'plate_rep.xlsx'))
        # Spreadsheet should contain one sheet
        self.assertEqual(wb.sheetnames, ["Inducers for Plate P1"])
        # Check inducer inoculation instructions
        ws = wb.get_sheet_by_name("Inducers for Plate P1")
        self.assertEqual(ws.cell(row=1, column=1).value, "I001")
        self.assertEqual(ws.cell(row=1, column=2).value, "I002")
        self.assertEqual(ws.cell(row=1, column=3).value, "I003")
        self.assertEqual(ws.cell(row=1, column=4).value, "I004")
        self.assertEqual(ws.cell(row=1, column=5).value, "I005")
        self.assertEqual(ws.cell(row=1, column=6).value, "I006")
        self.assertEqual(ws.cell(row=2, column=1).value, "a001")
        self.assertEqual(ws.cell(row=2, column=2).value, "a002")
        self.assertEqual(ws.cell(row=2, column=3).value, "a003")
        self.assertEqual(ws.cell(row=2, column=4).value, "a004")
        self.assertEqual(ws.cell(row=2, column=5).value, "a005")
        self.assertEqual(ws.cell(row=2, column=6).value, "a006")
        self.assertEqual(ws.cell(row=3, column=1).value, "(1, 1)")
        self.assertEqual(ws.cell(row=3, column=2).value, "(1, 2)")
        self.assertEqual(ws.cell(row=3, column=3).value, "(1, 3)")
        self.assertEqual(ws.cell(row=3, column=4).value, "(1, 4)")
        self.assertEqual(ws.cell(row=3, column=5).value, "(1, 5)")
        self.assertEqual(ws.cell(row=3, column=6).value, "(1, 6)")
        self.assertEqual(ws.cell(row=4, column=1).value, "(2, 1)")
        self.assertEqual(ws.cell(row=4, column=2).value, "(2, 2)")
        self.assertEqual(ws.cell(row=4, column=3).value, "(2, 3)")
        self.assertEqual(ws.cell(row=4, column=4).value, "(2, 4)")
        self.assertEqual(ws.cell(row=4, column=5).value, "(2, 5)")
        self.assertEqual(ws.cell(row=4, column=6).value, "(2, 6)")
        self.assertEqual(ws.cell(row=5, column=1).value, "(3, 1)")
        self.assertEqual(ws.cell(row=5, column=2).value, "(3, 2)")
        self.assertEqual(ws.cell(row=5, column=3).value, "(3, 3)")
        self.assertEqual(ws.cell(row=5, column=4).value, "(3, 4)")
        self.assertEqual(ws.cell(row=5, column=5).value, "(3, 5)")
        self.assertEqual(ws.cell(row=5, column=6).value, "(3, 6)")
        self.assertEqual(ws.cell(row=6, column=1).value, "(4, 1)")
        self.assertEqual(ws.cell(row=6, column=2).value, "(4, 2)")
        self.assertEqual(ws.cell(row=6, column=3).value, "(4, 3)")
        self.assertEqual(ws.cell(row=6, column=4).value, "(4, 4)")
        self.assertEqual(ws.cell(row=6, column=5).value, "(4, 5)")
        self.assertEqual(ws.cell(row=6, column=6).value, "(4, 6)")

    def test_save_rep_setup_instructions_inducer_rows_3(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Create inducer for plate rows
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.set_gradient(min=1e-6, max=1e-3, n=6, scale='log')
        iptg.shuffle()
        p.apply_inducer(iptg, apply_to='rows')
        # Create second inducer for plate rows
        atc = platedesign.inducer.ChemicalInducer(
            name='aTc',
            units=u'ng/µL')
        atc.set_gradient(min=0.5, max=50, n=6, scale='log')
        p.apply_inducer(atc, apply_to='rows')
        # Run save_rep_setup_instructions
        p.save_rep_setup_instructions(file_name=os.path.join(self.temp_dir,
                                                             'plate_rep.xlsx'))
        # Load spreadsheet
        wb = openpyxl.load_workbook(filename=os.path.join(self.temp_dir,
                                                          'plate_rep.xlsx'))
        # Spreadsheet should contain one sheet
        self.assertEqual(wb.sheetnames, ["Inducers for Plate P1"])
        # Check inducer inoculation instructions
        # The order of IPTG values after shuffling has been checked manually
        ws = wb.get_sheet_by_name("Inducers for Plate P1")
        self.assertEqual(ws.cell(row=1, column=1).value, "I002")
        self.assertEqual(ws.cell(row=1, column=2).value, "I003")
        self.assertEqual(ws.cell(row=1, column=3).value, "I006")
        self.assertEqual(ws.cell(row=1, column=4).value, "I004")
        self.assertEqual(ws.cell(row=1, column=5).value, "I005")
        self.assertEqual(ws.cell(row=1, column=6).value, "I001")
        self.assertEqual(ws.cell(row=2, column=1).value, "a001")
        self.assertEqual(ws.cell(row=2, column=2).value, "a002")
        self.assertEqual(ws.cell(row=2, column=3).value, "a003")
        self.assertEqual(ws.cell(row=2, column=4).value, "a004")
        self.assertEqual(ws.cell(row=2, column=5).value, "a005")
        self.assertEqual(ws.cell(row=2, column=6).value, "a006")
        self.assertEqual(ws.cell(row=3, column=1).value, "(1, 1)")
        self.assertEqual(ws.cell(row=3, column=2).value, "(1, 2)")
        self.assertEqual(ws.cell(row=3, column=3).value, "(1, 3)")
        self.assertEqual(ws.cell(row=3, column=4).value, "(1, 4)")
        self.assertEqual(ws.cell(row=3, column=5).value, "(1, 5)")
        self.assertEqual(ws.cell(row=3, column=6).value, "(1, 6)")
        self.assertEqual(ws.cell(row=4, column=1).value, "(2, 1)")
        self.assertEqual(ws.cell(row=4, column=2).value, "(2, 2)")
        self.assertEqual(ws.cell(row=4, column=3).value, "(2, 3)")
        self.assertEqual(ws.cell(row=4, column=4).value, "(2, 4)")
        self.assertEqual(ws.cell(row=4, column=5).value, "(2, 5)")
        self.assertEqual(ws.cell(row=4, column=6).value, "(2, 6)")
        self.assertEqual(ws.cell(row=5, column=1).value, "(3, 1)")
        self.assertEqual(ws.cell(row=5, column=2).value, "(3, 2)")
        self.assertEqual(ws.cell(row=5, column=3).value, "(3, 3)")
        self.assertEqual(ws.cell(row=5, column=4).value, "(3, 4)")
        self.assertEqual(ws.cell(row=5, column=5).value, "(3, 5)")
        self.assertEqual(ws.cell(row=5, column=6).value, "(3, 6)")
        self.assertEqual(ws.cell(row=6, column=1).value, "(4, 1)")
        self.assertEqual(ws.cell(row=6, column=2).value, "(4, 2)")
        self.assertEqual(ws.cell(row=6, column=3).value, "(4, 3)")
        self.assertEqual(ws.cell(row=6, column=4).value, "(4, 4)")
        self.assertEqual(ws.cell(row=6, column=5).value, "(4, 5)")
        self.assertEqual(ws.cell(row=6, column=6).value, "(4, 6)")

    def test_save_rep_setup_instructions_inducer_cols_1(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Create inducer for plate columns
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.set_gradient(min=1e-6, max=1e-3, n=4, scale='log')
        p.apply_inducer(iptg, apply_to='cols')
        # Run save_rep_setup_instructions
        p.save_rep_setup_instructions(file_name=os.path.join(self.temp_dir,
                                                             'plate_rep.xlsx'))
        # Load spreadsheet
        wb = openpyxl.load_workbook(filename=os.path.join(self.temp_dir,
                                                          'plate_rep.xlsx'))
        # Spreadsheet should contain one sheet
        self.assertEqual(wb.sheetnames, ["Inducers for Plate P1"])
        # Check inducer inoculation instructions
        ws = wb.get_sheet_by_name("Inducers for Plate P1")
        self.assertEqual(ws.cell(row=1, column=1).value, "I001")
        self.assertEqual(ws.cell(row=1, column=2).value, "(1, 1)")
        self.assertEqual(ws.cell(row=1, column=3).value, "(1, 2)")
        self.assertEqual(ws.cell(row=1, column=4).value, "(1, 3)")
        self.assertEqual(ws.cell(row=1, column=5).value, "(1, 4)")
        self.assertEqual(ws.cell(row=1, column=6).value, "(1, 5)")
        self.assertEqual(ws.cell(row=1, column=7).value, "(1, 6)")
        self.assertEqual(ws.cell(row=2, column=1).value, "I002")
        self.assertEqual(ws.cell(row=2, column=2).value, "(2, 1)")
        self.assertEqual(ws.cell(row=2, column=3).value, "(2, 2)")
        self.assertEqual(ws.cell(row=2, column=4).value, "(2, 3)")
        self.assertEqual(ws.cell(row=2, column=5).value, "(2, 4)")
        self.assertEqual(ws.cell(row=2, column=6).value, "(2, 5)")
        self.assertEqual(ws.cell(row=2, column=7).value, "(2, 6)")
        self.assertEqual(ws.cell(row=3, column=1).value, "I003")
        self.assertEqual(ws.cell(row=3, column=2).value, "(3, 1)")
        self.assertEqual(ws.cell(row=3, column=3).value, "(3, 2)")
        self.assertEqual(ws.cell(row=3, column=4).value, "(3, 3)")
        self.assertEqual(ws.cell(row=3, column=5).value, "(3, 4)")
        self.assertEqual(ws.cell(row=3, column=6).value, "(3, 5)")
        self.assertEqual(ws.cell(row=3, column=7).value, "(3, 6)")
        self.assertEqual(ws.cell(row=4, column=1).value, "I004")
        self.assertEqual(ws.cell(row=4, column=2).value, "(4, 1)")
        self.assertEqual(ws.cell(row=4, column=3).value, "(4, 2)")
        self.assertEqual(ws.cell(row=4, column=4).value, "(4, 3)")
        self.assertEqual(ws.cell(row=4, column=5).value, "(4, 4)")
        self.assertEqual(ws.cell(row=4, column=6).value, "(4, 5)")
        self.assertEqual(ws.cell(row=4, column=7).value, "(4, 6)")

    def test_save_rep_setup_instructions_inducer_cols_2(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Create inducer for plate columns
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.set_gradient(min=1e-6, max=1e-3, n=4, scale='log')
        p.apply_inducer(iptg, apply_to='cols')
        # Create second inducer for plate columns
        atc = platedesign.inducer.ChemicalInducer(
            name='aTc',
            units=u'ng/µL')
        atc.set_gradient(min=0.5, max=50, n=4, scale='log')
        p.apply_inducer(atc, apply_to='cols')
        # Run save_rep_setup_instructions
        p.save_rep_setup_instructions(file_name=os.path.join(self.temp_dir,
                                                             'plate_rep.xlsx'))
        # Load spreadsheet
        wb = openpyxl.load_workbook(filename=os.path.join(self.temp_dir,
                                                          'plate_rep.xlsx'))
        # Spreadsheet should contain one sheet
        self.assertEqual(wb.sheetnames, ["Inducers for Plate P1"])
        # Check inducer inoculation instructions
        ws = wb.get_sheet_by_name("Inducers for Plate P1")
        self.assertEqual(ws.cell(row=1, column=1).value, "I001")
        self.assertEqual(ws.cell(row=1, column=2).value, "a001")
        self.assertEqual(ws.cell(row=1, column=3).value, "(1, 1)")
        self.assertEqual(ws.cell(row=1, column=4).value, "(1, 2)")
        self.assertEqual(ws.cell(row=1, column=5).value, "(1, 3)")
        self.assertEqual(ws.cell(row=1, column=6).value, "(1, 4)")
        self.assertEqual(ws.cell(row=1, column=7).value, "(1, 5)")
        self.assertEqual(ws.cell(row=1, column=8).value, "(1, 6)")
        self.assertEqual(ws.cell(row=2, column=1).value, "I002")
        self.assertEqual(ws.cell(row=2, column=2).value, "a002")
        self.assertEqual(ws.cell(row=2, column=3).value, "(2, 1)")
        self.assertEqual(ws.cell(row=2, column=4).value, "(2, 2)")
        self.assertEqual(ws.cell(row=2, column=5).value, "(2, 3)")
        self.assertEqual(ws.cell(row=2, column=6).value, "(2, 4)")
        self.assertEqual(ws.cell(row=2, column=7).value, "(2, 5)")
        self.assertEqual(ws.cell(row=2, column=8).value, "(2, 6)")
        self.assertEqual(ws.cell(row=3, column=1).value, "I003")
        self.assertEqual(ws.cell(row=3, column=2).value, "a003")
        self.assertEqual(ws.cell(row=3, column=3).value, "(3, 1)")
        self.assertEqual(ws.cell(row=3, column=4).value, "(3, 2)")
        self.assertEqual(ws.cell(row=3, column=5).value, "(3, 3)")
        self.assertEqual(ws.cell(row=3, column=6).value, "(3, 4)")
        self.assertEqual(ws.cell(row=3, column=7).value, "(3, 5)")
        self.assertEqual(ws.cell(row=3, column=8).value, "(3, 6)")
        self.assertEqual(ws.cell(row=4, column=1).value, "I004")
        self.assertEqual(ws.cell(row=4, column=2).value, "a004")
        self.assertEqual(ws.cell(row=4, column=3).value, "(4, 1)")
        self.assertEqual(ws.cell(row=4, column=4).value, "(4, 2)")
        self.assertEqual(ws.cell(row=4, column=5).value, "(4, 3)")
        self.assertEqual(ws.cell(row=4, column=6).value, "(4, 4)")
        self.assertEqual(ws.cell(row=4, column=7).value, "(4, 5)")
        self.assertEqual(ws.cell(row=4, column=8).value, "(4, 6)")

    def test_save_rep_setup_instructions_inducer_cols_3(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Create inducer for plate columns
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.set_gradient(min=1e-6, max=1e-3, n=4, scale='log')
        iptg.shuffle()
        p.apply_inducer(iptg, apply_to='cols')
        # Create second inducer for plate columns
        atc = platedesign.inducer.ChemicalInducer(
            name='aTc',
            units=u'ng/µL')
        atc.set_gradient(min=0.5, max=50, n=4, scale='log')
        p.apply_inducer(atc, apply_to='cols')
        # Run save_rep_setup_instructions
        p.save_rep_setup_instructions(file_name=os.path.join(self.temp_dir,
                                                             'plate_rep.xlsx'))
        # Load spreadsheet
        wb = openpyxl.load_workbook(filename=os.path.join(self.temp_dir,
                                                          'plate_rep.xlsx'))
        # Spreadsheet should contain one sheet
        self.assertEqual(wb.sheetnames, ["Inducers for Plate P1"])
        # Check inducer inoculation instructions
        # IPTG concentrations have been checked manually
        ws = wb.get_sheet_by_name("Inducers for Plate P1")
        self.assertEqual(ws.cell(row=1, column=1).value, "I004")
        self.assertEqual(ws.cell(row=1, column=2).value, "a001")
        self.assertEqual(ws.cell(row=1, column=3).value, "(1, 1)")
        self.assertEqual(ws.cell(row=1, column=4).value, "(1, 2)")
        self.assertEqual(ws.cell(row=1, column=5).value, "(1, 3)")
        self.assertEqual(ws.cell(row=1, column=6).value, "(1, 4)")
        self.assertEqual(ws.cell(row=1, column=7).value, "(1, 5)")
        self.assertEqual(ws.cell(row=1, column=8).value, "(1, 6)")
        self.assertEqual(ws.cell(row=2, column=1).value, "I002")
        self.assertEqual(ws.cell(row=2, column=2).value, "a002")
        self.assertEqual(ws.cell(row=2, column=3).value, "(2, 1)")
        self.assertEqual(ws.cell(row=2, column=4).value, "(2, 2)")
        self.assertEqual(ws.cell(row=2, column=5).value, "(2, 3)")
        self.assertEqual(ws.cell(row=2, column=6).value, "(2, 4)")
        self.assertEqual(ws.cell(row=2, column=7).value, "(2, 5)")
        self.assertEqual(ws.cell(row=2, column=8).value, "(2, 6)")
        self.assertEqual(ws.cell(row=3, column=1).value, "I003")
        self.assertEqual(ws.cell(row=3, column=2).value, "a003")
        self.assertEqual(ws.cell(row=3, column=3).value, "(3, 1)")
        self.assertEqual(ws.cell(row=3, column=4).value, "(3, 2)")
        self.assertEqual(ws.cell(row=3, column=5).value, "(3, 3)")
        self.assertEqual(ws.cell(row=3, column=6).value, "(3, 4)")
        self.assertEqual(ws.cell(row=3, column=7).value, "(3, 5)")
        self.assertEqual(ws.cell(row=3, column=8).value, "(3, 6)")
        self.assertEqual(ws.cell(row=4, column=1).value, "I001")
        self.assertEqual(ws.cell(row=4, column=2).value, "a004")
        self.assertEqual(ws.cell(row=4, column=3).value, "(4, 1)")
        self.assertEqual(ws.cell(row=4, column=4).value, "(4, 2)")
        self.assertEqual(ws.cell(row=4, column=5).value, "(4, 3)")
        self.assertEqual(ws.cell(row=4, column=6).value, "(4, 4)")
        self.assertEqual(ws.cell(row=4, column=7).value, "(4, 5)")
        self.assertEqual(ws.cell(row=4, column=8).value, "(4, 6)")

    def test_save_rep_setup_instructions_inducer_wells_1(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Create inducer for plate
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.set_gradient(min=1e-6, max=1e-3, n=24, scale='log')
        p.apply_inducer(iptg, apply_to='wells')
        # Run save_rep_setup_instructions
        p.save_rep_setup_instructions(file_name=os.path.join(self.temp_dir,
                                                             'plate_rep.xlsx'))
        # Load spreadsheet
        wb = openpyxl.load_workbook(filename=os.path.join(self.temp_dir,
                                                          'plate_rep.xlsx'))
        # Spreadsheet should contain one sheet
        self.assertEqual(wb.sheetnames, ["Inducers for Plate P1"])
        # Check inducer inoculation instructions
        ws = wb.get_sheet_by_name("Inducers for Plate P1")
        self.assertEqual(ws.cell(row=1, column=1).value, "(1, 1)\nI001")
        self.assertEqual(ws.cell(row=1, column=2).value, "(1, 2)\nI002")
        self.assertEqual(ws.cell(row=1, column=3).value, "(1, 3)\nI003")
        self.assertEqual(ws.cell(row=1, column=4).value, "(1, 4)\nI004")
        self.assertEqual(ws.cell(row=1, column=5).value, "(1, 5)\nI005")
        self.assertEqual(ws.cell(row=1, column=6).value, "(1, 6)\nI006")
        self.assertEqual(ws.cell(row=2, column=1).value, "(2, 1)\nI007")
        self.assertEqual(ws.cell(row=2, column=2).value, "(2, 2)\nI008")
        self.assertEqual(ws.cell(row=2, column=3).value, "(2, 3)\nI009")
        self.assertEqual(ws.cell(row=2, column=4).value, "(2, 4)\nI010")
        self.assertEqual(ws.cell(row=2, column=5).value, "(2, 5)\nI011")
        self.assertEqual(ws.cell(row=2, column=6).value, "(2, 6)\nI012")
        self.assertEqual(ws.cell(row=3, column=1).value, "(3, 1)\nI013")
        self.assertEqual(ws.cell(row=3, column=2).value, "(3, 2)\nI014")
        self.assertEqual(ws.cell(row=3, column=3).value, "(3, 3)\nI015")
        self.assertEqual(ws.cell(row=3, column=4).value, "(3, 4)\nI016")
        self.assertEqual(ws.cell(row=3, column=5).value, "(3, 5)\nI017")
        self.assertEqual(ws.cell(row=3, column=6).value, "(3, 6)\nI018")
        self.assertEqual(ws.cell(row=4, column=1).value, "(4, 1)\nI019")
        self.assertEqual(ws.cell(row=4, column=2).value, "(4, 2)\nI020")
        self.assertEqual(ws.cell(row=4, column=3).value, "(4, 3)\nI021")
        self.assertEqual(ws.cell(row=4, column=4).value, "(4, 4)\nI022")
        self.assertEqual(ws.cell(row=4, column=5).value, "(4, 5)\nI023")
        self.assertEqual(ws.cell(row=4, column=6).value, "(4, 6)\nI024")

    def test_save_rep_setup_instructions_inducer_wells_2(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Create inducer for plate
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.set_gradient(min=1e-6, max=1e-3, n=24, scale='log')
        p.apply_inducer(iptg, apply_to='wells')
        # Create second inducer for plate
        atc = platedesign.inducer.ChemicalInducer(
            name='aTc',
            units=u'ng/µL')
        atc.set_gradient(min=0.5, max=50, n=24, scale='log')
        p.apply_inducer(atc, apply_to='wells')
        # Run save_rep_setup_instructions
        p.save_rep_setup_instructions(file_name=os.path.join(self.temp_dir,
                                                             'plate_rep.xlsx'))
        # Load spreadsheet
        wb = openpyxl.load_workbook(filename=os.path.join(self.temp_dir,
                                                          'plate_rep.xlsx'))
        # Spreadsheet should contain one sheet
        self.assertEqual(wb.sheetnames, ["Inducers for Plate P1"])
        # Check inducer inoculation instructions
        ws = wb.get_sheet_by_name("Inducers for Plate P1")
        self.assertEqual(ws.cell(row=1, column=1).value, "(1, 1)\nI001\na001")
        self.assertEqual(ws.cell(row=1, column=2).value, "(1, 2)\nI002\na002")
        self.assertEqual(ws.cell(row=1, column=3).value, "(1, 3)\nI003\na003")
        self.assertEqual(ws.cell(row=1, column=4).value, "(1, 4)\nI004\na004")
        self.assertEqual(ws.cell(row=1, column=5).value, "(1, 5)\nI005\na005")
        self.assertEqual(ws.cell(row=1, column=6).value, "(1, 6)\nI006\na006")
        self.assertEqual(ws.cell(row=2, column=1).value, "(2, 1)\nI007\na007")
        self.assertEqual(ws.cell(row=2, column=2).value, "(2, 2)\nI008\na008")
        self.assertEqual(ws.cell(row=2, column=3).value, "(2, 3)\nI009\na009")
        self.assertEqual(ws.cell(row=2, column=4).value, "(2, 4)\nI010\na010")
        self.assertEqual(ws.cell(row=2, column=5).value, "(2, 5)\nI011\na011")
        self.assertEqual(ws.cell(row=2, column=6).value, "(2, 6)\nI012\na012")
        self.assertEqual(ws.cell(row=3, column=1).value, "(3, 1)\nI013\na013")
        self.assertEqual(ws.cell(row=3, column=2).value, "(3, 2)\nI014\na014")
        self.assertEqual(ws.cell(row=3, column=3).value, "(3, 3)\nI015\na015")
        self.assertEqual(ws.cell(row=3, column=4).value, "(3, 4)\nI016\na016")
        self.assertEqual(ws.cell(row=3, column=5).value, "(3, 5)\nI017\na017")
        self.assertEqual(ws.cell(row=3, column=6).value, "(3, 6)\nI018\na018")
        self.assertEqual(ws.cell(row=4, column=1).value, "(4, 1)\nI019\na019")
        self.assertEqual(ws.cell(row=4, column=2).value, "(4, 2)\nI020\na020")
        self.assertEqual(ws.cell(row=4, column=3).value, "(4, 3)\nI021\na021")
        self.assertEqual(ws.cell(row=4, column=4).value, "(4, 4)\nI022\na022")
        self.assertEqual(ws.cell(row=4, column=5).value, "(4, 5)\nI023\na023")
        self.assertEqual(ws.cell(row=4, column=6).value, "(4, 6)\nI024\na024")

    def test_save_rep_setup_instructions_inducer_wells_3(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.samples_to_measure = 12
        # Create inducer for plate
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set concentrations from gradient
        iptg.set_gradient(min=1e-6, max=1e-3, n=12, scale='log')
        # Apply inducer to plate
        p.apply_inducer(iptg, apply_to='wells')
        # Run save_rep_setup_instructions
        p.save_rep_setup_instructions(file_name=os.path.join(self.temp_dir,
                                                             'plate_rep.xlsx'))
        # Load spreadsheet
        wb = openpyxl.load_workbook(filename=os.path.join(self.temp_dir,
                                                          'plate_rep.xlsx'))
        # Spreadsheet should contain one sheet
        self.assertEqual(wb.sheetnames, ["Inducers for Plate P1"])
        # Check inducer inoculation instructions
        ws = wb.get_sheet_by_name("Inducers for Plate P1")
        self.assertEqual(ws.cell(row=1, column=1).value, "(1, 1)\nI001")
        self.assertEqual(ws.cell(row=1, column=2).value, "(1, 2)\nI002")
        self.assertEqual(ws.cell(row=1, column=3).value, "(1, 3)\nI003")
        self.assertEqual(ws.cell(row=1, column=4).value, "(1, 4)\nI004")
        self.assertEqual(ws.cell(row=1, column=5).value, "(1, 5)\nI005")
        self.assertEqual(ws.cell(row=1, column=6).value, "(1, 6)\nI006")
        self.assertEqual(ws.cell(row=2, column=1).value, "(2, 1)\nI007")
        self.assertEqual(ws.cell(row=2, column=2).value, "(2, 2)\nI008")
        self.assertEqual(ws.cell(row=2, column=3).value, "(2, 3)\nI009")
        self.assertEqual(ws.cell(row=2, column=4).value, "(2, 4)\nI010")
        self.assertEqual(ws.cell(row=2, column=5).value, "(2, 5)\nI011")
        self.assertEqual(ws.cell(row=2, column=6).value, "(2, 6)\nI012")
        self.assertEqual(ws.cell(row=3, column=1).value, "(3, 1)")
        self.assertEqual(ws.cell(row=3, column=2).value, "(3, 2)")
        self.assertEqual(ws.cell(row=3, column=3).value, "(3, 3)")
        self.assertEqual(ws.cell(row=3, column=4).value, "(3, 4)")
        self.assertEqual(ws.cell(row=3, column=5).value, "(3, 5)")
        self.assertEqual(ws.cell(row=3, column=6).value, "(3, 6)")
        self.assertEqual(ws.cell(row=4, column=1).value, "(4, 1)")
        self.assertEqual(ws.cell(row=4, column=2).value, "(4, 2)")
        self.assertEqual(ws.cell(row=4, column=3).value, "(4, 3)")
        self.assertEqual(ws.cell(row=4, column=4).value, "(4, 4)")
        self.assertEqual(ws.cell(row=4, column=5).value, "(4, 5)")
        self.assertEqual(ws.cell(row=4, column=6).value, "(4, 6)")

    def test_save_rep_setup_instructions_inducer_wells_4(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Create inducer for plate
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.set_gradient(min=1e-6, max=1e-3, n=24, scale='log')
        iptg.shuffle()
        p.apply_inducer(iptg, apply_to='wells')
        # Create second inducer for plate
        atc = platedesign.inducer.ChemicalInducer(
            name='aTc',
            units=u'ng/µL')
        atc.set_gradient(min=0.5, max=50, n=24, scale='log')
        p.apply_inducer(atc, apply_to='wells')
        # Run save_rep_setup_instructions
        p.save_rep_setup_instructions(file_name=os.path.join(self.temp_dir,
                                                             'plate_rep.xlsx'))
        # Load spreadsheet
        wb = openpyxl.load_workbook(filename=os.path.join(self.temp_dir,
                                                          'plate_rep.xlsx'))
        # Spreadsheet should contain one sheet
        self.assertEqual(wb.sheetnames, ["Inducers for Plate P1"])
        # Check inducer inoculation instructions
        ws = wb.get_sheet_by_name("Inducers for Plate P1")
        self.assertEqual(ws.cell(row=1, column=1).value, "(1, 1)\nI024\na001")
        self.assertEqual(ws.cell(row=1, column=2).value, "(1, 2)\nI003\na002")
        self.assertEqual(ws.cell(row=1, column=3).value, "(1, 3)\nI008\na003")
        self.assertEqual(ws.cell(row=1, column=4).value, "(1, 4)\nI022\na004")
        self.assertEqual(ws.cell(row=1, column=5).value, "(1, 5)\nI011\na005")
        self.assertEqual(ws.cell(row=1, column=6).value, "(1, 6)\nI013\na006")
        self.assertEqual(ws.cell(row=2, column=1).value, "(2, 1)\nI019\na007")
        self.assertEqual(ws.cell(row=2, column=2).value, "(2, 2)\nI016\na008")
        self.assertEqual(ws.cell(row=2, column=3).value, "(2, 3)\nI007\na009")
        self.assertEqual(ws.cell(row=2, column=4).value, "(2, 4)\nI005\na010")
        self.assertEqual(ws.cell(row=2, column=5).value, "(2, 5)\nI015\na011")
        self.assertEqual(ws.cell(row=2, column=6).value, "(2, 6)\nI023\na012")
        self.assertEqual(ws.cell(row=3, column=1).value, "(3, 1)\nI021\na013")
        self.assertEqual(ws.cell(row=3, column=2).value, "(3, 2)\nI018\na014")
        self.assertEqual(ws.cell(row=3, column=3).value, "(3, 3)\nI001\na015")
        self.assertEqual(ws.cell(row=3, column=4).value, "(3, 4)\nI002\na016")
        self.assertEqual(ws.cell(row=3, column=5).value, "(3, 5)\nI014\na017")
        self.assertEqual(ws.cell(row=3, column=6).value, "(3, 6)\nI012\na018")
        self.assertEqual(ws.cell(row=4, column=1).value, "(4, 1)\nI009\na019")
        self.assertEqual(ws.cell(row=4, column=2).value, "(4, 2)\nI010\na020")
        self.assertEqual(ws.cell(row=4, column=3).value, "(4, 3)\nI006\na021")
        self.assertEqual(ws.cell(row=4, column=4).value, "(4, 4)\nI017\na022")
        self.assertEqual(ws.cell(row=4, column=5).value, "(4, 5)\nI020\na023")
        self.assertEqual(ws.cell(row=4, column=6).value, "(4, 6)\nI004\na024")

    def test_save_rep_setup_instructions_inducer_media_1(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Create inducer for plate
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.shot_vol = 5.
        # Set single concentration
        iptg.concentrations = [12]
        # Apply inducer to plate
        p.apply_inducer(iptg, apply_to='media')
        # Run save_rep_setup_instructions
        p.save_rep_setup_instructions(file_name=os.path.join(self.temp_dir,
                                                             'plate_rep.xlsx'))
        # Load spreadsheet
        wb = openpyxl.load_workbook(filename=os.path.join(self.temp_dir,
                                                          'plate_rep.xlsx'))
        # Spreadsheet should contain one sheet
        self.assertEqual(wb.sheetnames, ["Inducers for Plate P1"])
        # Check inducer inoculation instructions
        ws = wb.get_sheet_by_name("Inducers for Plate P1")
        self.assertEqual(ws.cell(row=1, column=1).value, "(1, 1)")
        self.assertEqual(ws.cell(row=1, column=2).value, "(1, 2)")
        self.assertEqual(ws.cell(row=1, column=3).value, "(1, 3)")
        self.assertEqual(ws.cell(row=1, column=4).value, "(1, 4)")
        self.assertEqual(ws.cell(row=1, column=5).value, "(1, 5)")
        self.assertEqual(ws.cell(row=1, column=6).value, "(1, 6)")
        self.assertEqual(ws.cell(row=2, column=1).value, "(2, 1)")
        self.assertEqual(ws.cell(row=2, column=2).value, "(2, 2)")
        self.assertEqual(ws.cell(row=2, column=3).value, "(2, 3)")
        self.assertEqual(ws.cell(row=2, column=4).value, "(2, 4)")
        self.assertEqual(ws.cell(row=2, column=5).value, "(2, 5)")
        self.assertEqual(ws.cell(row=2, column=6).value, "(2, 6)")
        self.assertEqual(ws.cell(row=3, column=1).value, "(3, 1)")
        self.assertEqual(ws.cell(row=3, column=2).value, "(3, 2)")
        self.assertEqual(ws.cell(row=3, column=3).value, "(3, 3)")
        self.assertEqual(ws.cell(row=3, column=4).value, "(3, 4)")
        self.assertEqual(ws.cell(row=3, column=5).value, "(3, 5)")
        self.assertEqual(ws.cell(row=3, column=6).value, "(3, 6)")
        self.assertEqual(ws.cell(row=4, column=1).value, "(4, 1)")
        self.assertEqual(ws.cell(row=4, column=2).value, "(4, 2)")
        self.assertEqual(ws.cell(row=4, column=3).value, "(4, 3)")
        self.assertEqual(ws.cell(row=4, column=4).value, "(4, 4)")
        self.assertEqual(ws.cell(row=4, column=5).value, "(4, 5)")
        self.assertEqual(ws.cell(row=4, column=6).value, "(4, 6)")
        self.assertEqual(ws.cell(row=6, column=1).value,
                         u"Add 5.00µL of IPTG to media")

    def test_save_rep_setup_instructions_inducer_media_2(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Create inducer for plate
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.shot_vol = 5.
        # Set single concentration
        iptg.concentrations = [12]
        # Apply inducer to plate
        p.apply_inducer(iptg, apply_to='media')
        # Create inducer for plate
        atc = platedesign.inducer.ChemicalInducer(
            name='aTc',
            units=u'ng/µL')
        atc.shot_vol = 10.
        # Set single concentration
        atc.concentrations = [2]
        # Apply inducer to plate
        p.apply_inducer(atc, apply_to='media')
        # Run save_rep_setup_instructions
        p.save_rep_setup_instructions(file_name=os.path.join(self.temp_dir,
                                                             'plate_rep.xlsx'))
        # Load spreadsheet
        wb = openpyxl.load_workbook(filename=os.path.join(self.temp_dir,
                                                          'plate_rep.xlsx'))
        # Spreadsheet should contain one sheet
        self.assertEqual(wb.sheetnames, ["Inducers for Plate P1"])
        # Check inducer inoculation instructions
        ws = wb.get_sheet_by_name("Inducers for Plate P1")
        self.assertEqual(ws.cell(row=1, column=1).value, "(1, 1)")
        self.assertEqual(ws.cell(row=1, column=2).value, "(1, 2)")
        self.assertEqual(ws.cell(row=1, column=3).value, "(1, 3)")
        self.assertEqual(ws.cell(row=1, column=4).value, "(1, 4)")
        self.assertEqual(ws.cell(row=1, column=5).value, "(1, 5)")
        self.assertEqual(ws.cell(row=1, column=6).value, "(1, 6)")
        self.assertEqual(ws.cell(row=2, column=1).value, "(2, 1)")
        self.assertEqual(ws.cell(row=2, column=2).value, "(2, 2)")
        self.assertEqual(ws.cell(row=2, column=3).value, "(2, 3)")
        self.assertEqual(ws.cell(row=2, column=4).value, "(2, 4)")
        self.assertEqual(ws.cell(row=2, column=5).value, "(2, 5)")
        self.assertEqual(ws.cell(row=2, column=6).value, "(2, 6)")
        self.assertEqual(ws.cell(row=3, column=1).value, "(3, 1)")
        self.assertEqual(ws.cell(row=3, column=2).value, "(3, 2)")
        self.assertEqual(ws.cell(row=3, column=3).value, "(3, 3)")
        self.assertEqual(ws.cell(row=3, column=4).value, "(3, 4)")
        self.assertEqual(ws.cell(row=3, column=5).value, "(3, 5)")
        self.assertEqual(ws.cell(row=3, column=6).value, "(3, 6)")
        self.assertEqual(ws.cell(row=4, column=1).value, "(4, 1)")
        self.assertEqual(ws.cell(row=4, column=2).value, "(4, 2)")
        self.assertEqual(ws.cell(row=4, column=3).value, "(4, 3)")
        self.assertEqual(ws.cell(row=4, column=4).value, "(4, 4)")
        self.assertEqual(ws.cell(row=4, column=5).value, "(4, 5)")
        self.assertEqual(ws.cell(row=4, column=6).value, "(4, 6)")
        self.assertEqual(ws.cell(row=6, column=1).value,
                         u"Add 5.00µL of IPTG to media")
        self.assertEqual(ws.cell(row=7, column=1).value,
                         u"Add 10.00µL of aTc to media")

    def test_save_rep_setup_instructions_inducer_mixed_1(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')

        # Create inducer for plate rows
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set concentrations from gradient
        iptg.set_gradient(min=1e-6, max=1e-3, n=6, scale='log')
        # Apply inducer to plate
        p.apply_inducer(iptg, apply_to='rows')

        # Create second inducer for plate columns
        atc = platedesign.inducer.ChemicalInducer(
            name='aTc',
            units=u'ng/µL')
        # Set concentrations from gradient
        atc.set_gradient(min=0.5, max=50, n=4, scale='log')
        # Apply inducer to plate
        p.apply_inducer(atc, apply_to='cols')

        # Create inducer for plate wells
        xyl = platedesign.inducer.ChemicalInducer(
            name='Xylose',
            units=u'%')
        # Set concentrations from gradient
        xyl.set_gradient(min=1e-6, max=1e-3, n=24, scale='log')
        # Apply inducer to plate
        p.apply_inducer(xyl, apply_to='wells')

        # Create inducer for plate
        sugar = platedesign.inducer.ChemicalInducer(
            name='Sugar',
            units=u'ng/µL')
        sugar.shot_vol = 10.
        # Set single concentration
        sugar.concentrations = [2]
        # Apply inducer to plate
        p.apply_inducer(sugar, apply_to='media')
        # Run save_rep_setup_instructions
        p.save_rep_setup_instructions(file_name=os.path.join(self.temp_dir,
                                                             'plate_rep.xlsx'))
        # Load spreadsheet
        wb = openpyxl.load_workbook(filename=os.path.join(self.temp_dir,
                                                          'plate_rep.xlsx'))
        # Spreadsheet should contain one sheet
        self.assertEqual(wb.sheetnames, ["Inducers for Plate P1"])
        # Check inducer inoculation instructions
        ws = wb.get_sheet_by_name("Inducers for Plate P1")
        self.assertEqual(ws.cell(row=1, column=1).value, None)
        self.assertEqual(ws.cell(row=1, column=2).value, "I001")
        self.assertEqual(ws.cell(row=1, column=3).value, "I002")
        self.assertEqual(ws.cell(row=1, column=4).value, "I003")
        self.assertEqual(ws.cell(row=1, column=5).value, "I004")
        self.assertEqual(ws.cell(row=1, column=6).value, "I005")
        self.assertEqual(ws.cell(row=1, column=7).value, "I006")
        self.assertEqual(ws.cell(row=2, column=1).value, "a001")
        self.assertEqual(ws.cell(row=2, column=2).value, "(1, 1)\nX001")
        self.assertEqual(ws.cell(row=2, column=3).value, "(1, 2)\nX002")
        self.assertEqual(ws.cell(row=2, column=4).value, "(1, 3)\nX003")
        self.assertEqual(ws.cell(row=2, column=5).value, "(1, 4)\nX004")
        self.assertEqual(ws.cell(row=2, column=6).value, "(1, 5)\nX005")
        self.assertEqual(ws.cell(row=2, column=7).value, "(1, 6)\nX006")
        self.assertEqual(ws.cell(row=3, column=1).value, "a002")
        self.assertEqual(ws.cell(row=3, column=2).value, "(2, 1)\nX007")
        self.assertEqual(ws.cell(row=3, column=3).value, "(2, 2)\nX008")
        self.assertEqual(ws.cell(row=3, column=4).value, "(2, 3)\nX009")
        self.assertEqual(ws.cell(row=3, column=5).value, "(2, 4)\nX010")
        self.assertEqual(ws.cell(row=3, column=6).value, "(2, 5)\nX011")
        self.assertEqual(ws.cell(row=3, column=7).value, "(2, 6)\nX012")
        self.assertEqual(ws.cell(row=4, column=1).value, "a003")
        self.assertEqual(ws.cell(row=4, column=2).value, "(3, 1)\nX013")
        self.assertEqual(ws.cell(row=4, column=3).value, "(3, 2)\nX014")
        self.assertEqual(ws.cell(row=4, column=4).value, "(3, 3)\nX015")
        self.assertEqual(ws.cell(row=4, column=5).value, "(3, 4)\nX016")
        self.assertEqual(ws.cell(row=4, column=6).value, "(3, 5)\nX017")
        self.assertEqual(ws.cell(row=4, column=7).value, "(3, 6)\nX018")
        self.assertEqual(ws.cell(row=5, column=1).value, "a004")
        self.assertEqual(ws.cell(row=5, column=2).value, "(4, 1)\nX019")
        self.assertEqual(ws.cell(row=5, column=3).value, "(4, 2)\nX020")
        self.assertEqual(ws.cell(row=5, column=4).value, "(4, 3)\nX021")
        self.assertEqual(ws.cell(row=5, column=5).value, "(4, 4)\nX022")
        self.assertEqual(ws.cell(row=5, column=6).value, "(4, 5)\nX023")
        self.assertEqual(ws.cell(row=5, column=7).value, "(4, 6)\nX024")
        self.assertEqual(ws.cell(row=7, column=1).value,
                         u"Add 10.00µL of Sugar to media")

    def test_save_rep_setup_instructions_cells_and_inducer(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.total_media_vol = 15000.
        # Add some information for cell setup
        p.cell_strain_name = 'Test strain 1'
        p.cell_setup_method = 'fixed_od600'
        p.cell_predilution = 100
        p.cell_predilution_vol = 1000
        p.cell_initial_od600 = 1e-5

        # Create inducer for plate rows
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set concentrations from gradient
        iptg.set_gradient(min=1e-6, max=1e-3, n=6, scale='log')
        # Apply inducer to plate
        p.apply_inducer(iptg, apply_to='rows')

        # Create second inducer for plate columns
        atc = platedesign.inducer.ChemicalInducer(
            name='aTc',
            units=u'ng/µL')
        # Set concentrations from gradient
        atc.set_gradient(min=0.5, max=50, n=4, scale='log')
        # Apply inducer to plate
        p.apply_inducer(atc, apply_to='cols')

        # Create inducer for plate wells
        xyl = platedesign.inducer.ChemicalInducer(
            name='Xylose',
            units=u'%')
        # Set concentrations from gradient
        xyl.set_gradient(min=1e-6, max=1e-3, n=24, scale='log')
        # Apply inducer to plate
        p.apply_inducer(xyl, apply_to='wells')

        # Create inducer for plate
        sugar = platedesign.inducer.ChemicalInducer(
            name='Sugar',
            units=u'ng/µL')
        sugar.shot_vol = 10.
        # Set single concentration
        sugar.concentrations = [2]
        # Apply inducer to plate
        p.apply_inducer(sugar, apply_to='media')
        # Run save_rep_setup_instructions
        p.save_rep_setup_instructions(file_name=os.path.join(self.temp_dir,
                                                             'plate_rep.xlsx'))
        # Load spreadsheet
        wb = openpyxl.load_workbook(filename=os.path.join(self.temp_dir,
                                                          'plate_rep.xlsx'))
        # Check that sheet exists in spreadsheet
        self.assertTrue("Inducers for Plate P1" in wb.sheetnames)
        # Check inducer inoculation instructions
        ws = wb.get_sheet_by_name("Inducers for Plate P1")
        self.assertEqual(ws.cell(row=1, column=1).value, None)
        self.assertEqual(ws.cell(row=1, column=2).value, "I001")
        self.assertEqual(ws.cell(row=1, column=3).value, "I002")
        self.assertEqual(ws.cell(row=1, column=4).value, "I003")
        self.assertEqual(ws.cell(row=1, column=5).value, "I004")
        self.assertEqual(ws.cell(row=1, column=6).value, "I005")
        self.assertEqual(ws.cell(row=1, column=7).value, "I006")
        self.assertEqual(ws.cell(row=2, column=1).value, "a001")
        self.assertEqual(ws.cell(row=2, column=2).value, "(1, 1)\nX001")
        self.assertEqual(ws.cell(row=2, column=3).value, "(1, 2)\nX002")
        self.assertEqual(ws.cell(row=2, column=4).value, "(1, 3)\nX003")
        self.assertEqual(ws.cell(row=2, column=5).value, "(1, 4)\nX004")
        self.assertEqual(ws.cell(row=2, column=6).value, "(1, 5)\nX005")
        self.assertEqual(ws.cell(row=2, column=7).value, "(1, 6)\nX006")
        self.assertEqual(ws.cell(row=3, column=1).value, "a002")
        self.assertEqual(ws.cell(row=3, column=2).value, "(2, 1)\nX007")
        self.assertEqual(ws.cell(row=3, column=3).value, "(2, 2)\nX008")
        self.assertEqual(ws.cell(row=3, column=4).value, "(2, 3)\nX009")
        self.assertEqual(ws.cell(row=3, column=5).value, "(2, 4)\nX010")
        self.assertEqual(ws.cell(row=3, column=6).value, "(2, 5)\nX011")
        self.assertEqual(ws.cell(row=3, column=7).value, "(2, 6)\nX012")
        self.assertEqual(ws.cell(row=4, column=1).value, "a003")
        self.assertEqual(ws.cell(row=4, column=2).value, "(3, 1)\nX013")
        self.assertEqual(ws.cell(row=4, column=3).value, "(3, 2)\nX014")
        self.assertEqual(ws.cell(row=4, column=4).value, "(3, 3)\nX015")
        self.assertEqual(ws.cell(row=4, column=5).value, "(3, 4)\nX016")
        self.assertEqual(ws.cell(row=4, column=6).value, "(3, 5)\nX017")
        self.assertEqual(ws.cell(row=4, column=7).value, "(3, 6)\nX018")
        self.assertEqual(ws.cell(row=5, column=1).value, "a004")
        self.assertEqual(ws.cell(row=5, column=2).value, "(4, 1)\nX019")
        self.assertEqual(ws.cell(row=5, column=3).value, "(4, 2)\nX020")
        self.assertEqual(ws.cell(row=5, column=4).value, "(4, 3)\nX021")
        self.assertEqual(ws.cell(row=5, column=5).value, "(4, 4)\nX022")
        self.assertEqual(ws.cell(row=5, column=6).value, "(4, 5)\nX023")
        self.assertEqual(ws.cell(row=5, column=7).value, "(4, 6)\nX024")
        self.assertEqual(ws.cell(row=7, column=1).value,
                         u"Add 10.00µL of Sugar to media")

        # Check that sheet exists in spreadsheet
        self.assertTrue("Cells for Plate P1" in wb.sheetnames)
        # Check cell inoculation instructions
        ws = wb.get_sheet_by_name("Cells for Plate P1")
        self.assertEqual(ws.cell(row=1, column=1).value, "Strain Name")
        self.assertEqual(ws.cell(row=1, column=2).value, "Test strain 1")
        self.assertTrue('A2:C2' in ws.merged_cell_ranges)
        self.assertEqual(ws.cell(row=2, column=1).value, "Predilution")
        self.assertEqual(ws.cell(row=3, column=1).value, "Predilution factor")
        self.assertEqual(ws.cell(row=3, column=2).value, 100)
        self.assertEqual(ws.cell(row=3, column=3).value, "x")
        self.assertEqual(ws.cell(row=4, column=1).value, "Media volume")
        self.assertEqual(ws.cell(row=4, column=2).value, 990)
        self.assertEqual(ws.cell(row=4, column=3).value, u"µL")
        self.assertEqual(ws.cell(row=5, column=1).value, "Preculture volume")
        self.assertEqual(ws.cell(row=5, column=2).value, 10)
        self.assertEqual(ws.cell(row=5, column=3).value, u"µL")
        self.assertEqual(ws.cell(row=6, column=1).value, "Predilution OD600")
        self.assertEqual(ws.cell(row=6, column=2).value, None)
        self.assertEqual(ws.cell(row=6, column=3).value, None)
        self.assertTrue('A7:C7' in ws.merged_cell_ranges)
        self.assertEqual(ws.cell(row=7, column=1).value, "Inoculation")
        self.assertEqual(ws.cell(row=8, column=1).value, "Target OD600")
        self.assertEqual(ws.cell(row=8, column=2).value, 1e-5)
        self.assertEqual(ws.cell(row=8, column=3).value, None)
        self.assertEqual(ws.cell(row=9, column=1).value, "Predilution volume")
        self.assertEqual(ws.cell(row=9, column=2).value, "=0.15/B6")
        self.assertEqual(ws.cell(row=9, column=3).value, u"µL")
        self.assertEqual(ws.cell(row=10, column=1).value, "Add into 15.00mL "
            "media, and distribute into plate wells.")

    def test_save_rep_setup_instructions_cells_and_inducer_workbook(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.total_media_vol = 15000.
        # Add some information for cell setup
        p.cell_strain_name = 'Test strain 1'
        p.cell_setup_method = 'fixed_od600'
        p.cell_predilution = 100
        p.cell_predilution_vol = 1000
        p.cell_initial_od600 = 1e-5

        # Create inducer for plate rows
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set concentrations from gradient
        iptg.set_gradient(min=1e-6, max=1e-3, n=6, scale='log')
        # Apply inducer to plate
        p.apply_inducer(iptg, apply_to='rows')

        # Create second inducer for plate columns
        atc = platedesign.inducer.ChemicalInducer(
            name='aTc',
            units=u'ng/µL')
        # Set concentrations from gradient
        atc.set_gradient(min=0.5, max=50, n=4, scale='log')
        # Apply inducer to plate
        p.apply_inducer(atc, apply_to='cols')

        # Create inducer for plate wells
        xyl = platedesign.inducer.ChemicalInducer(
            name='Xylose',
            units=u'%')
        # Set concentrations from gradient
        xyl.set_gradient(min=1e-6, max=1e-3, n=24, scale='log')
        # Apply inducer to plate
        p.apply_inducer(xyl, apply_to='wells')

        # Create inducer for plate
        sugar = platedesign.inducer.ChemicalInducer(
            name='Sugar',
            units=u'ng/µL')
        sugar.shot_vol = 10.
        # Set single concentration
        sugar.concentrations = [2]
        # Apply inducer to plate
        p.apply_inducer(sugar, apply_to='media')

        # Create new spreadsheet
        wb = openpyxl.Workbook()
        # Save instructions on existing spreadsheet
        p.save_rep_setup_instructions(workbook=wb)

        # Check that sheet exists in spreadsheet
        self.assertTrue("Inducers for Plate P1" in wb.sheetnames)
        # Check inducer inoculation instructions
        ws = wb.get_sheet_by_name("Inducers for Plate P1")
        self.assertEqual(ws.cell(row=1, column=1).value, "")
        self.assertEqual(ws.cell(row=1, column=2).value, "I001")
        self.assertEqual(ws.cell(row=1, column=3).value, "I002")
        self.assertEqual(ws.cell(row=1, column=4).value, "I003")
        self.assertEqual(ws.cell(row=1, column=5).value, "I004")
        self.assertEqual(ws.cell(row=1, column=6).value, "I005")
        self.assertEqual(ws.cell(row=1, column=7).value, "I006")
        self.assertEqual(ws.cell(row=2, column=1).value, "a001")
        self.assertEqual(ws.cell(row=2, column=2).value, "(1, 1)\nX001")
        self.assertEqual(ws.cell(row=2, column=3).value, "(1, 2)\nX002")
        self.assertEqual(ws.cell(row=2, column=4).value, "(1, 3)\nX003")
        self.assertEqual(ws.cell(row=2, column=5).value, "(1, 4)\nX004")
        self.assertEqual(ws.cell(row=2, column=6).value, "(1, 5)\nX005")
        self.assertEqual(ws.cell(row=2, column=7).value, "(1, 6)\nX006")
        self.assertEqual(ws.cell(row=3, column=1).value, "a002")
        self.assertEqual(ws.cell(row=3, column=2).value, "(2, 1)\nX007")
        self.assertEqual(ws.cell(row=3, column=3).value, "(2, 2)\nX008")
        self.assertEqual(ws.cell(row=3, column=4).value, "(2, 3)\nX009")
        self.assertEqual(ws.cell(row=3, column=5).value, "(2, 4)\nX010")
        self.assertEqual(ws.cell(row=3, column=6).value, "(2, 5)\nX011")
        self.assertEqual(ws.cell(row=3, column=7).value, "(2, 6)\nX012")
        self.assertEqual(ws.cell(row=4, column=1).value, "a003")
        self.assertEqual(ws.cell(row=4, column=2).value, "(3, 1)\nX013")
        self.assertEqual(ws.cell(row=4, column=3).value, "(3, 2)\nX014")
        self.assertEqual(ws.cell(row=4, column=4).value, "(3, 3)\nX015")
        self.assertEqual(ws.cell(row=4, column=5).value, "(3, 4)\nX016")
        self.assertEqual(ws.cell(row=4, column=6).value, "(3, 5)\nX017")
        self.assertEqual(ws.cell(row=4, column=7).value, "(3, 6)\nX018")
        self.assertEqual(ws.cell(row=5, column=1).value, "a004")
        self.assertEqual(ws.cell(row=5, column=2).value, "(4, 1)\nX019")
        self.assertEqual(ws.cell(row=5, column=3).value, "(4, 2)\nX020")
        self.assertEqual(ws.cell(row=5, column=4).value, "(4, 3)\nX021")
        self.assertEqual(ws.cell(row=5, column=5).value, "(4, 4)\nX022")
        self.assertEqual(ws.cell(row=5, column=6).value, "(4, 5)\nX023")
        self.assertEqual(ws.cell(row=5, column=7).value, "(4, 6)\nX024")
        self.assertEqual(ws.cell(row=7, column=1).value,
                         u"Add 10.00µL of Sugar to media")

        # Check that sheet exists in spreadsheet
        self.assertTrue("Cells for Plate P1" in wb.sheetnames)
        # Check cell inoculation instructions
        ws = wb.get_sheet_by_name("Cells for Plate P1")
        self.assertEqual(ws.cell(row=1, column=1).value, "Strain Name")
        self.assertEqual(ws.cell(row=1, column=2).value, "Test strain 1")
        self.assertTrue('A2:C2' in ws.merged_cell_ranges)
        self.assertEqual(ws.cell(row=2, column=1).value, "Predilution")
        self.assertEqual(ws.cell(row=3, column=1).value, "Predilution factor")
        self.assertEqual(ws.cell(row=3, column=2).value, 100)
        self.assertEqual(ws.cell(row=3, column=3).value, "x")
        self.assertEqual(ws.cell(row=4, column=1).value, "Media volume")
        self.assertEqual(ws.cell(row=4, column=2).value, 990)
        self.assertEqual(ws.cell(row=4, column=3).value, u"µL")
        self.assertEqual(ws.cell(row=5, column=1).value, "Preculture volume")
        self.assertEqual(ws.cell(row=5, column=2).value, 10)
        self.assertEqual(ws.cell(row=5, column=3).value, u"µL")
        self.assertEqual(ws.cell(row=6, column=1).value, "Predilution OD600")
        self.assertEqual(ws.cell(row=6, column=2).value, None)
        self.assertEqual(ws.cell(row=6, column=3).value, None)
        self.assertTrue('A7:C7' in ws.merged_cell_ranges)
        self.assertEqual(ws.cell(row=7, column=1).value, "Inoculation")
        self.assertEqual(ws.cell(row=8, column=1).value, "Target OD600")
        self.assertEqual(ws.cell(row=8, column=2).value, 1e-5)
        self.assertEqual(ws.cell(row=8, column=3).value, None)
        self.assertEqual(ws.cell(row=9, column=1).value, "Predilution volume")
        self.assertEqual(ws.cell(row=9, column=2).value, "=0.15/B6")
        self.assertEqual(ws.cell(row=9, column=3).value, u"µL")
        self.assertEqual(ws.cell(row=10, column=1).value, "Add into 15.00mL "
            "media, and distribute into plate wells.")

    def test_save_rep_setup_instructions_argument_error(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Run save_rep_setup_instructions with no arguments
        self.assertRaises(ValueError, p.save_rep_setup_instructions)

    def test_save_rep_setup_files(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Check that save_rep_setup_files runs successfully
        p.save_rep_setup_files()
        # save_exp_setup_files does not do anything in Plate. There is no need
        # to check for results.

    def test_add_inducer_setup_instructions_sheet_error(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Create workbook
        wb = openpyxl.Workbook()
        # Add sheet
        wb.create_sheet("Test sheet")
        # Attempt to add cell setup instructions
        self.assertRaises(ValueError,
                          p.add_inducer_setup_instructions,
                          wb,
                          "Test sheet")

    def test_add_cell_setup_instructions_sheet_error(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Create workbook
        wb = openpyxl.Workbook()
        # Add sheet
        wb.create_sheet("Test sheet")
        # Attempt to add cell setup instructions
        self.assertRaises(ValueError,
                          p.add_cell_setup_instructions,
                          wb,
                          "Test sheet")

    def test_close_plates_no_inducer_no_cell_inoculation(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.cell_strain_name = 'Test strain 1'
        # Call close plates and check length of output
        cps = p.close_plates()
        self.assertEqual(len(cps), 1)
        # Get the only closed place
        cp = cps[0]
        # Check basic properties
        self.assertEqual(cp.name, 'P1')
        self.assertEqual(cp.n_rows, 4)
        self.assertEqual(cp.n_cols, 6)
        # Check plate info
        self.assertEqual(len(cp.plate_info), 1)
        self.assertTrue('Strain' in cp.plate_info)
        self.assertEqual(cp.plate_info['Strain'], 'Test strain 1')
        # Check well info
        well_info = pandas.DataFrame()
        well_info['Measure'] = [True]*24
        pandas.util.testing.assert_frame_equal(cp.well_info, well_info)

    def test_close_plates_metadata(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.cell_strain_name = 'Test strain 1'
        # Add some metadata
        p.metadata['Meta 1'] = 'Value 1'
        p.metadata['Meta 2'] = 'Value 2'
        # Call close plates and check length of output
        cps = p.close_plates()
        self.assertEqual(len(cps), 1)
        # Get the only closed place
        cp = cps[0]
        # Check basic properties
        self.assertEqual(cp.name, 'P1')
        self.assertEqual(cp.n_rows, 4)
        self.assertEqual(cp.n_cols, 6)
        # Check plate info
        self.assertEqual(len(cp.plate_info), 3)
        self.assertTrue('Strain' in cp.plate_info)
        self.assertEqual(cp.plate_info['Strain'], 'Test strain 1')
        self.assertTrue('Meta 1' in cp.plate_info)
        self.assertEqual(cp.plate_info['Meta 1'], 'Value 1')
        self.assertTrue('Meta 2' in cp.plate_info)
        self.assertEqual(cp.plate_info['Meta 2'], 'Value 2')
        # Check well info
        well_info = pandas.DataFrame()
        well_info['Measure'] = [True]*24
        pandas.util.testing.assert_frame_equal(cp.well_info, well_info)

    def test_close_plates_cell_inoculation_1(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.cell_strain_name = 'Test strain 1'
        # Add cell inoculation info
        p.cell_setup_method = 'fixed_volume'
        p.cell_shot_vol = 5
        # Call close plates and check length of output
        cps = p.close_plates()
        self.assertEqual(len(cps), 1)
        # Get the only closed place
        cp = cps[0]
        # Check basic properties
        self.assertEqual(cp.name, 'P1')
        self.assertEqual(cp.n_rows, 4)
        self.assertEqual(cp.n_cols, 6)
        # Check plate info
        self.assertEqual(len(cp.plate_info), 3)
        self.assertTrue('Strain' in cp.plate_info)
        self.assertEqual(cp.plate_info['Strain'], 'Test strain 1')
        self.assertTrue('Preculture Dilution' in cp.plate_info)
        self.assertEqual(cp.plate_info['Preculture Dilution'], 1)
        self.assertTrue('Cell Inoculated Vol.' in cp.plate_info)
        self.assertEqual(cp.plate_info['Cell Inoculated Vol.'], 5)
        # Check well info
        well_info = pandas.DataFrame()
        well_info['Measure'] = [True]*24
        pandas.util.testing.assert_frame_equal(cp.well_info, well_info)

    def test_close_plates_cell_inoculation_2(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.cell_strain_name = 'Test strain 1'
        # Add cell inoculation info
        p.cell_setup_method = 'fixed_volume'
        p.cell_predilution = 100
        p.cell_predilution_vol = 1000
        p.cell_shot_vol = 5
        # Call close plates and check length of output
        cps = p.close_plates()
        self.assertEqual(len(cps), 1)
        # Get the only closed place
        cp = cps[0]
        # Check basic properties
        self.assertEqual(cp.name, 'P1')
        self.assertEqual(cp.n_rows, 4)
        self.assertEqual(cp.n_cols, 6)
        # Check plate info
        self.assertEqual(len(cp.plate_info), 3)
        self.assertTrue('Strain' in cp.plate_info)
        self.assertEqual(cp.plate_info['Strain'], 'Test strain 1')
        self.assertTrue('Preculture Dilution' in cp.plate_info)
        self.assertEqual(cp.plate_info['Preculture Dilution'], 100)
        self.assertTrue('Cell Inoculated Vol.' in cp.plate_info)
        self.assertEqual(cp.plate_info['Cell Inoculated Vol.'], 5)
        # Check well info
        well_info = pandas.DataFrame()
        well_info['Measure'] = [True]*24
        pandas.util.testing.assert_frame_equal(cp.well_info, well_info)

    def test_close_plates_cell_inoculation_3(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.cell_strain_name = 'Test strain 1'
        # Add cell inoculation info
        p.cell_setup_method = 'fixed_od600'
        p.cell_initial_od600 = 1e-5
        # Call close plates and check length of output
        cps = p.close_plates()
        self.assertEqual(len(cps), 1)
        # Get the only closed place
        cp = cps[0]
        # Check basic properties
        self.assertEqual(cp.name, 'P1')
        self.assertEqual(cp.n_rows, 4)
        self.assertEqual(cp.n_cols, 6)
        # Check plate info
        self.assertEqual(len(cp.plate_info), 3)
        self.assertTrue('Strain' in cp.plate_info)
        self.assertEqual(cp.plate_info['Strain'], 'Test strain 1')
        self.assertTrue('Preculture Dilution' in cp.plate_info)
        self.assertEqual(cp.plate_info['Preculture Dilution'], 1)
        self.assertTrue('Initial OD600' in cp.plate_info)
        self.assertEqual(cp.plate_info['Initial OD600'], 1e-5)
        # Check well info
        well_info = pandas.DataFrame()
        well_info['Measure'] = [True]*24
        pandas.util.testing.assert_frame_equal(cp.well_info, well_info)

    def test_close_plates_cell_inoculation_4(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.cell_strain_name = 'Test strain 1'
        # Add cell inoculation info
        p.cell_setup_method = 'fixed_od600'
        p.cell_predilution = 100
        p.cell_predilution_vol = 1000
        p.cell_initial_od600 = 1e-5
        # Call close plates and check length of output
        cps = p.close_plates()
        self.assertEqual(len(cps), 1)
        # Get the only closed place
        cp = cps[0]
        # Check basic properties
        self.assertEqual(cp.name, 'P1')
        self.assertEqual(cp.n_rows, 4)
        self.assertEqual(cp.n_cols, 6)
        # Check plate info
        self.assertEqual(len(cp.plate_info), 3)
        self.assertTrue('Strain' in cp.plate_info)
        self.assertEqual(cp.plate_info['Strain'], 'Test strain 1')
        self.assertTrue('Preculture Dilution' in cp.plate_info)
        self.assertEqual(cp.plate_info['Preculture Dilution'], 100)
        self.assertTrue('Initial OD600' in cp.plate_info)
        self.assertEqual(cp.plate_info['Initial OD600'], 1e-5)
        # Check well info
        well_info = pandas.DataFrame()
        well_info['Measure'] = [True]*24
        pandas.util.testing.assert_frame_equal(cp.well_info, well_info)

    def test_close_plates_inducer_row_1(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.cell_strain_name = 'Test strain 1'

        # Create inducer for plate rows
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.concentrations = [3, 4, 5, 6, 7, 8]
        p.apply_inducer(iptg, apply_to='rows')

        # Call close plates and check length of output
        cps = p.close_plates()
        self.assertEqual(len(cps), 1)
        # Get the only closed place
        cp = cps[0]
        # Check basic properties
        self.assertEqual(cp.name, 'P1')
        self.assertEqual(cp.n_rows, 4)
        self.assertEqual(cp.n_cols, 6)
        # Check plate info
        self.assertEqual(len(cp.plate_info), 1)
        self.assertTrue('Strain' in cp.plate_info)
        self.assertEqual(cp.plate_info['Strain'], 'Test strain 1')
        # Check well info
        well_info = pandas.DataFrame()
        well_info[u'IPTG Concentration (µM)'] = [3., 4., 5., 6., 7., 8.,
                                                 3., 4., 5., 6., 7., 8.,
                                                 3., 4., 5., 6., 7., 8.,
                                                 3., 4., 5., 6., 7., 8.]
        well_info['Measure'] = [True]*24
        pandas.util.testing.assert_frame_equal(cp.well_info, well_info)

    def test_close_plates_inducer_row_2(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.cell_strain_name = 'Test strain 1'

        # Create inducer for plate rows
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.concentrations = [3, 4, 5, 6, 7, 8]
        p.apply_inducer(iptg, apply_to='rows')

        # Second inducer for plate rows
        atc = platedesign.inducer.ChemicalInducer(
            name='aTc',
            units=u'ng/µL')
        atc.concentrations = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        p.apply_inducer(atc, apply_to='rows')

        # Call close plates and check length of output
        cps = p.close_plates()
        self.assertEqual(len(cps), 1)
        # Get the only closed place
        cp = cps[0]
        # Check basic properties
        self.assertEqual(cp.name, 'P1')
        self.assertEqual(cp.n_rows, 4)
        self.assertEqual(cp.n_cols, 6)
        # Check plate info
        self.assertEqual(len(cp.plate_info), 1)
        self.assertTrue('Strain' in cp.plate_info)
        self.assertEqual(cp.plate_info['Strain'], 'Test strain 1')
        # Check well info
        well_info = pandas.DataFrame()
        well_info[u'IPTG Concentration (µM)'] = [3., 4., 5., 6., 7., 8.,
                                                 3., 4., 5., 6., 7., 8.,
                                                 3., 4., 5., 6., 7., 8.,
                                                 3., 4., 5., 6., 7., 8.]
        well_info[u'aTc Concentration (ng/µL)'] = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6,
                                                   0.1, 0.2, 0.3, 0.4, 0.5, 0.6,
                                                   0.1, 0.2, 0.3, 0.4, 0.5, 0.6,
                                                   0.1, 0.2, 0.3, 0.4, 0.5, 0.6,]
        well_info['Measure'] = [True]*24
        pandas.util.testing.assert_frame_equal(cp.well_info, well_info)

    def test_close_plates_inducer_row_3(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.cell_strain_name = 'Test strain 1'

        # Create inducer for plate rows
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.concentrations = [3, 4, 5, 6, 7, 8]
        iptg.shuffle()
        p.apply_inducer(iptg, apply_to='rows')

        # Second inducer for plate rows
        atc = platedesign.inducer.ChemicalInducer(
            name='aTc',
            units=u'ng/µL')
        atc.concentrations = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        p.apply_inducer(atc, apply_to='rows')

        # Call close plates and check length of output
        cps = p.close_plates()
        self.assertEqual(len(cps), 1)
        # Get the only closed place
        cp = cps[0]
        # Check basic properties
        self.assertEqual(cp.name, 'P1')
        self.assertEqual(cp.n_rows, 4)
        self.assertEqual(cp.n_cols, 6)
        # Check plate info
        self.assertEqual(len(cp.plate_info), 1)
        self.assertTrue('Strain' in cp.plate_info)
        self.assertEqual(cp.plate_info['Strain'], 'Test strain 1')
        # Check well info
        well_info = pandas.DataFrame()
        well_info[u'IPTG Concentration (µM)'] = [4., 5., 8., 6., 7., 3.,
                                                 4., 5., 8., 6., 7., 3.,
                                                 4., 5., 8., 6., 7., 3.,
                                                 4., 5., 8., 6., 7., 3.,]
        well_info[u'aTc Concentration (ng/µL)'] = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6,
                                                   0.1, 0.2, 0.3, 0.4, 0.5, 0.6,
                                                   0.1, 0.2, 0.3, 0.4, 0.5, 0.6,
                                                   0.1, 0.2, 0.3, 0.4, 0.5, 0.6,]
        well_info['Measure'] = [True]*24
        pandas.util.testing.assert_frame_equal(cp.well_info, well_info)

    def test_close_plates_inducer_col_1(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.cell_strain_name = 'Test strain 1'

        # Create inducer for plate columns
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.concentrations = [3, 4, 5, 6]
        p.apply_inducer(iptg, apply_to='cols')

        # Call close plates and check length of output
        cps = p.close_plates()
        self.assertEqual(len(cps), 1)
        # Get the only closed place
        cp = cps[0]
        # Check basic properties
        self.assertEqual(cp.name, 'P1')
        self.assertEqual(cp.n_rows, 4)
        self.assertEqual(cp.n_cols, 6)
        # Check plate info
        self.assertEqual(len(cp.plate_info), 1)
        self.assertTrue('Strain' in cp.plate_info)
        self.assertEqual(cp.plate_info['Strain'], 'Test strain 1')
        # Check well info
        well_info = pandas.DataFrame()
        well_info[u'IPTG Concentration (µM)'] = [3., 3., 3., 3., 3., 3.,
                                                 4., 4., 4., 4., 4., 4.,
                                                 5., 5., 5., 5., 5., 5.,
                                                 6., 6., 6., 6., 6., 6.,]
        well_info['Measure'] = [True]*24
        pandas.util.testing.assert_frame_equal(cp.well_info, well_info)

    def test_close_plates_inducer_col_2(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.cell_strain_name = 'Test strain 1'

        # Create inducer for plate columns
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.concentrations = [3, 4, 5, 6]
        p.apply_inducer(iptg, apply_to='cols')

        # Second inducer for plate columns
        atc = platedesign.inducer.ChemicalInducer(
            name='aTc',
            units=u'ng/µL')
        atc.concentrations = [0.1, 0.2, 0.3, 0.4]
        p.apply_inducer(atc, apply_to='cols')

        # Call close plates and check length of output
        cps = p.close_plates()
        self.assertEqual(len(cps), 1)
        # Get the only closed place
        cp = cps[0]
        # Check basic properties
        self.assertEqual(cp.name, 'P1')
        self.assertEqual(cp.n_rows, 4)
        self.assertEqual(cp.n_cols, 6)
        # Check plate info
        self.assertEqual(len(cp.plate_info), 1)
        self.assertTrue('Strain' in cp.plate_info)
        self.assertEqual(cp.plate_info['Strain'], 'Test strain 1')
        # Check well info
        well_info = pandas.DataFrame()
        well_info[u'IPTG Concentration (µM)'] = [3., 3., 3., 3., 3., 3.,
                                                 4., 4., 4., 4., 4., 4.,
                                                 5., 5., 5., 5., 5., 5.,
                                                 6., 6., 6., 6., 6., 6.,]
        well_info[u'aTc Concentration (ng/µL)'] = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1,
                                                   0.2, 0.2, 0.2, 0.2, 0.2, 0.2,
                                                   0.3, 0.3, 0.3, 0.3, 0.3, 0.3,
                                                   0.4, 0.4, 0.4, 0.4, 0.4, 0.4,]
        well_info['Measure'] = [True]*24
        pandas.util.testing.assert_frame_equal(cp.well_info, well_info)

    def test_close_plates_inducer_col_3(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.cell_strain_name = 'Test strain 1'

        # Create inducer for plate columns
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.concentrations = [3, 4, 5, 6]
        iptg.shuffle()
        p.apply_inducer(iptg, apply_to='cols')

        # Second inducer for plate columns
        atc = platedesign.inducer.ChemicalInducer(
            name='aTc',
            units=u'ng/µL')
        atc.concentrations = [0.1, 0.2, 0.3, 0.4]
        p.apply_inducer(atc, apply_to='cols')

        # Call close plates and check length of output
        cps = p.close_plates()
        self.assertEqual(len(cps), 1)
        # Get the only closed place
        cp = cps[0]
        # Check basic properties
        self.assertEqual(cp.name, 'P1')
        self.assertEqual(cp.n_rows, 4)
        self.assertEqual(cp.n_cols, 6)
        # Check plate info
        self.assertEqual(len(cp.plate_info), 1)
        self.assertTrue('Strain' in cp.plate_info)
        self.assertEqual(cp.plate_info['Strain'], 'Test strain 1')
        # Check well info
        well_info = pandas.DataFrame()
        well_info[u'IPTG Concentration (µM)'] = [6., 6., 6., 6., 6., 6.,
                                                 4., 4., 4., 4., 4., 4.,
                                                 5., 5., 5., 5., 5., 5.,
                                                 3., 3., 3., 3., 3., 3.,]
        well_info[u'aTc Concentration (ng/µL)'] = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1,
                                                   0.2, 0.2, 0.2, 0.2, 0.2, 0.2,
                                                   0.3, 0.3, 0.3, 0.3, 0.3, 0.3,
                                                   0.4, 0.4, 0.4, 0.4, 0.4, 0.4,]
        well_info['Measure'] = [True]*24
        pandas.util.testing.assert_frame_equal(cp.well_info, well_info)

    def test_close_plates_inducer_wells_1(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.cell_strain_name = 'Test strain 1'

        # Create inducer for plate
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.concentrations = numpy.arange(24) + 1
        p.apply_inducer(iptg, apply_to='wells')

        # Call close plates and check length of output
        cps = p.close_plates()
        self.assertEqual(len(cps), 1)
        # Get the only closed place
        cp = cps[0]
        # Check basic properties
        self.assertEqual(cp.name, 'P1')
        self.assertEqual(cp.n_rows, 4)
        self.assertEqual(cp.n_cols, 6)
        # Check plate info
        self.assertEqual(len(cp.plate_info), 1)
        self.assertTrue('Strain' in cp.plate_info)
        self.assertEqual(cp.plate_info['Strain'], 'Test strain 1')
        # Check well info
        well_info = pandas.DataFrame()
        well_info[u'IPTG Concentration (µM)'] = [1., 2., 3., 4., 5., 6.,
                                                 7., 8., 9., 10., 11., 12.,
                                                 13., 14., 15., 16., 17., 18.,
                                                 19., 20., 21., 22., 23., 24.]
        well_info['Measure'] = [True]*24
        pandas.util.testing.assert_frame_equal(cp.well_info, well_info)

    def test_close_plates_inducer_wells_2(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.cell_strain_name = 'Test strain 1'

        # Create inducers for plate
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.concentrations = numpy.arange(24) + 1
        p.apply_inducer(iptg, apply_to='wells')

        atc = platedesign.inducer.ChemicalInducer(
            name='aTc',
            units=u'ng/µL')
        atc.concentrations = (numpy.arange(24) + 1)/10.
        p.apply_inducer(atc, apply_to='wells')

        # Call close plates and check length of output
        cps = p.close_plates()
        self.assertEqual(len(cps), 1)
        # Get the only closed place
        cp = cps[0]
        # Check basic properties
        self.assertEqual(cp.name, 'P1')
        self.assertEqual(cp.n_rows, 4)
        self.assertEqual(cp.n_cols, 6)
        # Check plate info
        self.assertEqual(len(cp.plate_info), 1)
        self.assertTrue('Strain' in cp.plate_info)
        self.assertEqual(cp.plate_info['Strain'], 'Test strain 1')
        # Check well info
        well_info = pandas.DataFrame()
        well_info[u'IPTG Concentration (µM)'] = [1., 2., 3., 4., 5., 6.,
                                                 7., 8., 9., 10., 11., 12.,
                                                 13., 14., 15., 16., 17., 18.,
                                                 19., 20., 21., 22., 23., 24.]
        well_info[u'aTc Concentration (ng/µL)'] = [0.1, 0.2, 0.3, 0.4, 0.5 ,0.6,
                                                   0.7, 0.8, 0.9, 1.0, 1.1, 1.2,
                                                   1.3, 1.4, 1.5, 1.6, 1.7, 1.8,
                                                   1.9, 2.0, 2.1, 2.2, 2.3, 2.4]
        well_info['Measure'] = [True]*24
        pandas.util.testing.assert_frame_equal(cp.well_info, well_info)

    def test_close_plates_inducer_wells_3(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.cell_strain_name = 'Test strain 1'

        # Create inducers for plate
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.concentrations = numpy.arange(24) + 1
        iptg.shuffle()
        p.apply_inducer(iptg, apply_to='wells')

        atc = platedesign.inducer.ChemicalInducer(
            name='aTc',
            units=u'ng/µL')
        atc.concentrations = (numpy.arange(24) + 1)/10.
        p.apply_inducer(atc, apply_to='wells')

        # Call close plates and check length of output
        cps = p.close_plates()
        self.assertEqual(len(cps), 1)
        # Get the only closed place
        cp = cps[0]
        # Check basic properties
        self.assertEqual(cp.name, 'P1')
        self.assertEqual(cp.n_rows, 4)
        self.assertEqual(cp.n_cols, 6)
        # Check plate info
        self.assertEqual(len(cp.plate_info), 1)
        self.assertTrue('Strain' in cp.plate_info)
        self.assertEqual(cp.plate_info['Strain'], 'Test strain 1')
        # Check well info
        well_info = pandas.DataFrame()
        well_info[u'IPTG Concentration (µM)'] = [24., 3., 8., 22., 11., 13.,
                                                 19., 16., 7., 5., 15., 23.,
                                                 21., 18., 1., 2., 14., 12.,
                                                 9., 10., 6., 17., 20., 4.,]
        well_info[u'aTc Concentration (ng/µL)'] = [0.1, 0.2, 0.3, 0.4, 0.5 ,0.6,
                                                   0.7, 0.8, 0.9, 1.0, 1.1, 1.2,
                                                   1.3, 1.4, 1.5, 1.6, 1.7, 1.8,
                                                   1.9, 2.0, 2.1, 2.2, 2.3, 2.4]
        well_info['Measure'] = [True]*24
        pandas.util.testing.assert_frame_equal(cp.well_info, well_info)

    def test_close_plates_inducer_wells_4(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.samples_to_measure = 12
        p.cell_strain_name = 'Test strain 1'

        # Create inducer for plate
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.concentrations = numpy.arange(12) + 1
        p.apply_inducer(iptg, apply_to='wells')

        # Call close plates and check length of output
        cps = p.close_plates()
        self.assertEqual(len(cps), 1)
        # Get the only closed place
        cp = cps[0]
        # Check basic properties
        self.assertEqual(cp.name, 'P1')
        self.assertEqual(cp.n_rows, 4)
        self.assertEqual(cp.n_cols, 6)
        # Check plate info
        self.assertEqual(len(cp.plate_info), 1)
        self.assertTrue('Strain' in cp.plate_info)
        self.assertEqual(cp.plate_info['Strain'], 'Test strain 1')
        # Check well info
        well_info = pandas.DataFrame()
        well_info[u'IPTG Concentration (µM)'] = [1., 2., 3., 4., 5., 6.,
                                                 7., 8., 9., 10., 11., 12.,
                                                 None, None, None, None, None, None,
                                                 None, None, None, None, None, None]
        well_info['Measure'] = [True]*12 + [False]*12
        pandas.util.testing.assert_frame_equal(cp.well_info, well_info)

    def test_close_plates_inducer_media_1(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.cell_strain_name = 'Test strain 1'

        # Create inducer for plate
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.concentrations = [3]
        p.apply_inducer(iptg, apply_to='media')

        # Call close plates and check length of output
        cps = p.close_plates()
        self.assertEqual(len(cps), 1)
        # Get the only closed place
        cp = cps[0]
        # Check basic properties
        self.assertEqual(cp.name, 'P1')
        self.assertEqual(cp.n_rows, 4)
        self.assertEqual(cp.n_cols, 6)
        # Check plate info
        self.assertEqual(len(cp.plate_info), 1)
        self.assertTrue('Strain' in cp.plate_info)
        self.assertEqual(cp.plate_info['Strain'], 'Test strain 1')
        # Check well info
        well_info = pandas.DataFrame()
        well_info[u'IPTG Concentration (µM)'] = [3., 3., 3., 3., 3., 3.,
                                                 3., 3., 3., 3., 3., 3.,
                                                 3., 3., 3., 3., 3., 3.,
                                                 3., 3., 3., 3., 3., 3.,]
        well_info['Measure'] = [True]*24
        pandas.util.testing.assert_frame_equal(cp.well_info, well_info)

    def test_close_plates_inducer_media_2(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.cell_strain_name = 'Test strain 1'

        # Create inducer for plate
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.concentrations = [3]
        p.apply_inducer(iptg, apply_to='media')

        atc = platedesign.inducer.ChemicalInducer(
            name='aTc',
            units=u'ng/µL')
        atc.concentrations = [5]
        p.apply_inducer(atc, apply_to='media')

        # Call close plates and check length of output
        cps = p.close_plates()
        self.assertEqual(len(cps), 1)
        # Get the only closed place
        cp = cps[0]
        # Check basic properties
        self.assertEqual(cp.name, 'P1')
        self.assertEqual(cp.n_rows, 4)
        self.assertEqual(cp.n_cols, 6)
        # Check plate info
        self.assertEqual(len(cp.plate_info), 1)
        self.assertTrue('Strain' in cp.plate_info)
        self.assertEqual(cp.plate_info['Strain'], 'Test strain 1')
        # Check well info
        well_info = pandas.DataFrame()
        well_info[u'IPTG Concentration (µM)'] = [3., 3., 3., 3., 3., 3.,
                                                 3., 3., 3., 3., 3., 3.,
                                                 3., 3., 3., 3., 3., 3.,
                                                 3., 3., 3., 3., 3., 3.,]
        well_info[u'aTc Concentration (ng/µL)'] = [5., 5., 5., 5., 5., 5.,
                                                   5., 5., 5., 5., 5., 5.,
                                                   5., 5., 5., 5., 5., 5.,
                                                   5., 5., 5., 5., 5., 5.,]
        well_info['Measure'] = [True]*24
        pandas.util.testing.assert_frame_equal(cp.well_info, well_info)

    def test_close_plates_inducer_media_3(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.samples_to_measure = 12
        p.cell_strain_name = 'Test strain 1'

        # Create inducer for plate
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.concentrations = [3]
        p.apply_inducer(iptg, apply_to='media')

        # Call close plates and check length of output
        cps = p.close_plates()
        self.assertEqual(len(cps), 1)
        # Get the only closed place
        cp = cps[0]
        # Check basic properties
        self.assertEqual(cp.name, 'P1')
        self.assertEqual(cp.n_rows, 4)
        self.assertEqual(cp.n_cols, 6)
        # Check plate info
        self.assertEqual(len(cp.plate_info), 1)
        self.assertTrue('Strain' in cp.plate_info)
        self.assertEqual(cp.plate_info['Strain'], 'Test strain 1')
        # Check well info
        well_info = pandas.DataFrame()
        well_info[u'IPTG Concentration (µM)'] = [3., 3., 3., 3., 3., 3.,
                                                 3., 3., 3., 3., 3., 3.,
                                                 None, None, None, None, None, None,
                                                 None, None, None, None, None, None]
        well_info['Measure'] = [True]*12 + [False]*12
        pandas.util.testing.assert_frame_equal(cp.well_info, well_info)

    def test_close_plates_combined(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        p.cell_strain_name = 'Test strain 1'
        # Add some metadata
        p.metadata['Meta 1'] = 'Value 1'
        p.metadata['Meta 2'] = 'Value 2'
        # Add cell inoculation info
        p.cell_setup_method = 'fixed_volume'
        p.cell_predilution = 100
        p.cell_predilution_vol = 1000
        p.cell_shot_vol = 5

        # Create inducer for plate rows
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.concentrations = [3, 4, 5, 6, 7, 8]
        p.apply_inducer(iptg, apply_to='rows')

        # Second inducer for plate columns
        atc = platedesign.inducer.ChemicalInducer(
            name='aTc',
            units=u'ng/µL')
        atc.concentrations = [0.1, 0.2, 0.3, 0.4]
        p.apply_inducer(atc, apply_to='cols')

        # Call close plates and check length of output
        cps = p.close_plates()
        self.assertEqual(len(cps), 1)
        # Get the only closed place
        cp = cps[0]
        # Check basic properties
        self.assertEqual(cp.name, 'P1')
        self.assertEqual(cp.n_rows, 4)
        self.assertEqual(cp.n_cols, 6)

        # Check plate info
        self.assertEqual(len(cp.plate_info), 5)
        self.assertTrue('Strain' in cp.plate_info)
        self.assertEqual(cp.plate_info['Strain'], 'Test strain 1')
        self.assertTrue('Meta 1' in cp.plate_info)
        self.assertEqual(cp.plate_info['Meta 1'], 'Value 1')
        self.assertTrue('Meta 2' in cp.plate_info)
        self.assertEqual(cp.plate_info['Meta 2'], 'Value 2')
        self.assertTrue('Preculture Dilution' in cp.plate_info)
        self.assertEqual(cp.plate_info['Preculture Dilution'], 100)
        self.assertTrue('Cell Inoculated Vol.' in cp.plate_info)
        self.assertEqual(cp.plate_info['Cell Inoculated Vol.'], 5)

        # Check well info
        well_info = pandas.DataFrame()
        well_info[u'IPTG Concentration (µM)'] = [3., 4., 5., 6., 7., 8.,
                                                 3., 4., 5., 6., 7., 8.,
                                                 3., 4., 5., 6., 7., 8.,
                                                 3., 4., 5., 6., 7., 8.]
        well_info[u'aTc Concentration (ng/µL)'] = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1,
                                                   0.2, 0.2, 0.2, 0.2, 0.2, 0.2,
                                                   0.3, 0.3, 0.3, 0.3, 0.3, 0.3,
                                                   0.4, 0.4, 0.4, 0.4, 0.4, 0.4,]

        well_info['Measure'] = [True]*24
        pandas.util.testing.assert_frame_equal(cp.well_info, well_info)

class TestPlateArray(unittest.TestCase):
    """
    Tests for the PlateArray class

    """
    def setUp(self):
        # Directory where to save temporary files
        self.temp_dir = "test/temp_plate_array"
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
        # Set random seed
        random.seed(1)

    def tearDown(self):
        # Delete temporary directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

class TestClosedPlate(unittest.TestCase):
    """
    Tests for the ClosedPlate class

    """
    def test_create(self):
        # Create
        p = platedesign.plate.ClosedPlate(name='P1')

    def test_attributes_no_optional_parameters(self):
        # Create
        p = platedesign.plate.ClosedPlate(name='P1')
        # Check all default attributes
        self.assertEqual(p.name, 'P1')
        self.assertEqual(p.n_rows, 4)
        self.assertEqual(p.n_cols, 6)
        self.assertIsNone(p.plate_info)
        self.assertIsNone(p.well_info)
        # Check samples table
        exp_samples_table = pandas.DataFrame(
            {'Plate': ['P1']*24,
             'Row': [1,1,1,1,1,1,
                     2,2,2,2,2,2,
                     3,3,3,3,3,3,
                     4,4,4,4,4,4],
             'Column': [1,2,3,4,5,6]*4})
        exp_samples_table = exp_samples_table[['Plate', 'Row', 'Column']]
        pandas.util.testing.assert_frame_equal(exp_samples_table,
                                               p.samples_table)

    def test_attributes_non_default_size(self):
        # Create
        p = platedesign.plate.ClosedPlate(name='P1', n_rows=8, n_cols=12)
        # Check all default attributes
        self.assertEqual(p.name, 'P1')
        self.assertEqual(p.n_rows, 8)
        self.assertEqual(p.n_cols, 12)
        self.assertIsNone(p.plate_info)
        self.assertIsNone(p.well_info)
        # Check samples table
        exp_samples_table = pandas.DataFrame(
            {'Plate': ['P1']*96,
             'Row': [1,1,1,1,1,1,1,1,1,1,1,1,
                     2,2,2,2,2,2,2,2,2,2,2,2,
                     3,3,3,3,3,3,3,3,3,3,3,3,
                     4,4,4,4,4,4,4,4,4,4,4,4,
                     5,5,5,5,5,5,5,5,5,5,5,5,
                     6,6,6,6,6,6,6,6,6,6,6,6,
                     7,7,7,7,7,7,7,7,7,7,7,7,
                     8,8,8,8,8,8,8,8,8,8,8,8],
             'Column': [1,2,3,4,5,6,7,8,9,10,11,12]*8})
        exp_samples_table = exp_samples_table[['Plate', 'Row', 'Column']]
        pandas.util.testing.assert_frame_equal(exp_samples_table,
                                               p.samples_table)

    def test_attributes_non_default_plate_info(self):
        # Create
        plate_info = collections.OrderedDict()
        plate_info['Cell strain'] = 'Strain 1'
        plate_info['Initial OD'] = 5e-5
        p = platedesign.plate.ClosedPlate(name='P1', plate_info=plate_info)
        # Check all default attributes
        self.assertEqual(p.name, 'P1')
        self.assertEqual(p.n_rows, 4)
        self.assertEqual(p.n_cols, 6)
        self.assertEqual(p.plate_info, plate_info)
        self.assertIsNone(p.well_info)
        # Check samples table
        exp_samples_table = pandas.DataFrame(
            {'Plate': ['P1']*24,
             'Cell strain': ['Strain 1']*24,
             'Initial OD': [5e-5]*24,
             'Row': [1,1,1,1,1,1,
                     2,2,2,2,2,2,
                     3,3,3,3,3,3,
                     4,4,4,4,4,4],
             'Column': [1,2,3,4,5,6]*4})
        exp_samples_table = exp_samples_table[['Plate',
                                               'Cell strain',
                                               'Initial OD',
                                               'Row',
                                               'Column']]
        pandas.util.testing.assert_frame_equal(exp_samples_table,
                                               p.samples_table)

    def test_attributes_non_default_well_info(self):
        # Create
        well_info = pandas.DataFrame()
        well_info['IPTG'] = [1,2,1,4,7,8,4,7,9,6,5,8,4,2,1,4,7,0,3,2,1,5,3,1]
        well_info['Measure'] = [True]*10 + [False]*14
        p = platedesign.plate.ClosedPlate(name='P1', well_info=well_info)
        # Check all default attributes
        self.assertEqual(p.name, 'P1')
        self.assertEqual(p.n_rows, 4)
        self.assertEqual(p.n_cols, 6)
        self.assertIsNone(p.plate_info)
        pandas.util.testing.assert_frame_equal(p.well_info, well_info)
        # Check samples table
        exp_samples_table = pandas.DataFrame(
            {'Plate': ['P1']*24,
             'Row': [1,1,1,1,1,1,
                     2,2,2,2,2,2,
                     3,3,3,3,3,3,
                     4,4,4,4,4,4],
             'Column': [1,2,3,4,5,6]*4,
             'IPTG':[1,2,1,4,7,8,4,7,9,6,5,8,4,2,1,4,7,0,3,2,1,5,3,1],
             'Measure':[True]*10 + [False]*14})
        exp_samples_table = exp_samples_table[['Plate',
                                               'Row',
                                               'Column',
                                               'IPTG',
                                               'Measure']]
        pandas.util.testing.assert_frame_equal(exp_samples_table,
                                               p.samples_table)

    def test_attributes_non_default_info(self):
        # Create
        plate_info = collections.OrderedDict()
        plate_info['Cell strain'] = 'Strain 1'
        plate_info['Initial OD'] = 5e-5
        well_info = pandas.DataFrame()
        well_info['IPTG'] = [1,2,1,4,7,8,4,7,9,6,5,8,4,2,1,4,7,0,3,2,1,5,3,1]
        well_info['Measure'] = [True]*10 + [False]*14
        p = platedesign.plate.ClosedPlate(name='P1',
                                          plate_info=plate_info,
                                          well_info=well_info)
        # Check all default attributes
        self.assertEqual(p.name, 'P1')
        self.assertEqual(p.n_rows, 4)
        self.assertEqual(p.n_cols, 6)
        self.assertEqual(p.plate_info, plate_info)
        pandas.util.testing.assert_frame_equal(p.well_info, well_info)
        # Check samples table
        exp_samples_table = pandas.DataFrame(
            {'Plate': ['P1']*24,
             'Cell strain': ['Strain 1']*24,
             'Initial OD': [5e-5]*24,
             'Row': [1,1,1,1,1,1,
                     2,2,2,2,2,2,
                     3,3,3,3,3,3,
                     4,4,4,4,4,4],
             'Column': [1,2,3,4,5,6]*4,
             'IPTG':[1,2,1,4,7,8,4,7,9,6,5,8,4,2,1,4,7,0,3,2,1,5,3,1],
             'Measure':[True]*10 + [False]*14})
        exp_samples_table = exp_samples_table[['Plate',
                                               'Cell strain',
                                               'Initial OD',
                                               'Row',
                                               'Column',
                                               'IPTG',
                                               'Measure']]
        pandas.util.testing.assert_frame_equal(exp_samples_table,
                                               p.samples_table)

    def test_modify_plate_info(self):
        # Create
        plate_info = collections.OrderedDict()
        plate_info['Cell strain'] = 'Strain 1'
        plate_info['Initial OD'] = 5e-5
        well_info = pandas.DataFrame()
        well_info['IPTG'] = [1,2,1,4,7,8,4,7,9,6,5,8,4,2,1,4,7,0,3,2,1,5,3,1]
        well_info['Measure'] = [True]*10 + [False]*14
        p = platedesign.plate.ClosedPlate(name='P1',
                                          plate_info=plate_info,
                                          well_info=well_info)
        # Check samples table
        exp_samples_table = pandas.DataFrame(
            {'Plate': ['P1']*24,
             'Cell strain': ['Strain 1']*24,
             'Initial OD': [5e-5]*24,
             'Row': [1,1,1,1,1,1,
                     2,2,2,2,2,2,
                     3,3,3,3,3,3,
                     4,4,4,4,4,4],
             'Column': [1,2,3,4,5,6]*4,
             'IPTG':[1,2,1,4,7,8,4,7,9,6,5,8,4,2,1,4,7,0,3,2,1,5,3,1],
             'Measure':[True]*10 + [False]*14})
        exp_samples_table = exp_samples_table[['Plate',
                                               'Cell strain',
                                               'Initial OD',
                                               'Row',
                                               'Column',
                                               'IPTG',
                                               'Measure']]
        pandas.util.testing.assert_frame_equal(exp_samples_table,
                                               p.samples_table)

        # Add field to plate_info
        p.plate_info['Predilution'] = 10
        # Samples table should be the same as before
        pandas.util.testing.assert_frame_equal(exp_samples_table,
                                               p.samples_table)
        # Update and check that samples table has changed
        p.update_samples_table()
        exp_samples_table = pandas.DataFrame(
            {'Plate': ['P1']*24,
             'Cell strain': ['Strain 1']*24,
             'Initial OD': [5e-5]*24,
             'Predilution': [10]*24,
             'Row': [1,1,1,1,1,1,
                     2,2,2,2,2,2,
                     3,3,3,3,3,3,
                     4,4,4,4,4,4],
             'Column': [1,2,3,4,5,6]*4,
             'IPTG':[1,2,1,4,7,8,4,7,9,6,5,8,4,2,1,4,7,0,3,2,1,5,3,1],
             'Measure':[True]*10 + [False]*14})
        exp_samples_table = exp_samples_table[['Plate',
                                               'Cell strain',
                                               'Initial OD',
                                               'Predilution',
                                               'Row',
                                               'Column',
                                               'IPTG',
                                               'Measure']]
        pandas.util.testing.assert_frame_equal(exp_samples_table,
                                               p.samples_table)


    def test_modify_well_info(self):
        # Create
        plate_info = collections.OrderedDict()
        plate_info['Cell strain'] = 'Strain 1'
        plate_info['Initial OD'] = 5e-5
        well_info = pandas.DataFrame()
        well_info['IPTG'] = [1,2,1,4,7,8,4,7,9,6,5,8,4,2,1,4,7,0,3,2,1,5,3,1]
        well_info['Measure'] = [True]*10 + [False]*14
        p = platedesign.plate.ClosedPlate(name='P1',
                                          plate_info=plate_info,
                                          well_info=well_info)
        pandas.util.testing.assert_frame_equal(p.well_info, well_info)
        # Check samples table
        exp_samples_table = pandas.DataFrame(
            {'Plate': ['P1']*24,
             'Cell strain': ['Strain 1']*24,
             'Initial OD': [5e-5]*24,
             'Row': [1,1,1,1,1,1,
                     2,2,2,2,2,2,
                     3,3,3,3,3,3,
                     4,4,4,4,4,4],
             'Column': [1,2,3,4,5,6]*4,
             'IPTG':[1,2,1,4,7,8,4,7,9,6,5,8,4,2,1,4,7,0,3,2,1,5,3,1],
             'Measure':[True]*10 + [False]*14})
        exp_samples_table = exp_samples_table[['Plate',
                                               'Cell strain',
                                               'Initial OD',
                                               'Row',
                                               'Column',
                                               'IPTG',
                                               'Measure']]
        pandas.util.testing.assert_frame_equal(exp_samples_table,
                                               p.samples_table)

        # Change one of the columns in well_info
        p.well_info['Measure'] = [False]*8 + [True]*16
        # Samples table should be the same as before
        pandas.util.testing.assert_frame_equal(exp_samples_table,
                                               p.samples_table)
        # Update and check that samples table has changed
        p.update_samples_table()
        exp_samples_table = pandas.DataFrame(
            {'Plate': ['P1']*24,
             'Cell strain': ['Strain 1']*24,
             'Initial OD': [5e-5]*24,
             'Row': [1,1,1,1,1,1,
                     2,2,2,2,2,2,
                     3,3,3,3,3,3,
                     4,4,4,4,4,4],
             'Column': [1,2,3,4,5,6]*4,
             'IPTG':[1,2,1,4,7,8,4,7,9,6,5,8,4,2,1,4,7,0,3,2,1,5,3,1],
             'Measure':[False]*8 + [True]*16})
        exp_samples_table = exp_samples_table[['Plate',
                                               'Cell strain',
                                               'Initial OD',
                                               'Row',
                                               'Column',
                                               'IPTG',
                                               'Measure']]
        pandas.util.testing.assert_frame_equal(exp_samples_table,
                                               p.samples_table)
