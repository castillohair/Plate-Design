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
                  n=6,
                  scale='log',
                  use_zero=True)
exp.add_inducer(iptg)

xyl = platedesign.inducer.ChemicalInducer(name='Xylose', units='%')
xyl.stock_conc = 50.
xyl.shot_vol = 5.
xyl.set_gradient(min=5e-3,
                 max=0.5,
                 n=4,
                 scale='log',
                 use_zero=True)
exp.add_inducer(xyl)

# Plates 1 and 2: test strains
plate = platedesign.plate.Plate('P1', n_rows=4, n_cols=6)
plate.media_vol = 16000.
plate.sample_vol = 500.
plate.metadata['Strain'] = 'Test Strain 1'
exp.add_plate(plate)
exp.apply_inducer(plate=plate, inducer=iptg, apply_to='rows')
exp.apply_inducer(plate=plate, inducer=xyl, apply_to='cols')

plate = platedesign.plate.Plate('P2', n_rows=4, n_cols=6)
plate.media_vol = 16000.
plate.sample_vol = 500.
plate.metadata['Strain'] = 'Test Strain 2'
exp.add_plate(plate)
exp.apply_inducer(plate=plate, inducer=iptg, apply_to='rows')
exp.apply_inducer(plate=plate, inducer=xyl, apply_to='cols')

# Plate 3: autofluorescence control strain
plate = platedesign.plate.Plate('P3', n_rows=4, n_cols=6)
plate.media_vol = 16000.
plate.sample_vol = 500.
plate.samples_to_measure = 4
plate.metadata['Strain'] = 'Autofluorescence Control Strain'
exp.add_plate(plate)

exp.generate()
