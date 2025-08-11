from pathlib import Path
import pytest

from scm.plams import Molecule

PATH = Path(".") / "xyz"


@pytest.fixture
def m1(xyz_folder):
    return Molecule(xyz_folder / "CO_6_1.xyz")


@pytest.fixture
def m2(xyz_folder):
    return Molecule(xyz_folder / "CO_6_2.xyz")


@pytest.fixture
def n1(xyz_folder):
    return Molecule(xyz_folder / "CO_6_3.xyz")


@pytest.fixture
def n2(xyz_folder):
    return Molecule(xyz_folder / "CO_6_4.xyz")


@pytest.fixture
def n3(xyz_folder):
    return Molecule(xyz_folder / "CO_6_5.xyz")


def testYES(m1, m2, n1, n2, n3):
    for i in range(4):
        assert m1.label(i) == m2.label(i)
    for i in range(4):
        assert n1.label(i) == n2.label(i) == n3.label(i)


def testNO(m1, m2, n1, n2, n3):
    assert m1.label(4) != m2.label(4)
    assert n1.label(4) != n2.label(4)
    assert n1.label(4) != n3.label(4)
    assert n2.label(4) != n3.label(4)
