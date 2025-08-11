#!/usr/bin/env amspython
from scm.plams import *


def main():
    mol = packmol(from_smiles("CCO"), density=0.8, n_molecules=4)  # 4 ethanol molecules in cubic box

    # Start by running UFF with Berendsen thermostat
    s = Settings()
    s.runscript.nproc = 1
    s.input.forcefield.type = "UFF"
    pre_eq = AMSNVTJob(
        settings=s, molecule=mol, name="pre_eq", temperature=400, timestep=1.0, thermostat="berendsen", nsteps=5
    )
    assert pre_eq.settings.input.ams.MolecularDynamics.Thermostat.Type == "berendsen"  # explicitly set above
    assert (
        pre_eq.settings.input.ams.MolecularDynamics.Thermostat.Tau == 400
    )  # default 400 * timestep if not set explicitly
    pre_eq.run()

    # Then switch to GAFF with an NHC thermostat
    s.input.forcefield.type = "GAFF"
    s.input.forcefield.antechamberintegration = "Yes"
    eq = AMSNVTJob.restart_from(
        pre_eq, settings=s, name="eq", nsteps=100, thermostat="NHC", samplingfreq=10, writevelocities=True
    )
    assert eq.settings.input.ams.MolecularDynamics.Thermostat.Type == "NHC"  # explicitly set above
    assert eq.settings.input.ams.MolecularDynamics.TimeStep == 1.0  # inherited from pre_eq
    eq.run()

    # Launch NVE simulation from some frames (structures+velocities) of the previous NVT simulation (still using GAFF)
    for frame in [1, 4, 7]:
        nvejob = AMSNVEJob.restart_from(eq, name=f"nve{frame}", frame=frame, nsteps=10, samplingfreq=1)
        assert "Thermostat" not in nvejob.settings.input.ams.MolecularDynamics
        nvejob.run()

    # Also run an NPT simulation at a pressure of 2 bar
    npt = AMSNPTJob.restart_from(
        eq, name="npt", nsteps=50, samplingfreq=10, pressure=2, thermostat="NHC", barostat="MTK"
    )
    assert npt.settings.input.ams.MolecularDynamics.Thermostat.Temperature == 400  # inherited
    npt.run()

    # continue NVT
    nvt_from_npt = AMSNVTJob.restart_from(npt, name="nvt_from_npt")
    assert "Barostat" not in nvt_from_npt.settings.input.ams.MolecularDynamics
    assert nvt_from_npt.settings.input.ams.MolecularDynamics.NSteps == 50  # inherited
    nvt_from_npt.run()

    # NVE from NPT
    nve_from_npt = AMSNVEJob.restart_from(npt, name="nve_from_npt")
    assert "Barostat" not in nve_from_npt.settings.input.ams.MolecularDynamics
    assert "Thermostat" not in nve_from_npt.settings.input.ams.MolecularDynamics
    assert nve_from_npt.settings.input.ams.MolecularDynamics.NSteps == 50  # inherited
    nve_from_npt.run()

    # NVE with random initial velocities
    nve_clean = AMSNVEJob(name="nve_clean", settings=s, molecule=mol, velocities=200, nsteps=20)
    nve_clean.run()


if __name__ == "__main__":
    init()
    main()
    finish()
