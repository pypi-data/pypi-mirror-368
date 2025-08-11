import sys
from scm.plams import RKFTrajectoryFile, DCDTrajectoryFile
from scm.flexmd import pdb_from_plamsmol, PSFTopology


def main():
    """
    Main script
    """
    rkf = RKFTrajectoryFile("ams.rkf")
    mol = rkf.get_plamsmol()
    print("NSTeps: ", len(rkf))

    pdb = pdb_from_plamsmol(mol)
    psf = PSFTopology(pdb=pdb)
    psf.write_psf("ams.psf")

    dcd = DCDTrajectoryFile("ams.dcd", mode="wb")

    for i in range(len(rkf)):
        if i % 100 == 0:
            print(i)
        crd, cell = rkf.read_frame(i)
        mol.from_array(crd)
        mol.map_atoms_to_bonds()
        dcd.write_next(coords=mol.as_array(), cell=cell)


if __name__ == "__main__":
    main()
