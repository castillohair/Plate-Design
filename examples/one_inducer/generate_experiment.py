# -*- coding: UTF-8 -*-
import platedesign

exp = platedesign.experiment.Experiment()
exp.n_replicates = 5
exp.randomize_inducer = True
exp.randomize_plate = True
exp.plate_locations = ['Stack 1-1', 'Stack 1-2', 'Stack 1-3', 'Stack 1-4']
exp.measurement_template = '../supporting_files/template_FlowCal.xlsx'

# Inducers
iptg = platedesign.inducer.ChemicalInducer(name='IPTG', units=u'µM')
iptg.stock_conc = 1e6
iptg.shot_vol = 5.
iptg.set_gradient(min=0.5,
                  max=500,
                  n=12,
                  scale='log',
                  use_zero=True)
exp.add_inducer(iptg)

# Plates 1 and 2: test strains
plate = platedesign.plate.Plate('P1', n_rows=4, n_cols=6)
plate.cell_strain_name = 'Test Strain 1'
plate.samples_to_measure = 12
plate.total_media_vol = 16000.
plate.sample_media_vol = 500.
plate.cell_setup_method = 'fixed_volume'
plate.cell_predilution = 100
plate.cell_predilution_vol = 1000
plate.cell_shot_vol = 5
plate.apply_inducer(inducer=iptg, apply_to='wells')
exp.add_plate(plate)

plate = platedesign.plate.Plate('P2', n_rows=4, n_cols=6)
plate.cell_strain_name = 'Test Strain 2'
plate.samples_to_measure = 12
plate.total_media_vol = 16000.
plate.sample_media_vol = 500.
plate.cell_setup_method = 'fixed_volume'
plate.cell_shot_vol = 5
plate.apply_inducer(inducer=iptg, apply_to='wells')
exp.add_plate(plate)

# Plate 3: autofluorescence control strain
plate = platedesign.plate.Plate('P3', n_rows=4, n_cols=6)
plate.cell_strain_name = 'Autofluorescence Control Strain'
plate.samples_to_measure = 4
plate.total_media_vol = 16000.
plate.sample_media_vol = 500.
plate.cell_setup_method = 'fixed_od600'
plate.cell_predilution = 100
plate.cell_predilution_vol = 1000
plate.cell_initial_od600 = 1e-5
exp.add_plate(plate)

exp.generate()
