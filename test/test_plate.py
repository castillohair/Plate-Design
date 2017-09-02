# -*- coding: UTF-8 -*-
"""
Unit tests for plate classes

"""

import collections
import itertools
import os
import shutil
import unittest

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

    def test_save_exp_setup_instructions(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Check that save_exp_setup_instructions runs successfully
        p.save_exp_setup_instructions()
        # save_exp_setup_instructions does not do anything in Plate. There is
        # no need to check for results.

    def test_save_exp_setup_files(self):
        # Create plate
        p = platedesign.plate.Plate(name='P1')
        # Check that save_exp_setup_files runs successfully
        p.save_exp_setup_files()
        # save_exp_setup_files does not do anything in Plate. There is no need
        # to check for results.

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
    pass
