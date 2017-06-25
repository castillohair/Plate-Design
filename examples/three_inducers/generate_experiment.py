import platedesign

exp = platedesign.experiment.Experiment()
exp.n_replicates = 5
exp.randomize = True
exp.measurement_template = '../supporting_files/template_FlowCal.xlsx'

# Inducers
iptg = platedesign.inducer.ChemicalInducer(name='IPTG', units='uM')
iptg.stock_conc = 1e6
iptg.shot_vol = 5.
iptg.set_gradient(min=0.5,
                  max=500,
                  n=6,
                  scale='log',
                  use_zero=True,
                  n_repeat=2)
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

ligand = platedesign.inducer.ChemicalInducer(name='Ligand', units='uM')
ligand.stock_conc = 1e6
ligand.shot_vol = 5.
ligand.concentrations = [0, 500, 0, 500, 0, 500]
ligand.sync_shuffling(iptg)
exp.add_inducer(ligand)

# Plates 1 and 2: test strains
plate = platedesign.plate.Plate('P1', n_rows=4, n_cols=6)
plate.cell_strain_name = 'Test Strain 1'
plate.apply_inducer(inducer=iptg, apply_to='rows')
plate.apply_inducer(inducer=xyl, apply_to='cols')
plate.apply_inducer(inducer=ligand, apply_to='rows')
exp.add_plate(plate)

plate = platedesign.plate.Plate('P2', n_rows=4, n_cols=6)
plate.cell_strain_name = 'Test Strain 2'
plate.apply_inducer(inducer=iptg, apply_to='rows')
plate.apply_inducer(inducer=xyl, apply_to='cols')
plate.apply_inducer(inducer=ligand, apply_to='rows')
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
