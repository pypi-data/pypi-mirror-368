from scm.plams import PT, Molecule
import pytest


PT.set_connectors("Mg", 4)


@pytest.fixture
def m1(xyz_folder):
    return Molecule(xyz_folder / "chlorophyl1.xyz")


@pytest.fixture
def m2(xyz_folder):
    return Molecule(xyz_folder / "chlorophyl2.xyz")


def testYES(m1, m2):
    for i in range(2):
        assert m1.label(i) == m2.label(i)


def testNO(m1, m2):
    for i in range(2, 5):
        assert m1.label(i) != m2.label(i)
