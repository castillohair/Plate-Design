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
                  n=16,
                  scale='log',
                  use_zero=True)
exp.add_inducer(iptg)

xyl = platedesign.inducer.ChemicalInducer(name='Xylose', units='%')
xyl.stock_conc = 50.
xyl.shot_vol = 5.
xyl.set_gradient(min=5e-3,
                 max=0.5,
                 n=12,
                 n_repeat=2,
                 scale='log',
                 use_zero=True)
exp.add_inducer(xyl)

# Plate for autofluorescence control strain
plate = platedesign.plate.Plate('P9', n_rows=4, n_cols=6)
plate.samples_to_measure = 4
plate.media_vol = 16000.
plate.sample_vol = 500.
plate.metadata['Strain'] = 'Autofluorescence Control Strain'
exp.add_plate(plate)

# Plate array
platearray = platedesign.plate.PlateArray(
    'PA1',
    array_n_rows=4,
    array_n_cols=2,
    plate_names=['P{}'.format(i+1) for i in range(8)],
    plate_n_rows=4,
    plate_n_cols=6)
platearray.media_vol = 16000.*8
platearray.sample_vol = 500.
platearray.metadata['Strain'] = 'Test Strain 1'
platearray.apply_inducer(inducer=xyl, apply_to='rows')
platearray.apply_inducer(inducer=iptg, apply_to='cols')
exp.add_plate(platearray)

exp.generate()
