import pytest

from scm.plams import Molecule


@pytest.fixture
def m1(xyz_folder):
    return Molecule(xyz_folder / "CO_flat4_1.xyz")


@pytest.fixture
def m2(xyz_folder):
    return Molecule(xyz_folder / "CO_flat4_2.xyz")


@pytest.fixture
def m3(xyz_folder):
    return Molecule(xyz_folder / "CO_flat4_3.xyz")


@pytest.fixture
def m4(xyz_folder):
    return Molecule(xyz_folder / "CO_flat4_4.xyz")


def testYES(m1, m2, m3, m4):
    for i in range(4):
        assert m1.label(i) == m2.label(i)
    for i in range(4):
        assert m3.label(i) == m4.label(i)


def testNO(m1, m2, m3, m4):
    assert m1.label(4) != m2.label(4)
    assert m3.label(4) != m4.label(4)
