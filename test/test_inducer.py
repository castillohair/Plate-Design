# -*- coding: UTF-8 -*-
"""
Unit tests for inducer classes

"""

import itertools
import os
import random
import shutil
import unittest

import numpy
import openpyxl
import pandas

import platedesign

class TestInducerBase(unittest.TestCase):
    """
    Tests for the InducerBase class
    
    """
    def test_create(self):
        ind = platedesign.inducer.InducerBase('Inducer')

    def test_name(self):
        ind = platedesign.inducer.InducerBase('Inducer')
        self.assertEqual(ind.name, 'Inducer')

    def test_default_doses_table(self):
        ind = platedesign.inducer.InducerBase('Inducer')
        self.assertIsInstance(ind.doses_table, pandas.DataFrame)
        self.assertTrue(ind.doses_table.empty)

    def test_shuffle_not_implemented(self):
        ind = platedesign.inducer.InducerBase('Inducer')
        with self.assertRaises(NotImplementedError):
            ind.set_vol_from_shots(n_shots=10)
        with self.assertRaises(NotImplementedError):
            ind.shuffle()

    def test_no_effect_functions(self):
        ind = platedesign.inducer.InducerBase('Inducer')
        ind.save_exp_setup_instructions()
        ind.save_exp_setup_files()
        ind.save_rep_setup_instructions()
        ind.save_rep_setup_files()

class TestChemicalInducer(unittest.TestCase):
    """
    Tests for the ChemicalInducer class.

    """
    def setUp(self):
        # Directory where to save temporary files
        self.temp_dir = "test/temp_chemical_inducer"
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def tearDown(self):
        # Delete temporary directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_create(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')

    def test_default_dose_table_attributes(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Default main attributes
        self.assertEqual(iptg.name, 'IPTG')
        self.assertEqual(iptg.units, u'µM')
        self.assertEqual(iptg.id_prefix, 'I')
        self.assertEqual(iptg.id_offset, 0)
        # Default dilutions table
        df = pandas.DataFrame()
        pandas.util.testing.assert_frame_equal(iptg._doses_table, df)
        pandas.util.testing.assert_frame_equal(iptg.doses_table, df)
        # Header for the dilutions table
        self.assertEqual(iptg._concentrations_header,
                         u"IPTG Concentration (µM)")

    def test_default_custom_table_attributes(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM',
            id_prefix='IP',
            id_offset=24)
        # Default main attributes
        self.assertEqual(iptg.name, 'IPTG')
        self.assertEqual(iptg.units, u'µM')
        self.assertEqual(iptg.id_prefix, 'IP')
        self.assertEqual(iptg.id_offset, 24)

    def test_default_calculation_attributes(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        self.assertIsNone(iptg.stock_conc)
        self.assertIsNone(iptg.media_vol)
        self.assertIsNone(iptg.shot_vol)
        self.assertIsNone(iptg.total_vol)
        self.assertIsNone(iptg.replicate_vol)
        self.assertEqual(iptg.vol_safety_factor, 1.2)
        self.assertEqual(iptg.min_stock_vol,1.5)
        self.assertEqual(iptg.max_stock_vol, 20.)
        self.assertEqual(iptg.stock_dilution_step, 10.)
        self.assertEqual(iptg.stock_decimals, 2)
        self.assertEqual(iptg.water_decimals, 1)

    def test_default_shuffling_attributes(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        self.assertTrue(iptg.shuffling_enabled)
        self.assertIsNone(iptg.shuffled_idx)
        self.assertEqual(iptg.shuffling_sync_list, [])

    def test_concentrations_assignment(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Write concentrations should generate a corresponding _doses_table
        iptg.concentrations = numpy.linspace(0,1,11)
        # Test doses table
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': numpy.linspace(0,1,11)},
            index=['I{:03d}'.format(i + 1) for i in range(11)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(iptg._doses_table, df)
        pandas.util.testing.assert_frame_equal(iptg.doses_table, df)
        # Test conc attribute
        numpy.testing.assert_array_equal(iptg.concentrations,
                                         numpy.linspace(0,1,11))

    def test_concentrations_assignment_custom_id(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM',
            id_prefix='IP',
            id_offset=24)
        # Writing concentrations should generate a corresponding _doses_table
        iptg.concentrations = numpy.linspace(0,1,11)
        # Test doses table
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': numpy.linspace(0,1,11)},
            index=['IP{:03d}'.format(i + 24 + 1) for i in range(11)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(iptg._doses_table, df)
        pandas.util.testing.assert_frame_equal(iptg.doses_table, df)
        # Test concentrations attribute
        numpy.testing.assert_array_equal(iptg.concentrations,
                                         numpy.linspace(0,1,11))

    def test_set_gradient_linear(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set concentrations from gradient
        iptg.set_gradient(min=0, max=1, n=21)
        # Check doses table
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': numpy.linspace(0,1,21)},
            index=['I{:03d}'.format(i + 1) for i in range(21)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(iptg._doses_table, df)
        pandas.util.testing.assert_frame_equal(iptg.doses_table, df)
        # Test concentrations attribute
        numpy.testing.assert_array_equal(iptg.concentrations,
                                         numpy.linspace(0,1,21))

    def test_set_gradient_linear_repeat(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set concentrations from gradient
        iptg.set_gradient(min=0, max=1, n=12, n_repeat=3)
        # Check doses table
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': numpy.repeat(numpy.linspace(0,1,4), 3)},
            index=['I{:03d}'.format(i + 1) for i in range(12)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(iptg._doses_table, df)
        pandas.util.testing.assert_frame_equal(iptg.doses_table, df)
        # Test concentrations attribute
        numpy.testing.assert_array_equal(iptg.concentrations,
                                         numpy.repeat(numpy.linspace(0,1,4), 3))

    def test_set_gradient_linear_repeat_error(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        with self.assertRaises(ValueError):
            iptg.set_gradient(min=0, max=1, n=11, n_repeat=3)

    def test_set_gradient_log(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set concentrations from gradient
        iptg.set_gradient(min=1e-6, max=1e-3, n=10, scale='log')
        # Check doses table
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': numpy.logspace(-6,-3,10)},
            index=['I{:03d}'.format(i + 1) for i in range(10)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(iptg._doses_table, df)
        pandas.util.testing.assert_frame_equal(iptg.doses_table, df)
        # Test concentrations attribute
        numpy.testing.assert_array_equal(iptg.concentrations,
                                         numpy.logspace(-6,-3,10))

    def test_set_gradient_log_repeat(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set concentrations from gradient
        iptg.set_gradient(min=1e-6, max=1e-3, n=12, scale='log', n_repeat=3)
        # Check doses table
        conc = numpy.repeat(numpy.logspace(-6,-3,4), 3)
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': conc},
            index=['I{:03d}'.format(i + 1) for i in range(12)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(iptg._doses_table, df)
        pandas.util.testing.assert_frame_equal(iptg.doses_table, df)
        # Test concentrations attribute
        numpy.testing.assert_array_equal(iptg.concentrations, conc)

    def test_set_gradient_log_zero(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set concentrations from gradient
        iptg.set_gradient(min=1e-6, max=1e-3, n=10, scale='log', use_zero=True)
        # Check doses table
        conc = numpy.append([0], numpy.logspace(-6,-3,9))
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': conc},
            index=['I{:03d}'.format(i + 1) for i in range(10)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(iptg._doses_table, df)
        pandas.util.testing.assert_frame_equal(iptg.doses_table, df)
        # Test concentrations attribute
        numpy.testing.assert_array_equal(iptg.concentrations, conc)

    def test_set_gradient_log_zero_repeat(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set concentrations from gradient
        iptg.set_gradient(min=1e-6,
                          max=1e-3,
                          n=12,
                          scale='log',
                          use_zero=True,
                          n_repeat=2)
        # Check doses table
        conc = numpy.repeat(numpy.append([0], numpy.logspace(-6,-3,5)), 2)
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': conc},
            index=['I{:03d}'.format(i + 1) for i in range(12)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(iptg._doses_table, df)
        pandas.util.testing.assert_frame_equal(iptg.doses_table, df)
        # Test concentrations attribute
        numpy.testing.assert_array_equal(iptg.concentrations, conc)

    def test_set_gradient_scale_error(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        with self.assertRaises(ValueError):
            iptg.set_gradient(min=1e-6, max=1e-3, n=10, scale='symlog')

    def test_set_vol_from_shots_single_rep(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.concentrations = numpy.linspace(0,1,11)
        # Shot volume and safety factor should be set
        iptg.shot_vol = 5.
        iptg.vol_safety_factor = 1.2
        # Call function to set functions
        iptg.set_vol_from_shots(n_shots=5)
        # Check attributes
        self.assertEqual(iptg.replicate_vol, None)
        self.assertEqual(iptg.total_vol, 30)

    def test_set_vol_from_shots_many_reps(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.concentrations = numpy.linspace(0,1,11)
        # Shot volume and safety factor should be set
        iptg.shot_vol = 5.
        iptg.vol_safety_factor = 1.2
        # Call function to set functions
        iptg.set_vol_from_shots(n_shots=5, n_replicates=5)
        # Check attributes
        self.assertEqual(iptg.replicate_vol, 30)
        self.assertEqual(iptg.total_vol, 200)

    def test_shuffle(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.concentrations = numpy.linspace(0,1,11)
        # Shuffle
        random.seed(1)
        iptg.shuffle()
        # The following indices give the correct shuffled concentrations array
        # after setting the random seed to one.
        shuffling_ind = [10, 5, 0, 4, 9, 7, 3, 2, 6, 8, 1]
        # Check concentrations
        concentrations = numpy.linspace(0,1,11)
        numpy.testing.assert_almost_equal(iptg.concentrations,
                                          concentrations[shuffling_ind])
        # Check unshuffled doses table
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': numpy.linspace(0,1,11)},
            index=['I{:03d}'.format(i + 1) for i in range(11)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(iptg._doses_table, df)
        # Check shuffled doses table
        pandas.util.testing.assert_frame_equal(iptg.doses_table,
                                               df.iloc[shuffling_ind])

    def test_shuffle_disabled(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.concentrations = numpy.linspace(0,1,11)
        # Disable shuffling
        iptg.shuffling_enabled = False
        # Shuffle
        random.seed(1)
        iptg.shuffle()
        # Check concentrations
        numpy.testing.assert_almost_equal(iptg.concentrations,
                                          numpy.linspace(0,1,11))
        # Check unshuffled doses table
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': numpy.linspace(0,1,11)},
            index=['I{:03d}'.format(i + 1) for i in range(11)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(iptg._doses_table, df)
        pandas.util.testing.assert_frame_equal(iptg.doses_table, df)

    def test_sync_shuffling_fail(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.concentrations = numpy.linspace(0,1,11)
        atc = platedesign.inducer.ChemicalInducer(
            name='aTc',
            units=u'µM')
        atc.concentrations = numpy.linspace(2,3,12)

        with self.assertRaises(ValueError):
            iptg.sync_shuffling(atc)

    def test_sync_shuffling_attributes(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.concentrations = numpy.linspace(0,1,11)
        atc = platedesign.inducer.ChemicalInducer(
            name='aTc',
            units=u'µM')
        atc.concentrations = numpy.linspace(2,3,11)
        # Sync shuffling
        iptg.sync_shuffling(atc)
        # Check attributes
        self.assertTrue(iptg.shuffling_enabled)
        self.assertFalse(atc.shuffling_enabled)
        self.assertEqual(iptg.shuffling_sync_list, [atc])

    def test_sync_shuffling_no_shuffling_in_dependent(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.concentrations = numpy.linspace(0,1,11)
        atc = platedesign.inducer.ChemicalInducer(
            name='aTc',
            units=u'µM')
        atc.concentrations = numpy.linspace(2,3,11)
        # Sync shuffling
        iptg.sync_shuffling(atc)
        # Shuffle dependent inducer
        random.seed(1)
        atc.shuffle()
        # Check concentrations
        numpy.testing.assert_almost_equal(atc.concentrations,
                                          numpy.linspace(0,1,11) + 2)
        # Check unshuffled doses table
        df = pandas.DataFrame(
            {u'aTc Concentration (µM)': numpy.linspace(0,1,11) + 2},
            index=['a{:03d}'.format(i + 1) for i in range(11)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(atc._doses_table, df)
        pandas.util.testing.assert_frame_equal(atc.doses_table, df)

    def test_sync_shuffling(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        iptg.concentrations = numpy.linspace(0,1,11)
        atc = platedesign.inducer.ChemicalInducer(
            name='aTc',
            units=u'µM')
        atc.concentrations = numpy.linspace(2,3,11)
        # Sync shuffling
        iptg.sync_shuffling(atc)
        # Shuffle both inducers by calling the first one
        random.seed(1)
        iptg.shuffle()
        # The following indices give the correct shuffled concentrations array
        # after setting the random seed to one.
        shuffling_ind = [10, 5, 0, 4, 9, 7, 3, 2, 6, 8, 1]
        # Check concentrations for independent inducer
        concentrations = numpy.linspace(0,1,11)
        numpy.testing.assert_almost_equal(iptg.concentrations,
                                          concentrations[shuffling_ind])
        # Check unshuffled doses table
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': numpy.linspace(0,1,11)},
            index=['I{:03d}'.format(i + 1) for i in range(11)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(iptg._doses_table, df)
        # Check shuffled doses table
        pandas.util.testing.assert_frame_equal(iptg.doses_table,
                                               df.iloc[shuffling_ind])
        # Check concentrations for dependent inducer
        concentrations = numpy.linspace(2,3,11)
        numpy.testing.assert_almost_equal(atc.concentrations,
                                          concentrations[shuffling_ind])
        # Check unshuffled doses table
        df = pandas.DataFrame(
            {u'aTc Concentration (µM)': numpy.linspace(0,1,11) + 2},
            index=['a{:03d}'.format(i + 1) for i in range(11)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(atc._doses_table, df)
        # Check shuffled doses table
        pandas.util.testing.assert_frame_equal(atc.doses_table,
                                               df.iloc[shuffling_ind])

    def test_save_exp_setup_instructions_error_1(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set attributes for calculations
        # iptg.stock_conc = 1e6
        iptg.media_vol = 500.
        iptg.shot_vol = 5.
        iptg.total_vol = 100.
        # Set concentrations from gradient
        iptg.set_gradient(min=0.5, max=500, n=12, scale='log', use_zero=True)
        # Try to generate setup instructions
        with self.assertRaises(AttributeError):
            iptg.save_exp_setup_instructions(file_name=os.path.join(
                self.temp_dir,
                'IPTG.xlsx'))

    def test_save_exp_setup_instructions_error_2(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set attributes for calculations
        iptg.stock_conc = 1e6
        # iptg.media_vol = 500.
        iptg.shot_vol = 5.
        iptg.total_vol = 100.
        # Set concentrations from gradient
        iptg.set_gradient(min=0.5, max=500, n=12, scale='log', use_zero=True)
        # Try to generate setup instructions
        with self.assertRaises(AttributeError):
            iptg.save_exp_setup_instructions(file_name=os.path.join(
                self.temp_dir,
                'IPTG.xlsx'))

    def test_save_exp_setup_instructions_error_3(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set attributes for calculations
        iptg.stock_conc = 1e6
        iptg.media_vol = 500.
        # iptg.shot_vol = 5.
        iptg.total_vol = 100.
        # Set concentrations from gradient
        iptg.set_gradient(min=0.5, max=500, n=12, scale='log', use_zero=True)
        # Try to generate setup instructions
        with self.assertRaises(AttributeError):
            iptg.save_exp_setup_instructions(file_name=os.path.join(
                self.temp_dir,
                'IPTG.xlsx'))

    def test_save_exp_setup_instructions_error_4(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set attributes for calculations
        iptg.stock_conc = 1e6
        iptg.media_vol = 500.
        iptg.shot_vol = 5.
        # iptg.total_vol = 100.
        # Set concentrations from gradient
        iptg.set_gradient(min=0.5, max=500, n=12, scale='log', use_zero=True)
        # Try to generate setup instructions
        with self.assertRaises(AttributeError):
            iptg.save_exp_setup_instructions(file_name=os.path.join(
                self.temp_dir,
                'IPTG.xlsx'))

    def test_save_exp_setup_instructions_error_5(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set attributes for calculations
        iptg.stock_conc = 1e6
        iptg.media_vol = 500.
        iptg.shot_vol = 5.
        iptg.total_vol = 100.
        # Set concentrations from gradient
        iptg.set_gradient(min=0.5, max=500, n=12, scale='log', use_zero=True)
        # Try to generate setup instructions
        with self.assertRaises(ValueError):
            iptg.save_exp_setup_instructions()

    def test_save_exp_setup_instructions_1(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set attributes for calculations
        iptg.stock_conc = 1e6
        iptg.media_vol = 500.
        iptg.shot_vol = 5.
        iptg.total_vol = 100.
        # Set concentrations from gradient
        iptg.set_gradient(min=0.5, max=500, n=12, scale='log', use_zero=True)
        # Try to generate setup instructions
        file_name = os.path.join(self.temp_dir, 'IPTG_test1.xlsx')
        iptg.save_exp_setup_instructions(file_name=file_name)
        # Load instructions file
        df_in_file = pandas.read_excel(file_name)
        # Expected result
        c = numpy.append([0], numpy.logspace(numpy.log10(0.5),
                                             numpy.log10(500),
                                             11))
        d = numpy.array([1., 1000., 1000., 1000., 100., 100.,
                         100., 10., 10., 10., 1., 1.])
        ind = numpy.round(500*c/5*100/1e6*d, decimals=2)
        water = numpy.round(100 - ind, decimals=1)
        actual_conc = 1e6/d*ind/(ind + water)*5/500.
        # Expected dataframe
        df = pandas.DataFrame()
        df[u'IPTG Concentration (µM)'] = actual_conc
        df[u'Stock dilution'] = d
        df[u'Inducer volume (µL)'] = ind
        df[u'Water volume (µL)'] = water
        df[u'Total volume (µL)'] = 100.
        df[u'Aliquot IDs'] = ['I{:03d}'.format(i + 1) for i in range(12)]
        # Add two empty rows
        df = df.reindex(df.index.union([len(c), len(c) + 1]))
        # Add message in first column, last row
        df[u'IPTG Concentration (µM)'] = \
            df[u'IPTG Concentration (µM)'].astype('object')
        df.set_value(
            len(c) + 1,
            u'IPTG Concentration (µM)',
            u'Distribute in aliquots of {} µL.'.format(100.))
        # Test for equality
        pandas.util.testing.assert_frame_equal(df_in_file, df)

    def test_save_exp_setup_instructions_2(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set attributes for calculations
        iptg.stock_conc = 1e6
        iptg.media_vol = 500.
        iptg.shot_vol = 5.
        iptg.total_vol = 100.
        # Set concentrations from gradient
        iptg.set_gradient(min=0.5,
                          max=500,
                          n=12,
                          scale='log',
                          use_zero=True,
                          n_repeat=2)
        # Try to generate setup instructions
        file_name = os.path.join(self.temp_dir, 'IPTG_test2.xlsx')
        iptg.save_exp_setup_instructions(file_name=file_name)
        # Load instructions file
        df_in_file = pandas.read_excel(file_name)
        # Expected result
        c = numpy.append([0], numpy.logspace(numpy.log10(0.5),
                                             numpy.log10(500),
                                             5))
        d = numpy.array([1., 1000., 100., 10., 10., 1.])
        ind = numpy.round(500*c/5*200/1e6*d, decimals=2)
        water = numpy.round(200 - ind, decimals=1)
        actual_conc = 1e6/d*ind/(ind + water)*5/500.
        # Expected dataframe
        df = pandas.DataFrame()
        df[u'IPTG Concentration (µM)'] = actual_conc
        df[u'Stock dilution'] = d
        df[u'Inducer volume (µL)'] = ind
        df[u'Water volume (µL)'] = water
        df[u'Total volume (µL)'] = 200.
        df[u'Aliquot IDs'] = ["I001, I002", "I003, I004", "I005, I006",
                              "I007, I008", "I009, I010", "I011, I012"]
        # Add two empty rows
        df = df.reindex(df.index.union([len(c), len(c) + 1]))
        # Add message in first column, last row
        df[u'IPTG Concentration (µM)'] = \
            df[u'IPTG Concentration (µM)'].astype('object')
        df.set_value(
            len(c) + 1,
            u'IPTG Concentration (µM)',
            u'Distribute in aliquots of {} µL.'.format(100.))
        # Test for equality
        pandas.util.testing.assert_frame_equal(df_in_file, df)

    def test_save_exp_setup_instructions_3(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set attributes for calculations
        iptg.stock_conc = 1e6
        iptg.media_vol = 500.
        iptg.shot_vol = 5.
        iptg.vol_safety_factor = 1.2
        # Call function to set volumes
        iptg.set_vol_from_shots(n_shots=6, n_replicates=5)
        # Check attributes
        self.assertEqual(iptg.replicate_vol, 40)
        self.assertEqual(iptg.total_vol, 300)
        # Set concentrations from gradient
        iptg.set_gradient(min=0.5,
                          max=500,
                          n=12,
                          scale='log',
                          use_zero=True,
                          n_repeat=2)
        # Try to generate setup instructions
        file_name = os.path.join(self.temp_dir, 'IPTG_test3.xlsx')
        iptg.save_exp_setup_instructions(file_name=file_name)
        # Load instructions file
        df_in_file = pandas.read_excel(file_name)
        # Expected result
        c = numpy.append([0], numpy.logspace(numpy.log10(0.5),
                                             numpy.log10(500),
                                             5))
        d = numpy.array([1., 100., 100., 10., 1., 1.])
        ind = numpy.round(500*c/5*600/1e6*d, decimals=2)
        water = numpy.round(600 - ind, decimals=1)
        actual_conc = 1e6/d*ind/(ind + water)*5/500.
        # Expected dataframe
        df = pandas.DataFrame()
        df[u'IPTG Concentration (µM)'] = actual_conc
        df[u'Stock dilution'] = d
        df[u'Inducer volume (µL)'] = ind
        df[u'Water volume (µL)'] = water
        df[u'Total volume (µL)'] = 600.
        df[u'Aliquot IDs'] = ["I001, I002", "I003, I004", "I005, I006",
                              "I007, I008", "I009, I010", "I011, I012"]
        # Add two empty rows
        df = df.reindex(df.index.union([len(c), len(c) + 1]))
        # Add message in first column, last row
        df[u'IPTG Concentration (µM)'] = \
            df[u'IPTG Concentration (µM)'].astype('object')
        df.set_value(
            len(c) + 1,
            u'IPTG Concentration (µM)',
            u'Distribute in aliquots of {} µL.'.format(40.))
        # Test for equality
        pandas.util.testing.assert_frame_equal(df_in_file, df)

    def test_save_exp_setup_instructions_workbook(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units=u'µM')
        # Set attributes for calculations
        iptg.stock_conc = 1e6
        iptg.media_vol = 500.
        iptg.shot_vol = 5.
        iptg.total_vol = 100.
        # Set concentrations from gradient
        iptg.set_gradient(min=0.5, max=500, n=12, scale='log', use_zero=True)
        # Create new spreadsheet
        wb_test = openpyxl.Workbook()
        # Remove sheet created by default
        wb_test.remove_sheet(wb_test.active)
        # Try to generate setup instructions
        iptg.save_exp_setup_instructions(workbook=wb_test)
        # Extract data from worksheet and convert into dataframe
        ws_values = wb_test.get_sheet_by_name('IPTG').values
        cols = next(ws_values)
        ws_values = list(ws_values)
        df_in_wb = pandas.DataFrame(ws_values, columns=cols)
        # Expected result
        c = numpy.append([0], numpy.logspace(numpy.log10(0.5),
                                             numpy.log10(500),
                                             11))
        d = numpy.array([1., 1000., 1000., 1000., 100., 100.,
                         100., 10., 10., 10., 1., 1.])
        ind = numpy.round(500*c/5*100/1e6*d, decimals=2)
        water = numpy.round(100 - ind, decimals=1)
        actual_conc = 1e6/d*ind/(ind + water)*5/500.
        # Expected dataframe
        df = pandas.DataFrame()
        df[u'IPTG Concentration (µM)'] = actual_conc
        df[u'Stock dilution'] = d
        df[u'Inducer volume (µL)'] = ind
        df[u'Water volume (µL)'] = water
        df[u'Total volume (µL)'] = 100.
        df[u'Aliquot IDs'] = ['I{:03d}'.format(i + 1) for i in range(12)]
        # Add two empty rows
        df = df.reindex(df.index.union([len(c), len(c) + 1]))
        # Add message in first column, last row
        df[u'IPTG Concentration (µM)'] = \
            df[u'IPTG Concentration (µM)'].astype('object')
        df.set_value(
            len(c) + 1,
            u'IPTG Concentration (µM)',
            u'Distribute in aliquots of {} µL.'.format(100.))
        # Test for equality
        pandas.util.testing.assert_frame_equal(df_in_wb, df)

class TestChemicalGeneExpression(unittest.TestCase):
    """
    Tests for the ChemicalInducer class.

    """
    def setUp(self):
        # Directory where to save temporary files
        self.temp_dir = "test/temp_chemical_gene_expression"
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def tearDown(self):
        # Delete temporary directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def hill(self, y0, dy, n, K, x):
        return y0 + dy*(x**n)/(K**n + x**n)

    def hill_inverse(self, y0, dy, n, K, y):
        z = (y - y0)/dy
        return K*(z/(1.-z))**(1./n)

    def test_create(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})

    def test_create_error_arg_number(self):
        with self.assertRaises(TypeError):
            rr = platedesign.inducer.ChemicalGeneExpression(
                name='RR',
                units='MEFL')

    def test_create_error_hill_params_1(self):
        with self.assertRaises(ValueError):
            rr = platedesign.inducer.ChemicalGeneExpression(
                name='RR',
                units='MEFL',
                inducer_name='IPTG',
                inducer_units=u'µM',
                hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2, 'a': 20})

    def test_create_error_hill_params_2(self):
        with self.assertRaises(ValueError):
            rr = platedesign.inducer.ChemicalGeneExpression(
                name='RR',
                units='MEFL',
                inducer_name='IPTG',
                inducer_units=u'µM',
                hill_params={'y0': 10, 'dy':1000, 'K': 50})

    def test_create_error_hill_params_3(self):
        with self.assertRaises(ValueError):
            rr = platedesign.inducer.ChemicalGeneExpression(
                name='RR',
                units='MEFL',
                inducer_name='IPTG',
                inducer_units=u'µM',
                hill_params={'y0': 10, 'dy':1000, 'K': 50, 'a': 20})

    def test_hill_function_method_forward_array(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Test (forward) hill function method
        x = numpy.array([0, 1e-2, 3e-2, 1e-1, 3e-1, 1, 3, 1e1, 3e1, 1e2, 3e2])
        y = rr._hill(x)
        # Expected output
        y_exp = self.hill(y0=10., dy=1000., K=50., n=2., x=x)
        numpy.testing.assert_almost_equal(y, y_exp)

    def test_hill_function_method_inverse_array(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Test (inverse) hill function method
        y = numpy.array([10.001, 30, 100, 300, 1000, 1009.9])
        x = rr._hill_inverse(y)
        # Expected output
        x_exp = self.hill_inverse(y0=10., dy=1000., K=50., n=2., y=y)
        numpy.testing.assert_almost_equal(x, x_exp)

    def test_hill_function_method_inverse_limits_array(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Test (inverse) hill function method, extend input with edge values
        y = numpy.array([10.001, 30, 100, 300, 1000, 1009.9, 10, 1010])
        x = rr._hill_inverse(y)
        # Expected output
        x_exp = self.hill_inverse(y0=10., dy=1000., K=50., n=2., y=y[:-2])
        x_exp = numpy.append(x_exp, [0, numpy.inf])
        numpy.testing.assert_almost_equal(x, x_exp)

    def test_hill_function_method_inverse_error_bounds_array(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Test (inverse) hill function method, extend input with edge values
        y = numpy.array([10.001, 30, 100, 300, 1000, 1009.9, 10, 1010.1])
        with self.assertRaises(ValueError):
            x = rr._hill_inverse(y)
        y = numpy.array([10.001, 30, 100, 300, 1000, 1009.9, 9.999])
        with self.assertRaises(ValueError):
            x = rr._hill_inverse(y)

    def test_hill_function_method_forward_scalar(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Test (forward) hill function method
        x = 3
        y = rr._hill(x)
        # Expected output
        y_exp = self.hill(y0=10., dy=1000., K=50., n=2., x=x)
        numpy.testing.assert_almost_equal(y, y_exp)

    def test_hill_function_method_inverse_scalar(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Test (inverse) hill function method
        y = 500
        x = rr._hill_inverse(y)
        # Expected output
        x_exp = self.hill_inverse(y0=10., dy=1000., K=50., n=2., y=y)
        numpy.testing.assert_almost_equal(x, x_exp)

    def test_hill_function_method_inverse_limits_low_scalar(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Test (inverse) hill function method
        y = 10
        x = rr._hill_inverse(y)
        numpy.testing.assert_almost_equal(x, 0)

    def test_hill_function_method_inverse_limits_high_scalar(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Test (inverse) hill function method
        y = 1010
        x = rr._hill_inverse(y)
        numpy.testing.assert_almost_equal(x, numpy.inf)

    def test_hill_function_method_inverse_error_bounds_scalar(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Test (inverse) hill function method
        y = 1010.1
        with self.assertRaises(ValueError):
            x = rr._hill_inverse(y)
        y = 9.999
        with self.assertRaises(ValueError):
            x = rr._hill_inverse(y)

    def test_default_dose_table_attributes(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Default main attributes
        self.assertEqual(rr.name, 'RR')
        self.assertEqual(rr.units, 'MEFL')
        self.assertEqual(rr.inducer_name, 'IPTG')
        self.assertEqual(rr.inducer_units, u'µM')
        self.assertEqual(rr.id_prefix, 'R')
        self.assertEqual(rr.id_offset, 0)
        # Default dilutions table
        df = pandas.DataFrame()
        pandas.util.testing.assert_frame_equal(rr._doses_table, df)
        pandas.util.testing.assert_frame_equal(rr.doses_table, df)
        # Headers for the dose table
        self.assertEqual(rr._concentrations_header,
                         u"IPTG Concentration (µM)")
        self.assertEqual(rr._expression_levels_header,
                         u"RR Expression (MEFL)")

    def test_default_custom_table_attributes(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2},
            id_prefix='CcaR',
            id_offset=24)
        # Default main attributes
        self.assertEqual(rr.name, 'RR')
        self.assertEqual(rr.units, 'MEFL')
        self.assertEqual(rr.inducer_name, 'IPTG')
        self.assertEqual(rr.inducer_units, u'µM')
        self.assertEqual(rr.id_prefix, 'CcaR')
        self.assertEqual(rr.id_offset, 24)

    def test_default_calculation_attributes(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        self.assertIsNone(rr.stock_conc)
        self.assertIsNone(rr.media_vol)
        self.assertIsNone(rr.shot_vol)
        self.assertIsNone(rr.total_vol)
        self.assertIsNone(rr.replicate_vol)
        self.assertEqual(rr.vol_safety_factor, 1.2)
        self.assertEqual(rr.min_stock_vol,1.5)
        self.assertEqual(rr.max_stock_vol, 20.)
        self.assertEqual(rr.stock_dilution_step, 10.)
        self.assertEqual(rr.stock_decimals, 2)
        self.assertEqual(rr.water_decimals, 1)

    def test_default_shuffling_attributes(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        self.assertTrue(rr.shuffling_enabled)
        self.assertIsNone(rr.shuffled_idx)
        self.assertEqual(rr.shuffling_sync_list, [])

    def test_concentrations_assignment(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Concentrations
        concentrations = numpy.logspace(numpy.log10(0.5),
                                        numpy.log10(500),
                                        11)
        expression_levels = self.hill(y0=10,
                                      dy=1000,
                                      K=50,
                                      n=2,
                                      x=concentrations)
        # Write concentrations should generate a corresponding _doses_table
        rr.concentrations = concentrations
        # Test concentrations attribute
        numpy.testing.assert_array_equal(rr.concentrations,
                                         concentrations)
        # Test expression_levels attribute
        numpy.testing.assert_array_equal(rr.expression_levels,
                                         expression_levels)
        # Test doses table
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': concentrations,
             u'RR Expression (MEFL)': expression_levels},
            index=['R{:03d}'.format(i + 1) for i in range(11)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(rr._doses_table, df)
        pandas.util.testing.assert_frame_equal(rr.doses_table, df)

    def test_expression_levels_assignment(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Concentrations
        concentrations = numpy.logspace(numpy.log10(0.5),
                                        numpy.log10(500),
                                        11)
        expression_levels = self.hill(y0=10,
                                      dy=1000,
                                      K=50,
                                      n=2,
                                      x=concentrations)
        # Write concentrations should generate a corresponding _doses_table
        rr.expression_levels = expression_levels
        # Test concentrations attribute
        numpy.testing.assert_almost_equal(rr.concentrations,
                                          concentrations)
        # Test expression_levels attribute
        numpy.testing.assert_array_equal(rr.expression_levels,
                                         expression_levels)
        # Test doses table
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': concentrations,
             u'RR Expression (MEFL)': expression_levels},
            index=['R{:03d}'.format(i + 1) for i in range(11)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(rr._doses_table, df)
        pandas.util.testing.assert_frame_equal(rr.doses_table, df)

    def test_concentrations_assignment_custom_id(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2},
            id_prefix='RR',
            id_offset=24)
        # Concentrations
        concentrations = numpy.logspace(numpy.log10(0.5),
                                        numpy.log10(500),
                                        11)
        expression_levels = self.hill(y0=10,
                                      dy=1000,
                                      K=50,
                                      n=2,
                                      x=concentrations)
        # Write concentrations should generate a corresponding _doses_table
        rr.concentrations = concentrations
        # Test concentrations attribute
        numpy.testing.assert_array_equal(rr.concentrations,
                                         concentrations)
        # Test expression_levels attribute
        numpy.testing.assert_array_equal(rr.expression_levels,
                                         expression_levels)
        # Test doses table
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': concentrations,
             u'RR Expression (MEFL)': expression_levels},
            index=['RR{:03d}'.format(i + 24 + 1) for i in range(11)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(rr._doses_table, df)
        pandas.util.testing.assert_frame_equal(rr.doses_table, df)

    def test_expression_levels_assignment_custom_id(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2},
            id_prefix='RR',
            id_offset=24)
        # Concentrations
        concentrations = numpy.logspace(numpy.log10(0.5),
                                        numpy.log10(500),
                                        11)
        expression_levels = self.hill(y0=10,
                                      dy=1000,
                                      K=50,
                                      n=2,
                                      x=concentrations)
        # Write concentrations should generate a corresponding _doses_table
        rr.expression_levels = expression_levels
        # Test concentrations attribute
        numpy.testing.assert_almost_equal(rr.concentrations,
                                          concentrations)
        # Test expression_levels attribute
        numpy.testing.assert_array_equal(rr.expression_levels,
                                         expression_levels)
        # Test doses table
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': concentrations,
             u'RR Expression (MEFL)': expression_levels},
            index=['RR{:03d}'.format(i + 24 + 1) for i in range(11)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(rr._doses_table, df)
        pandas.util.testing.assert_frame_equal(rr.doses_table, df)

    def test_set_gradient_linear(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Set concentrations from gradient
        rr.set_gradient(min=30, max=1000, n=21, scale='linear')
        # Expected results
        expression_levels = numpy.linspace(30, 1000, 21)
        concentrations = self.hill_inverse(y0=10,
                                           dy=1000,
                                           K=50,
                                           n=2,
                                           y=expression_levels)
        # Test concentrations attribute
        numpy.testing.assert_array_equal(rr.expression_levels,
                                         expression_levels)
        numpy.testing.assert_array_equal(rr.concentrations,
                                         concentrations)
        # Check doses table
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': concentrations,
             u'RR Expression (MEFL)': expression_levels},
            index=['R{:03d}'.format(i + 1) for i in range(21)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(rr._doses_table, df)
        pandas.util.testing.assert_frame_equal(rr.doses_table, df)

    def test_set_gradient_linear_default(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Set concentrations from gradient
        rr.set_gradient(min=30, max=1000, n=21)
        # Expected results
        expression_levels = numpy.linspace(30, 1000, 21)
        concentrations = self.hill_inverse(y0=10,
                                           dy=1000,
                                           K=50,
                                           n=2,
                                           y=expression_levels)
        # Test concentrations attribute
        numpy.testing.assert_array_equal(rr.expression_levels,
                                         expression_levels)
        numpy.testing.assert_array_equal(rr.concentrations,
                                         concentrations)
        # Check doses table
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': concentrations,
             u'RR Expression (MEFL)': expression_levels},
            index=['R{:03d}'.format(i + 1) for i in range(21)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(rr._doses_table, df)
        pandas.util.testing.assert_frame_equal(rr.doses_table, df)

    def test_set_gradient_linear_min_is_y0(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Set concentrations from gradient
        rr.set_gradient(min=10, max=1000, n=21)
        # Expected results
        expression_levels = numpy.linspace(10, 1000, 21)
        concentrations = numpy.append(
            [0],
            self.hill_inverse(y0=10,
                              dy=1000,
                              K=50,
                              n=2,
                              y=expression_levels[1:]))
        # Test concentrations attribute
        numpy.testing.assert_array_equal(rr.expression_levels,
                                         expression_levels)
        numpy.testing.assert_array_equal(rr.concentrations,
                                         concentrations)
        # Check doses table
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': concentrations,
             u'RR Expression (MEFL)': expression_levels},
            index=['R{:03d}'.format(i + 1) for i in range(21)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(rr._doses_table, df)
        pandas.util.testing.assert_frame_equal(rr.doses_table, df)

    def test_set_gradient_linear_no_min(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Set concentrations from gradient
        rr.set_gradient(max=1000, n=21)
        # Expected results
        expression_levels = numpy.linspace(10, 1000, 21)
        concentrations = numpy.append(
            [0],
            self.hill_inverse(y0=10,
                              dy=1000,
                              K=50,
                              n=2,
                              y=expression_levels[1:]))
        # Test concentrations attribute
        numpy.testing.assert_array_equal(rr.expression_levels,
                                         expression_levels)
        numpy.testing.assert_array_equal(rr.concentrations,
                                         concentrations)
        # Check doses table
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': concentrations,
             u'RR Expression (MEFL)': expression_levels},
            index=['R{:03d}'.format(i + 1) for i in range(21)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(rr._doses_table, df)
        pandas.util.testing.assert_frame_equal(rr.doses_table, df)

    def test_set_gradient_linear_min_inducer(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Set concentrations from gradient
        rr.set_gradient(min_inducer=1., max=1000, n=21)
        # Expected results
        min_exp = self.hill(y0=10,
                            dy=1000,
                            K=50,
                            n=2,
                            x=1.)
        expression_levels = numpy.linspace(min_exp, 1000, 21)
        concentrations = self.hill_inverse(y0=10,
                                           dy=1000,
                                           K=50,
                                           n=2,
                                           y=expression_levels)
        # Test concentrations attribute
        numpy.testing.assert_array_equal(rr.expression_levels,
                                         expression_levels)
        numpy.testing.assert_array_equal(rr.concentrations,
                                         concentrations)
        # Check doses table
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': concentrations,
             u'RR Expression (MEFL)': expression_levels},
            index=['R{:03d}'.format(i + 1) for i in range(21)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(rr._doses_table, df)
        pandas.util.testing.assert_frame_equal(rr.doses_table, df)

    def test_set_gradient_linear_ignore_min_inducer(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Set concentrations from gradient
        # hill(1.) ~= 10.4 != 30.
        rr.set_gradient(min=30, min_inducer=1., max=1000, n=21)
        # Expected results
        expression_levels = numpy.linspace(30, 1000, 21)
        concentrations = self.hill_inverse(y0=10,
                                           dy=1000,
                                           K=50,
                                           n=2,
                                           y=expression_levels)
        # Test concentrations attribute
        numpy.testing.assert_array_equal(rr.expression_levels,
                                         expression_levels)
        numpy.testing.assert_array_equal(rr.concentrations,
                                         concentrations)
        # Check doses table
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': concentrations,
             u'RR Expression (MEFL)': expression_levels},
            index=['R{:03d}'.format(i + 1) for i in range(21)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(rr._doses_table, df)
        pandas.util.testing.assert_frame_equal(rr.doses_table, df)

    def test_set_gradient_linear_max_inducer(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Set concentrations from gradient
        rr.set_gradient(min=30, max_inducer=200, n=21)
        # Expected results
        max_exp = self.hill(y0=10,
                            dy=1000,
                            K=50,
                            n=2,
                            x=200.)
        expression_levels = numpy.linspace(30, max_exp, 21)
        concentrations = self.hill_inverse(y0=10,
                                           dy=1000,
                                           K=50,
                                           n=2,
                                           y=expression_levels)
        # Test concentrations attribute
        numpy.testing.assert_array_equal(rr.expression_levels,
                                         expression_levels)
        numpy.testing.assert_array_equal(rr.concentrations,
                                         concentrations)
        # Check doses table
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': concentrations,
             u'RR Expression (MEFL)': expression_levels},
            index=['R{:03d}'.format(i + 1) for i in range(21)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(rr._doses_table, df)
        pandas.util.testing.assert_frame_equal(rr.doses_table, df)

    def test_set_gradient_linear_ignore_max_inducer(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Set concentrations from gradient
        # hill(200) = 951.18 != 1000
        rr.set_gradient(min=30, max=1000, max_inducer=200, n=21)
        # Expected results
        expression_levels = numpy.linspace(30, 1000, 21)
        concentrations = self.hill_inverse(y0=10,
                                           dy=1000,
                                           K=50,
                                           n=2,
                                           y=expression_levels)
        # Test concentrations attribute
        numpy.testing.assert_array_equal(rr.expression_levels,
                                         expression_levels)
        numpy.testing.assert_array_equal(rr.concentrations,
                                         concentrations)
        # Check doses table
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': concentrations,
             u'RR Expression (MEFL)': expression_levels},
            index=['R{:03d}'.format(i + 1) for i in range(21)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(rr._doses_table, df)
        pandas.util.testing.assert_frame_equal(rr.doses_table, df)

    def test_set_gradient_linear_no_max_error(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Attempt to set gradient without specifying max value
        with self.assertRaises(ValueError):
            rr.set_gradient(min=30, n=21)

    def test_set_gradient_linear_out_of_range_error(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Attempt to set a valid expression level
        rr.set_gradient(min=10, max=1009.99, n=21)
        # Attempt to set invalid expression levels
        with self.assertRaises(ValueError):
            rr.set_gradient(min=10, max=1010, n=21)
        with self.assertRaises(ValueError):
            rr.set_gradient(min=10, max=1300, n=21)
        with self.assertRaises(ValueError):
            rr.set_gradient(min=9.99, max=1009.99, n=21)
        with self.assertRaises(ValueError):
            rr.set_gradient(min=0, max=1010, n=21)
        with self.assertRaises(ValueError):
            rr.set_gradient(min=0, max=1300, n=21)

    def test_set_gradient_linear_repeat(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Set concentrations from gradient
        rr.set_gradient(min=10, max=1000, n=12, n_repeat=3)
        # Expected results
        expression_levels = numpy.repeat(numpy.linspace(10, 1000, 4), 3)
        concentrations = numpy.append(
            [0, 0, 0],
            self.hill_inverse(y0=10,
                              dy=1000,
                              K=50,
                              n=2,
                              y=expression_levels[3:]))
        # Test concentrations attribute
        numpy.testing.assert_array_equal(rr.expression_levels,
                                         expression_levels)
        numpy.testing.assert_array_equal(rr.concentrations,
                                         concentrations)
        # Check doses table
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': concentrations,
             u'RR Expression (MEFL)': expression_levels},
            index=['R{:03d}'.format(i + 1) for i in range(12)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(rr._doses_table, df)
        pandas.util.testing.assert_frame_equal(rr.doses_table, df)

    def test_set_gradient_linear_repeat_error(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        with self.assertRaises(ValueError):
            rr.set_gradient(min=10, max=1000, n=11, n_repeat=3)

    def test_set_gradient_log(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Set concentrations from gradient
        rr.set_gradient(min=30, max=1000, n=21, scale='log')
        # Expected results
        expression_levels = numpy.logspace(numpy.log10(30),
                                           numpy.log10(1000),
                                           21)
        concentrations = self.hill_inverse(y0=10,
                                           dy=1000,
                                           K=50,
                                           n=2,
                                           y=expression_levels)
        # Test concentrations attribute
        numpy.testing.assert_array_equal(rr.expression_levels,
                                         expression_levels)
        numpy.testing.assert_array_equal(rr.concentrations,
                                         concentrations)
        # Check doses table
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': concentrations,
             u'RR Expression (MEFL)': expression_levels},
            index=['R{:03d}'.format(i + 1) for i in range(21)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(rr._doses_table, df)
        pandas.util.testing.assert_frame_equal(rr.doses_table, df)

    def test_set_gradient_log_min_is_y0(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Set concentrations from gradient
        rr.set_gradient(min=10, max=1000, n=21, scale='log')
        # Expected results
        expression_levels = numpy.logspace(numpy.log10(10),
                                           numpy.log10(1000),
                                           21)
        concentrations = numpy.append(
            [0],
            self.hill_inverse(y0=10,
                              dy=1000,
                              K=50,
                              n=2,
                              y=expression_levels[1:]))
        # Test concentrations attribute
        numpy.testing.assert_array_equal(rr.expression_levels,
                                         expression_levels)
        numpy.testing.assert_array_equal(rr.concentrations,
                                         concentrations)
        # Check doses table
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': concentrations,
             u'RR Expression (MEFL)': expression_levels},
            index=['R{:03d}'.format(i + 1) for i in range(21)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(rr._doses_table, df)
        pandas.util.testing.assert_frame_equal(rr.doses_table, df)

    def test_set_gradient_log_no_min(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Set concentrations from gradient
        rr.set_gradient(max=1000, n=21, scale='log')
        # Expected results
        expression_levels = numpy.logspace(numpy.log10(10),
                                           numpy.log10(1000),
                                           21)
        concentrations = numpy.append(
            [0],
            self.hill_inverse(y0=10,
                              dy=1000,
                              K=50,
                              n=2,
                              y=expression_levels[1:]))
        # Test concentrations attribute
        numpy.testing.assert_array_equal(rr.expression_levels,
                                         expression_levels)
        numpy.testing.assert_array_equal(rr.concentrations,
                                         concentrations)
        # Check doses table
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': concentrations,
             u'RR Expression (MEFL)': expression_levels},
            index=['R{:03d}'.format(i + 1) for i in range(21)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(rr._doses_table, df)
        pandas.util.testing.assert_frame_equal(rr.doses_table, df)

    def test_set_gradient_log_min_inducer(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Set concentrations from gradient
        rr.set_gradient(min_inducer=1., max=1000, n=21, scale='log')
        # Expected results
        min_exp = self.hill(y0=10,
                            dy=1000,
                            K=50,
                            n=2,
                            x=1.)
        expression_levels = numpy.logspace(numpy.log10(min_exp),
                                           numpy.log10(1000),
                                           21)
        concentrations = self.hill_inverse(y0=10,
                                           dy=1000,
                                           K=50,
                                           n=2,
                                           y=expression_levels)
        # Test concentrations attribute
        numpy.testing.assert_array_equal(rr.expression_levels,
                                         expression_levels)
        numpy.testing.assert_array_equal(rr.concentrations,
                                         concentrations)
        # Check doses table
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': concentrations,
             u'RR Expression (MEFL)': expression_levels},
            index=['R{:03d}'.format(i + 1) for i in range(21)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(rr._doses_table, df)
        pandas.util.testing.assert_frame_equal(rr.doses_table, df)

    def test_set_gradient_log_ignore_min_inducer(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Set concentrations from gradient
        # hill(1.) ~= 10.4 != 30.
        rr.set_gradient(min=30, min_inducer=1., max=1000, n=21, scale='log')
        # Expected results
        expression_levels = numpy.logspace(numpy.log10(30),
                                           numpy.log10(1000),
                                           21)
        concentrations = self.hill_inverse(y0=10,
                                           dy=1000,
                                           K=50,
                                           n=2,
                                           y=expression_levels)
        # Test concentrations attribute
        numpy.testing.assert_array_equal(rr.expression_levels,
                                         expression_levels)
        numpy.testing.assert_array_equal(rr.concentrations,
                                         concentrations)
        # Check doses table
        df = pandas.DataFrame(
            {u'IPTG Concentration (µM)': concentrations,
             u'RR Expression (MEFL)': expression_levels},
            index=['R{:03d}'.format(i + 1) for i in range(21)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(rr._doses_table, df)
        pandas.util.testing.assert_frame_equal(rr.doses_table, df)

    def test_set_gradient_bad_scale(self):
        rr = platedesign.inducer.ChemicalGeneExpression(
            name='RR',
            units='MEFL',
            inducer_name='IPTG',
            inducer_units=u'µM',
            hill_params={'y0': 10, 'dy':1000, 'K': 50, 'n': 2})
        # Attempt to set gradient without specifying max value
        with self.assertRaises(ValueError):
            rr.set_gradient(min=30, max=1000, n=21, scale='symlog')