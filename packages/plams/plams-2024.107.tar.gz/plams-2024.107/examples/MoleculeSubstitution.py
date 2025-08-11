#!/usr/bin/env amspython
from scm.plams import *

"""
Example illustrating the PLAMS Molecule.substitute() method

See the documentation for Molecule.substitute() for details

Here, an auxiliary class MoleculeConnector is defined for easier use.

Run this example as:
$AMSBIN/amspython MoleculeSubstitution.py
"""


class MoleculeConnector:
    def __init__(self, molecule, connector, name="molecule"):
        self.name = name
        self.molecule = molecule
        self.connector = connector  # 2-tuple of integers, unlike the Molecule.substitute() method which uses two atoms

    def __str__(self):
        return f"""
Name: {self.name}
{self.molecule}
Connector: {self.connector}. This means that when substitution is performed atom {self.connector[0]} will be kept in the substituted molecule. Atom {self.connector[1]}, and anything connected to it, will NOT be kept.
        """


def substitute(substrate: MoleculeConnector, ligand: MoleculeConnector):
    """
    Returns: Molecule with the ligand added to the substrate, replacing the respective connector bonds.
    """
    molecule = substrate.molecule.copy()
    molecule.substitute(
        connector=(molecule[substrate.connector[0]], molecule[substrate.connector[1]]),
        ligand=ligand.molecule,
        ligand_connector=(ligand.molecule[ligand.connector[0]], ligand.molecule[ligand.connector[1]]),
    )
    return molecule


def main():
    benzene = from_smiles("c1ccccc1", forcefield="uff")
    # in the molecule you need to define which bond to cleave
    # to find out, run for example
    # benzene.write('benzene.xyz')
    # then open benzene.xyz in the AMS GUI and find that atoms 6 (C) and 12 (H) are bonded.
    # choose this bond to cleave
    substrate = MoleculeConnector(
        benzene, (6, 12), "phenyl"
    )  # benzene becomes phenyl when bond between atoms 6,12 is cleaved
    print("Substrate")
    print(substrate)

    # similarly for the ligand, if you do not know which bond to cleave, write the molecule to a .xyz file and find out
    ligands = [
        MoleculeConnector(from_smiles("[C-]#[NH+]", forcefield="uff"), (2, 3), "isocyanide"),  # bond to H cleaved
        MoleculeConnector(from_smiles("O=NO", forcefield="uff"), (3, 4), "nitrite"),  # bond to H cleaved
        MoleculeConnector(from_smiles("Cl", forcefield="uff"), (1, 2), "chloride"),  # bond to H cleaved
        MoleculeConnector(from_smiles("c1ccccc1", forcefield="uff"), (6, 12), "phenyl"),  # bond to H cleave H
    ]

    for ligand in ligands:
        print("New ligand:")
        print(ligand)
        mol = substitute(substrate, ligand)
        mol.delete_all_bonds()  # use engine bond guessing
        # the preoptimize() function requires AMS2023 or later
        # mol = preoptimize(mol, model='UFF')
        fname = f"{substrate.name}--{ligand.name}.xyz"
        print("Writing to:")
        print(fname)
        mol.write(fname)
        print("--------")
        print("--------")


if __name__ == "__main__":
    main()
