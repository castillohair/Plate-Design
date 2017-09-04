# -*- coding: UTF-8 -*-
"""
Unit tests for plate classes

"""

import collections
import itertools
import os
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

    # def test_save_rep_setup_instructions_1(self):
    #     # Create plate
    #     p = platedesign.plate.Plate(name='P1')
    #     # Run save_rep_setup_instructions
    #     p.save_rep_setup_instructions(file_name=os.path.join(self.temp_dir,
    #                                                          'plate_rep.xlsx'))
    #     # TODO: check results

    # def test_save_rep_setup_instructions_2(self):
    #     # Create plate
    #     p = platedesign.plate.Plate(name='P1')
    #     # Create new spreadsheet
    #     wb_test = openpyxl.Workbook()
    #     # Remove sheet created by default
    #     wb_test.remove_sheet(wb_test.active)
    #     # Run save_rep_setup_instructions
    #     p.save_rep_setup_instructions(workbook=wb_test)
    #     # save_exp_setup_instructions does not do anything in Plate. There is
    #     # no need to check for results.

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

    # def test_close_plates(self):
    #     # TODO
    #     pass

class TestPlateArray(unittest.TestCase):
    """
    Tests for the PlateArray class

    """
    def setUp(self):
        # Directory where to save temporary files
        self.temp_dir = "test/temp_plate_array"
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

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
