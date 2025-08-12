# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
from pathlib import Path

import pytest
from pydefect.cli.vasp.get_defect_charge_state import \
    get_defect_charge_state
from pymatgen.core import Structure, Lattice
from pymatgen.io.vasp import Poscar, Potcar, Incar


# def test_get_defect_charge_state(tmpdir):
#     tmpdir.chdir()
#     structure = Structure(Lattice.cubic(10), ["H", "He"], [[0.0]*3, [0.5]*3])
#
#
#     Path("POTCAR").write_text(fake_potcar_str)
#     potcar = Potcar.from_file("POTCAR")
#     incar = Incar.from_string("NELECT = 1")
#     assert get_defect_charge_state(Poscar(structure), potcar, incar) == 2 - 1
#
#     structure = Structure(Lattice.cubic(10), ["H", "He", "H", "H"],
#                           [[0.0]*3, [0.2]*3, [0.4]*3, [0.6]*3])
#     with pytest.raises(ValueError):
#         get_defect_charge_state(Poscar(structure), potcar, incar)
#
#     incar = Incar.from_string("")
#     assert get_defect_charge_state(Poscar(structure), potcar, incar) == 0


