# -*- coding: UTF-8 -*-
import platedesign

exp = platedesign.experiment.Experiment()
exp.n_replicates = 3
exp.n_replicates_extra_inducer = 2
exp.plate_resources['Location'] = ['Stack 1-1',
                                   'Stack 1-2',
                                   'Stack 1-3',
                                   'Stack 1-4',
                                   'Stack 2-1',
                                   'Stack 2-2',
                                   'Stack 2-3',
                                   'Stack 2-4']
exp.randomize_inducers = True
exp.randomize_plate_resources = True
exp.measurement_template = '../supporting_files/template_FlowCal.xlsx'
exp.measurement_order = 'Location'
exp.plate_measurements = ['Final OD600', 'Incubation time (min)']
exp.replicate_measurements = ['Date', 'Run by']

# Inducers
iptg = platedesign.inducer.ChemicalInducer(name='IPTG', units=u'µM')
iptg.stock_conc = 1e6
iptg.shot_vol = 5.
iptg.set_gradient(min=0.5,
                  max=500,
                  n=8,
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

# Plate array for test strain
platearray = platedesign.plate.PlateArray(
    'PA1',
    array_n_rows=2,
    array_n_cols=2,
    plate_names=['P{}'.format(i+1) for i in range(4)],
    plate_n_rows=4,
    plate_n_cols=6)
platearray.cell_strain_name = 'Test Strain 1'
platearray.total_media_vol = 16000.*8
platearray.apply_inducer(inducer=xyl, apply_to='rows')
platearray.apply_inducer(inducer=iptg, apply_to='cols')
exp.add_plate(platearray)

# Plate for autofluorescence control strain
plate = platedesign.plate.Plate('P9', n_rows=4, n_cols=6)
plate.cell_strain_name = 'Autofluorescence Control Strain'
plate.samples_to_measure = 4
plate.total_media_vol = 16000.
exp.add_plate(plate)

# Specify media and cell setup parameters
for plate in exp.plates:
    plate.sample_media_vol = 500.
    plate.cell_setup_method = 'fixed_dilution'
    plate.cell_predilution = 100
    plate.cell_predilution_vol = 300
    plate.cell_total_dilution = 1e5

exp.generate()
