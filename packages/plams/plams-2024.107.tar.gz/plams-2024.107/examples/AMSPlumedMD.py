#!/usr/bin/env amspython
import os

from scm.plams import *

"""
Example illustrating how to run AMS MD with
* AMS Restraints
* AMS EngineAddon WallPotential
* Plumed restraints

This example illustrates biased ReaxFF MD for the reaction H2CO3 -> H2O + CO2

Run with
$AMSBIN/amspython AMSPlumedMD.py
"""


def get_molecule():
    job = AMSJob.from_input(
        """
    system
      Atoms
                  O      -0.1009275285       1.5113007791      -0.4061554537 
                  C       0.0189044656       0.3835929386       0.1570043855
                  O       1.2796450751      -0.2325516597       0.3936038789
                  O      -1.0798994361      -0.4640886294       0.4005134306
                  H       1.7530114719      -0.6822230417      -0.3461237499
                  H      -1.8707340481      -0.5160303870      -0.1988424913
      End
    End
    """
    )
    return job.molecule[""]


def main():
    mol = get_molecule()
    # O(3) binds H(5), the other H is H(6)

    current_O3H6 = mol[3].distance_to(mol[6])
    target_O3H6 = 0.95

    current_O1C2 = mol[1].distance_to(mol[2])

    nsteps = 10000
    kappa = 500000.0

    os.environ["OMP_NUM_THREADS"] = "1"

    s = Settings()
    s.runscript.nproc = 1
    s.input.ReaxFF.ForceField = "CHO.ff"
    s.input.ams.Task = "MolecularDynamics"
    s.input.ams.MolecularDynamics.NSteps = nsteps
    s.input.ams.MolecularDynamics.Trajectory.SamplingFreq = 100
    s.input.ams.MolecularDynamics.InitialVelocities.Temperature = 200
    s.input.ams.MolecularDynamics.Thermostat.Temperature = 500
    s.input.ams.MolecularDynamics.Thermostat.Tau = 100
    s.input.ams.MolecularDynamics.Thermostat.Type = "Berendsen"

    # use an AMS restraint for one of the C-O bond lengths
    s.input.ams.Restraints.Distance = []
    s.input.ams.Restraints.Distance.append(f"1 2 {current_O1C2} 1.0")

    # use an AMS EngineAddon WallPotential to keep the molecules within a sphere of radius 6 angstrom
    s.input.ams.EngineAddons.WallPotential.Enabled = "Yes"
    s.input.ams.EngineAddons.WallPotential.Radius = 6.0

    # Plumed input, note that distances are given in nanometer so multiply by 0.1
    s.input.ams.MolecularDynamics.Plumed.Input = f"""
        DISTANCE ATOMS=3,6 LABEL=d36
        MOVINGRESTRAINT ARG=d36 STEP0=1 AT0={current_O3H6*0.1} KAPPA0={kappa} STEP1={nsteps} AT1={target_O3H6*0.1}
        PRINT ARG=d36 FILE=colvar-d36.dat STRIDE=20
        End
    """

    job = AMSJob(settings=s, molecule=mol, name="plumed-example")
    job.run()


if __name__ == "__main__":
    init()
    main()
    finish()
