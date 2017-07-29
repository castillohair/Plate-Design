# -*- coding: UTF-8 -*-
"""
Unit tests for inducer classes

"""

import os
import random
import shutil
import unittest

import numpy
import pandas

import platedesign

def _round_sigfig(a, n=1):
    """
    Round numpy array to specified number of significant digits.

    """
    a_nz_ind = numpy.nonzero(a)
    a_nz = a[a_nz_ind]
    e = numpy.ceil(numpy.log10(a_nz))
    m = a_nz/(10**e)
    r = numpy.round(m, decimals=n)
    a_rounded = a.copy()
    a_rounded[a_nz_ind] = r*(10**e)
    return a_rounded

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
        file_name = os.path.join(self.temp_dir, 'IPTG.xlsx')
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
