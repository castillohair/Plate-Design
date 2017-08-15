# -*- coding: UTF-8 -*-
import platedesign

exp = platedesign.experiment.Experiment()
exp.n_replicates = 5
exp.randomize = True
exp.measurement_template = '../supporting_files/template_FlowCal.xlsx'
exp.plate_measurements = ['Final OD600', 'Incubation time (min)']

# Inducers
rr = platedesign.inducer.ChemicalGeneExpression(
  name='RR',
  units='MEFL',
  inducer_name='IPTG',
  inducer_units=u'µM',
  hill_params={'y0': 1e1,
               'dy': 3000.,
               'K': 40.,
               'n': 1.8})
rr.stock_conc = 1e6
rr.shot_vol = 5.
rr.set_gradient(n=6, max_inducer=500., scale='log')
exp.add_inducer(rr)

sk = platedesign.inducer.ChemicalGeneExpression(
  name='SK',
  units='MEFL',
  inducer_name='Xylose',
  inducer_units='%',
  hill_params={'y0': 5.,
               'dy': 1000.,
               'K': 0.086,
               'n': 1.3})
sk.stock_conc = 50.
sk.shot_vol = 5.
sk.set_gradient(n=4, max_inducer=0.5, scale='log')
exp.add_inducer(sk)

# Plates 1 and 2: test strains
plate = platedesign.plate.Plate('P1', n_rows=4, n_cols=6)
plate.cell_strain_name = 'Test Strain 1'
plate.apply_inducer(inducer=rr, apply_to='rows')
plate.apply_inducer(inducer=sk, apply_to='cols')
exp.add_plate(plate)

plate = platedesign.plate.Plate('P2', n_rows=4, n_cols=6)
plate.cell_strain_name = 'Test Strain 2'
plate.apply_inducer(inducer=rr, apply_to='rows')
plate.apply_inducer(inducer=sk, apply_to='cols')
exp.add_plate(plate)

# Plate 3: autofluorescence control strain
plate = platedesign.plate.Plate('P3', n_rows=4, n_cols=6)
plate.cell_strain_name = 'Autofluorescence Control Strain'
plate.samples_to_measure = 4
exp.add_plate(plate)

# Add common settings to plates
for plate in exp.plates:
    plate.media_vol = 16000.
    plate.sample_vol = 500.
    plate.cell_setup_method = 'fixed_od600'
    plate.cell_predilution = 100
    plate.cell_predilution_vol = 1000
    plate.cell_initial_od600 = 1e-5

exp.generate()
