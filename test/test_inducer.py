"""
Unit tests for inducer classes

"""

import os
import random
import unittest

import numpy
import pandas

import platedesign
import platedesign.inducer

class TestChemicalInducer(unittest.TestCase):
    """
    Tests for the ChemicalInducer class.

    """

    def test_create(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')

    def test_default_attributes(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        # Default attributes
        self.assertEqual(iptg.name, 'IPTG')
        self.assertEqual(iptg.units, 'uM')
        self.assertEqual(iptg.id_prefix, 'I')
        self.assertEqual(iptg.id_offset, 0)
        # Default properties
        self.assertEqual(iptg.conc_header, "Concentration (uM)")
        # Default dilutions table
        df = pandas.DataFrame({'Concentration (uM)': [0]}, index=['I001'])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(iptg._dilutions, df)
        pandas.util.testing.assert_frame_equal(iptg.dilutions, df)

    def test_custom_attributes(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM',
            id_prefix='IP',
            id_offset=24)
        self.assertEqual(iptg.name, 'IPTG')
        self.assertEqual(iptg.units, 'uM')
        self.assertEqual(iptg.id_prefix, 'IP')
        self.assertEqual(iptg.id_offset, 24)
        # Test properties
        self.assertEqual(iptg.conc_header, "Concentration (uM)")
        # Test dilutions table
        df = pandas.DataFrame({'Concentration (uM)': [0]}, index=['IP025'])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(iptg._dilutions, df)
        pandas.util.testing.assert_frame_equal(iptg.dilutions, df)

    def test_conc_assignment(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        iptg.conc = numpy.linspace(0,1,10)
        # Test dilutions table
        df = pandas.DataFrame(
            {'Concentration (uM)': numpy.linspace(0,1,10)},
            index=['I{:03d}'.format(i + 1) for i in range(10)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(iptg._dilutions, df)
        pandas.util.testing.assert_frame_equal(iptg.dilutions, df)
        # Test conc attribute
        numpy.testing.assert_array_equal(iptg.conc, numpy.linspace(0,1,10))

    def test_set_gradient_linear(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        iptg.set_gradient(min=0, max=1, n=11)
        df = pandas.DataFrame(
            {'Concentration (uM)': numpy.linspace(0,1,11)},
            index=['I{:03d}'.format(i + 1) for i in range(11)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(iptg._dilutions, df)
        pandas.util.testing.assert_frame_equal(iptg.dilutions, df)

    def test_set_gradient_linear_repeat(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        iptg.set_gradient(min=0, max=1, n=12, n_repeat=3)
        df = pandas.DataFrame(
            {'Concentration (uM)': numpy.repeat(numpy.linspace(0,1,4), 3)},
            index=['I{:03d}'.format(i + 1) for i in range(12)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(iptg._dilutions, df)
        pandas.util.testing.assert_frame_equal(iptg.dilutions, df)

    def test_set_gradient_linear_repeat_error(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        with self.assertRaises(ValueError):
            iptg.set_gradient(min=0, max=1, n=11, n_repeat=3)

    def test_set_gradient_log(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        iptg.set_gradient(min=1e-6, max=1e-3, n=10, scale='log')
        df = pandas.DataFrame(
            {'Concentration (uM)': numpy.logspace(-6,-3,10)},
            index=['I{:03d}'.format(i + 1) for i in range(10)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(iptg._dilutions, df)
        pandas.util.testing.assert_frame_equal(iptg.dilutions, df)

    def test_set_gradient_log_repeat(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        iptg.set_gradient(min=1e-6, max=1e-3, n=12, scale='log', n_repeat=3)
        df = pandas.DataFrame(
            {'Concentration (uM)': numpy.repeat(numpy.logspace(-6,-3,4), 3)},
            index=['I{:03d}'.format(i + 1) for i in range(12)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(iptg._dilutions, df)
        pandas.util.testing.assert_frame_equal(iptg.dilutions, df)

    def test_set_gradient_log_zero(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        iptg.set_gradient(min=1e-6, max=1e-3, n=10, scale='log', use_zero=True)
        df = pandas.DataFrame(
            {'Concentration (uM)': numpy.append([0], numpy.logspace(-6,-3,9))},
            index=['I{:03d}'.format(i + 1) for i in range(10)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(iptg._dilutions, df)
        pandas.util.testing.assert_frame_equal(iptg.dilutions, df)

    def test_set_gradient_log_zero_repeat(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        iptg.set_gradient(min=1e-6,
                          max=1e-3,
                          n=12,
                          scale='log',
                          use_zero=True,
                          n_repeat=2)
        conc = numpy.repeat(numpy.append([0], numpy.logspace(-6,-3,5)), 2)
        df = pandas.DataFrame(
            {'Concentration (uM)': conc},
            index=['I{:03d}'.format(i + 1) for i in range(12)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(iptg._dilutions, df)
        pandas.util.testing.assert_frame_equal(iptg.dilutions, df)

    def test_set_gradient_scale_error(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        with self.assertRaises(ValueError):
            iptg.set_gradient(min=1e-6, max=1e-3, n=10, scale='symlog')

    def test_calculate_vol_no_rep(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        iptg.conc = numpy.linspace(0,1,10)
        iptg.inoculation_vol = 5.
        iptg.calculate_vol(n_samples=10, n_replicates=1, safety_factor=1.2)
        self.assertEqual(iptg.replicate_vol, None)
        self.assertEqual(iptg.total_vol, 60)

    def test_calculate_vol_rep(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        iptg.conc = numpy.linspace(0,1,10)
        iptg.inoculation_vol = 5.
        iptg.calculate_vol(n_samples=10, n_replicates=2, safety_factor=1.2)
        self.assertEqual(iptg.replicate_vol, 60)
        self.assertEqual(iptg.total_vol, 200)

    def test_calculate_recipe_error_1(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        iptg.set_gradient(min=1, max=500, n=12, scale='log', use_zero=True)
        # iptg.stock_conc = 1e6
        iptg.inoculation_vol = 5.
        iptg.sample_vol = 500.
        iptg.total_vol = 100.
        with self.assertRaises(AttributeError):
            iptg.calculate_recipe()

    def test_calculate_recipe_error_2(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        iptg.set_gradient(min=1, max=500, n=12, scale='log', use_zero=True)
        iptg.stock_conc = 1e6
        # iptg.inoculation_vol = 5.
        iptg.sample_vol = 500.
        iptg.total_vol = 100.
        with self.assertRaises(AttributeError):
            iptg.calculate_recipe()

    def test_calculate_recipe_error_3(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        iptg.set_gradient(min=1, max=500, n=12, scale='log', use_zero=True)
        iptg.stock_conc = 1e6
        iptg.inoculation_vol = 5.
        # iptg.sample_vol = 500.
        iptg.total_vol = 100.
        with self.assertRaises(AttributeError):
            iptg.calculate_recipe()

    def test_calculate_recipe_error_4(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        iptg.set_gradient(min=1, max=500, n=12, scale='log', use_zero=True)
        iptg.stock_conc = 1e6
        iptg.inoculation_vol = 5.
        iptg.sample_vol = 500.
        # iptg.total_vol = 100.
        with self.assertRaises(AttributeError):
            iptg.calculate_recipe()

    def test_calculate_recipe(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        iptg.set_gradient(min=1, max=500, n=12, scale='log', use_zero=True)
        iptg.stock_conc = 1e6
        iptg.inoculation_vol = 5.
        iptg.sample_vol = 500.
        iptg.total_vol = 100.
        iptg.calculate_recipe()
        # Make expected result by hand
        df = pandas.DataFrame(
            index=['I{:03d}'.format(i + 1) for i in range(12)])
        df.index.name='ID'
        df['Concentration (uM)'] = numpy.array(
            [0.,
             1e6*5./500./1000.*10./(10. + 90.),
             1e6*5./500./1000.*18.62/(18.62 + 81.4),
             1e6*5./500./100.*3.47/(3.47 + 96.5),
             1e6*5./500./100.*6.45/(6.45 + 93.6),
             1e6*5./500./100.*12.01/(12.01 + 88),
             1e6*5./500./10.*2.24/(2.24 + 97.8),
             1e6*5./500./10.*4.16/(4.16 + 95.8),
             1e6*5./500./10.*7.75/(7.75 + 92.2),
             1e6*5./500./10.*14.43/(14.43 + 85.6),
             1e6*5./500./1.*2.69/(2.69 + 97.3),
             1e6*5./500./1.*5./(5. + 95),
             ])
        df['Stock dilution'] = numpy.array(
            [0., 1000., 1000., 100., 100., 100.,
             10., 10., 10., 10., 1., 1.])
        df['Inducer volume (uL)'] = numpy.array(
            [0., 10., 18.62, 3.47, 6.45, 12.01,
             2.24, 4.16, 7.75, 14.43, 2.69, 5.0])
        df['Water volume (uL)'] = numpy.array(
            [100., 90., 81.4, 96.5, 93.6, 88.,
             97.8, 95.8, 92.2, 85.6, 97.3, 95.])
        pandas.util.testing.assert_frame_equal(iptg._dilutions, df)

    def test_save_files(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        iptg.set_gradient(min=1, max=500, n=12, scale='log', use_zero=True)
        iptg.stock_conc = 1e6
        iptg.inoculation_vol = 5.
        iptg.sample_vol = 500.
        iptg.total_vol = 100.
        iptg.calculate_recipe()
        iptg.save_files(file_name='test_file.xlsx', sheet_name='Test Sheet')
        # Open and check contents
        df_file = pandas.read_excel(
            'test_file.xlsx',
            sheet_name='Test Sheet',
            index_col='ID')
        # Make expected result by hand
        df = pandas.DataFrame(
            index=['I{:03d}'.format(i + 1) for i in range(12)])
        df.index.name='ID'
        df['Concentration (uM)'] = numpy.array(
            [0.,
             1e6*5./500./1000.*10./(10. + 90.),
             1e6*5./500./1000.*18.62/(18.62 + 81.4),
             1e6*5./500./100.*3.47/(3.47 + 96.5),
             1e6*5./500./100.*6.45/(6.45 + 93.6),
             1e6*5./500./100.*12.01/(12.01 + 88),
             1e6*5./500./10.*2.24/(2.24 + 97.8),
             1e6*5./500./10.*4.16/(4.16 + 95.8),
             1e6*5./500./10.*7.75/(7.75 + 92.2),
             1e6*5./500./10.*14.43/(14.43 + 85.6),
             1e6*5./500./1.*2.69/(2.69 + 97.3),
             1e6*5./500./1.*5./(5. + 95),
             ])
        df['Stock dilution'] = numpy.array(
            [0, 1000, 1000, 100, 100, 100,
             10, 10, 10, 10, 1, 1], dtype=numpy.int64)
        df['Inducer volume (uL)'] = numpy.array(
            [0., 10., 18.62, 3.47, 6.45, 12.01,
             2.24, 4.16, 7.75, 14.43, 2.69, 5.0])
        df['Water volume (uL)'] = numpy.array(
            [100., 90., 81.4, 96.5, 93.6, 88.,
             97.8, 95.8, 92.2, 85.6, 97.3, 95.])
        pandas.util.testing.assert_frame_equal(df_file, df)
        # Delete file
        os.remove('test_file.xlsx')

    def test_generate_shufflings(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        iptg.conc = numpy.linspace(0,1,10)
        # Generate shufflings
        random.seed(1)
        iptg.generate_shufflings(3)
        self.assertEqual(len(iptg.shufflings), 3)
        self.assertEqual(len(iptg.shufflings[0]), 10)
        self.assertEqual(len(iptg.shufflings[1]), 10)
        self.assertEqual(len(iptg.shufflings[2]), 10)
        self.assertEqual(iptg.shufflings[0], [8, 0, 3, 4, 5, 2, 9, 6, 7, 1])
        self.assertEqual(iptg.shufflings[1], [8, 1, 6, 4, 2, 9, 5, 3, 7, 0])
        self.assertEqual(iptg.shufflings[2], [2, 6, 4, 7, 1, 5, 3, 8, 0, 9])

    def test_shuffle_error_1(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        iptg.conc = numpy.linspace(0,1,10)
        # Generate shufflings and try to shuffle
        random.seed(1)
        iptg.generate_shufflings(3)
        with self.assertRaises(ValueError):
            iptg.shuffle(4)

    def test_shuffle_error_2(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        iptg.conc = numpy.linspace(0,1,10)
        random.seed(1)
        # Generate shufflings and try to shuffle
        iptg.generate_shufflings(3)
        with self.assertRaises(ValueError):
            iptg.shuffle(-1)

    def test_shuffle_no_shuffling(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        iptg.conc = numpy.linspace(0,1,10)
        # Shuffle without generating shufflings
        random.seed(1)
        # iptg.generate_shufflings(3)
        iptg.shuffle(2)
        # Test dilutions table
        df = pandas.DataFrame(
            {'Concentration (uM)': numpy.linspace(0,1,10)},
            index=['I{:03d}'.format(i + 1) for i in range(10)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(iptg._dilutions, df)
        pandas.util.testing.assert_frame_equal(iptg.dilutions, df)

    def test_shuffle(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        iptg.conc = numpy.linspace(0,1,10)
        # Shuffle
        random.seed(1)
        iptg.generate_shufflings(3)
        iptg.shuffle(2)
        # Test dilutions table
        df = pandas.DataFrame(
            {'Concentration (uM)': numpy.linspace(0,1,10)},
            index=['I{:03d}'.format(i + 1) for i in range(10)])
        df.index.name='ID'
        df_shuffled = df.iloc[[2, 6, 4, 7, 1, 5, 3, 8, 0, 9]]
        pandas.util.testing.assert_frame_equal(iptg._dilutions, df)
        pandas.util.testing.assert_frame_equal(iptg.dilutions, df_shuffled)

    def test_shuffle_restore(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        iptg.conc = numpy.linspace(0,1,10)
        # Shuffle
        random.seed(1)
        iptg.generate_shufflings(3)
        iptg.shuffle(2)
        iptg.shuffle(None)
        # Test dilutions table
        df = pandas.DataFrame(
            {'Concentration (uM)': numpy.linspace(0,1,10)},
            index=['I{:03d}'.format(i + 1) for i in range(10)])
        df.index.name='ID'
        pandas.util.testing.assert_frame_equal(iptg._dilutions, df)
        pandas.util.testing.assert_frame_equal(iptg.dilutions, df)

    def test_split_1(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        iptg.conc = numpy.linspace(0,1,10)
        iptg_split = iptg.split(1, split_shuffled=True)
        self.assertEqual(len(iptg_split), 1)
        pandas.util.testing.assert_frame_equal(iptg._dilutions,
                                               iptg_split[0]._dilutions)

    def test_split_2(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        iptg.conc = numpy.linspace(0,1,10)
        iptg_split = iptg.split(1, split_shuffled=False)
        self.assertEqual(len(iptg_split), 1)
        pandas.util.testing.assert_frame_equal(iptg._dilutions,
                                               iptg_split[0]._dilutions)

    def test_split_3(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        iptg.conc = numpy.linspace(0,1,12)
        iptg_split = iptg.split(3, split_shuffled=False)
        self.assertEqual(len(iptg_split), 3)
        pandas.util.testing.assert_frame_equal(iptg._dilutions.iloc[:4],
                                               iptg_split[0]._dilutions)
        pandas.util.testing.assert_frame_equal(iptg._dilutions.iloc[4:8],
                                               iptg_split[1]._dilutions)
        pandas.util.testing.assert_frame_equal(iptg._dilutions.iloc[8:12],
                                               iptg_split[2]._dilutions)
        self.assertEqual(iptg_split[0].current_shuffling, None)
        self.assertEqual(iptg_split[1].current_shuffling, None)
        self.assertEqual(iptg_split[2].current_shuffling, None)
        self.assertEqual(iptg_split[0].shufflings, None)
        self.assertEqual(iptg_split[1].shufflings, None)
        self.assertEqual(iptg_split[2].shufflings, None)
        self.assertEqual(iptg_split[0].id_offset, None)
        self.assertEqual(iptg_split[1].id_offset, None)
        self.assertEqual(iptg_split[2].id_offset, None)

    def test_split_4(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        iptg.conc = numpy.linspace(0,1,12)
        iptg_split = iptg.split(3, split_shuffled=True)
        self.assertEqual(len(iptg_split), 3)
        pandas.util.testing.assert_frame_equal(iptg._dilutions.iloc[:4],
                                               iptg_split[0]._dilutions)
        pandas.util.testing.assert_frame_equal(iptg._dilutions.iloc[4:8],
                                               iptg_split[1]._dilutions)
        pandas.util.testing.assert_frame_equal(iptg._dilutions.iloc[8:12],
                                               iptg_split[2]._dilutions)
        self.assertEqual(iptg_split[0].current_shuffling, None)
        self.assertEqual(iptg_split[1].current_shuffling, None)
        self.assertEqual(iptg_split[2].current_shuffling, None)
        self.assertEqual(iptg_split[0].shufflings, None)
        self.assertEqual(iptg_split[1].shufflings, None)
        self.assertEqual(iptg_split[2].shufflings, None)
        self.assertEqual(iptg_split[0].id_offset, None)
        self.assertEqual(iptg_split[1].id_offset, None)
        self.assertEqual(iptg_split[2].id_offset, None)

    def test_split_5(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        iptg.conc = numpy.linspace(0,1,12)
        # Shuffle
        random.seed(1)
        iptg.generate_shufflings(3)
        iptg.shuffle(2)
        # Split
        iptg_split = iptg.split(3, split_shuffled=True)
        # Check
        self.assertEqual(len(iptg_split), 3)

        pandas.util.testing.assert_frame_equal(iptg.dilutions.iloc[:4],
                                               iptg_split[0]._dilutions)
        pandas.util.testing.assert_frame_equal(iptg.dilutions.iloc[4:8],
                                               iptg_split[1]._dilutions)
        pandas.util.testing.assert_frame_equal(iptg.dilutions.iloc[8:12],
                                               iptg_split[2]._dilutions)

        pandas.util.testing.assert_frame_equal(iptg.dilutions.iloc[:4],
                                               iptg_split[0].dilutions)
        pandas.util.testing.assert_frame_equal(iptg.dilutions.iloc[4:8],
                                               iptg_split[1].dilutions)
        pandas.util.testing.assert_frame_equal(iptg.dilutions.iloc[8:12],
                                               iptg_split[2].dilutions)

        pandas.util.testing.assert_frame_equal(iptg._dilutions.iloc[[6, 10, 8, 7]],
                                               iptg_split[0].dilutions)
        pandas.util.testing.assert_frame_equal(iptg._dilutions.iloc[[5, 9, 1, 0]],
                                               iptg_split[1].dilutions)
        pandas.util.testing.assert_frame_equal(iptg._dilutions.iloc[[3, 2, 4, 11]],
                                               iptg_split[2].dilutions)

        self.assertEqual(iptg_split[0].current_shuffling, None)
        self.assertEqual(iptg_split[1].current_shuffling, None)
        self.assertEqual(iptg_split[2].current_shuffling, None)
        self.assertEqual(iptg_split[0].shufflings, None)
        self.assertEqual(iptg_split[1].shufflings, None)
        self.assertEqual(iptg_split[2].shufflings, None)
        self.assertEqual(iptg_split[0].id_offset, None)
        self.assertEqual(iptg_split[1].id_offset, None)
        self.assertEqual(iptg_split[2].id_offset, None)

    def test_split_6(self):
        iptg = platedesign.inducer.ChemicalInducer(
            name='IPTG',
            units='uM')
        iptg.conc = numpy.linspace(0,1,12)
        # Shuffle
        random.seed(1)
        iptg.generate_shufflings(3)
        iptg.shuffle(2)
        # Split
        iptg_split = iptg.split(3, split_shuffled=False)
        # Check
        self.assertEqual(len(iptg_split), 3)

        pandas.util.testing.assert_frame_equal(iptg._dilutions.iloc[:4],
                                               iptg_split[0]._dilutions)
        pandas.util.testing.assert_frame_equal(iptg._dilutions.iloc[4:8],
                                               iptg_split[1]._dilutions)
        pandas.util.testing.assert_frame_equal(iptg._dilutions.iloc[8:12],
                                               iptg_split[2]._dilutions)

        pandas.util.testing.assert_frame_equal(iptg._dilutions.iloc[:4],
                                               iptg_split[0].dilutions)
        pandas.util.testing.assert_frame_equal(iptg._dilutions.iloc[4:8],
                                               iptg_split[1].dilutions)
        pandas.util.testing.assert_frame_equal(iptg._dilutions.iloc[8:12],
                                               iptg_split[2].dilutions)

        self.assertEqual(iptg_split[0].current_shuffling, None)
        self.assertEqual(iptg_split[1].current_shuffling, None)
        self.assertEqual(iptg_split[2].current_shuffling, None)
        self.assertEqual(iptg_split[0].shufflings, None)
        self.assertEqual(iptg_split[1].shufflings, None)
        self.assertEqual(iptg_split[2].shufflings, None)
        self.assertEqual(iptg_split[0].id_offset, None)
        self.assertEqual(iptg_split[1].id_offset, None)
        self.assertEqual(iptg_split[2].id_offset, None)
