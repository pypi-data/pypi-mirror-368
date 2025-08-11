#!/usr/bin/env amspython
import matplotlib.pyplot as plt
import pyCRS

"""

This example uses the Property Prediction tool to estimate some properties for
a molecule represented by a SMILES string.

The vapor pressures are handled separately from other properties because vapor pressures are temperature-dependent.

Run this script using
$AMSBIN/amspython PropertyPrediction.py

"""


def single_compound_example():
    print("Single compound example for SMILES CCO")
    mol = pyCRS.Input.read_smiles("CCO")
    temperatures = [298.15, 308.15, 318.15]
    pyCRS.PropPred.estimate(mol, temperatures=temperatures)
    print("Boiling point: {:.2f} {}".format(mol.properties["boilingpoint"], pyCRS.PropPred.units["boilingpoint"]))
    print("Available properties: {}".format(pyCRS.PropPred.available_properties))
    # vapor pressures are handled separately -- as part of temperature-dependent properties
    print(f'{"Temperature":>15} {"Vapor Pressure":>15}')
    for i in range(len(temperatures)):
        print(
            f'{mol.properties_tdep["vaporpressure"][i][0]:15.2f} {mol.properties_tdep["vaporpressure"][i][1]:15.6e} {pyCRS.PropPred.units["vaporpressure"]}'
        )


def multi_compound_example():
    smiles_list = ["CCO", "CCOC", "OCCCN", "C", "C1=CC=C(C=C1)COCC2=CC=CC=C2"]
    mols = [pyCRS.Input.read_smiles(s) for s in smiles_list]
    for mol in mols:
        pyCRS.PropPred.estimate(mol, temperatures=list(range(280, 340, 10)))

    plot_vapor_pressures(mols, "vaporpressures.png")


def property_list_example():
    print("Using a specified list of properties only")
    mol = pyCRS.Input.read_smiles("CCCCO")
    pyCRS.PropPred.estimate(
        mol, ["boilingpoint", "criticaltemp", "density", "vaporpressure"], temperatures=[290, 300, 310, 320, 330]
    )

    print("Temperature-independent properties:")
    for k, v in mol.properties.items():
        print(f"{k:<15} {v:15.6e} {pyCRS.PropPred.units[k]}")
    print("\nTemperature-dependent properties")
    for k, vals in mol.properties_tdep.items():
        print(k)
        print(f'{"Temperature":>15} {"Vapor Pressure":>15}')
        for temp, val in vals:
            print(f"{temp:15.2f} {val:15.6e} {pyCRS.PropPred.units[k]}")


def plot_vapor_pressures(mols, filename: str):
    n = 2  # only show the first two

    plt.clf()
    for mol in mols[:n]:
        temperatures = [x[0] for x in mol.properties_tdep["vaporpressure"]]
        vaporpressures = [x[1] for x in mol.properties_tdep["vaporpressure"]]
        plt.plot(temperatures, vaporpressures, label=mol.smiles)
    plt.legend()
    plt.xlabel("Temperature (K)")
    plt.ylabel("Vapor pressure (bar)")
    plt.title("Estimated vapor pressures")
    plt.plot()
    plt.savefig(filename)


if __name__ == "__main__":
    single_compound_example()
    multi_compound_example()
    property_list_example()
