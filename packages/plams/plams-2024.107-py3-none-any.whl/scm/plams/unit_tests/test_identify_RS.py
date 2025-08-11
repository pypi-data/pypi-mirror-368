import pytest

from scm.plams import Molecule


@pytest.fixture
def m1(xyz_folder):
    return Molecule(xyz_folder / "RS1.xyz")


@pytest.fixture
def m2(xyz_folder):
    return Molecule(xyz_folder / "RS2.xyz")


def testYES(m1, m2):
    for i in range(3):
        assert m1.label(i) == m2.label(i)


def testNO(m1, m2):
    for i in range(3, 5):
        assert m1.label(i) != m2.label(i)
