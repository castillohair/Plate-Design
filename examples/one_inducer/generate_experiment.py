import platedesign

exp = platedesign.experiment.Experiment()
exp.n_replicates = 5
exp.randomize = True
exp.measurement_template = 'template_FlowCal.xlsx'

# Inducers
iptg = platedesign.inducer.ChemicalInducer(name='IPTG', units='uM')
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
plate.samples_to_measure = 12
plate.media_vol = 16000.
plate.sample_vol = 500.
plate.metadata['Strain'] = 'Test Strain 1'
plate.apply_inducer(inducer=iptg, apply_to='wells')
exp.add_plate(plate)

plate = platedesign.plate.Plate('P2', n_rows=4, n_cols=6)
plate.samples_to_measure = 12
plate.media_vol = 16000.
plate.sample_vol = 500.
plate.metadata['Strain'] = 'Test Strain 2'
plate.apply_inducer(inducer=iptg, apply_to='wells')
exp.add_plate(plate)

# Plate 3: autofluorescence control strain
plate = platedesign.plate.Plate('P3', n_rows=4, n_cols=6)
plate.samples_to_measure = 4
plate.media_vol = 16000.
plate.sample_vol = 500.
plate.metadata['Strain'] = 'Autofluorescence Control Strain'
exp.add_plate(plate)

exp.generate()
