# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
from pathlib import Path

import pytest
from pydefect.analyzer.band_edge_states import EdgeInfo, BandEdgeOrbitalInfos, \
    PerfectBandEdgeState, OrbitalInfo, BandEdgeStates, BandEdgeState, \
    LocalizedOrbital
from pydefect.analyzer.defect_charge_info import DefectChargeInfo
from pydefect.analyzer.make_band_edge_states import make_band_edge_states, \
    orbital_diff, num_electron_in_cbm, num_hole_in_vbm


@pytest.fixture
def p_edge_state():
    vbm_info = EdgeInfo(band_idx=10, kpt_coord=(0.0, 0.0, 0.0),
                        orbital_info=OrbitalInfo(energy=-1.0, orbitals={"Mn": [0.5, 0.6, 0.0, 0.0], "O": [0.0, 0.0, 0.0, 0.0]}, occupation=1.0, participation_ratio=0.1))
    cbm_info = EdgeInfo(band_idx=11, kpt_coord=(0.0, 0.0, 0.0),
                        orbital_info=OrbitalInfo(energy=1.0, orbitals={"Mn": [0.0, 0.0, 0.0, 0.0], "O": [0.1, 0.2, 0.0, 0.0]}, occupation=0.0, participation_ratio=0.1))
    return PerfectBandEdgeState(vbm_info=vbm_info, cbm_info=cbm_info)


@pytest.fixture
def orb_infos():
    orbital_infos = [[[
        OrbitalInfo(energy=-1.1, orbitals={"Mn": [0.5, 0.6, 0.0, 0.0],
                                           "O": [0.0, 0.0, 0.0, 0.0]},
                    occupation=1.0, participation_ratio=0.1),
        OrbitalInfo(energy=-0.9, orbitals={"Mn": [0.5, 0.7, 0.0, 0.0],
                                           "O": [0.0, 0.0, 0.0, 0.0]},
                    occupation=1.0, participation_ratio=0.1),  # vbm
        OrbitalInfo(energy=0.0,  orbitals={"Mn": [0.1, 0.2, 0.0, 0.0],
                                           "O": [0.3, 0.4, 0.0, 0.0]},
                    occupation=1.0, participation_ratio=0.1),  # in-gap
        OrbitalInfo(energy=1.0,  orbitals={"Mn": [0.5, 0.8, 0.0, 0.0],
                                           "O": [0.0, 0.0, 0.0, 0.0]},
                    occupation=0.05, participation_ratio=0.1),  # in-gap
        OrbitalInfo(energy=1.2,  orbitals={"Mn": [0.0, 0.0, 0.0, 0.0],
                                           "O": [0.1, 0.3, 0.0, 0.0]},
                    occupation=0.02, participation_ratio=0.1),
        OrbitalInfo(energy=1.2,  orbitals={"Mn": [0.0, 0.0, 0.0, 0.0],
                                           "O": [0.1, 0.3, 0.0, 0.0]},
                    occupation=0.01, participation_ratio=0.1)]]]  # cbm
    return BandEdgeOrbitalInfos(kpt_coords=[(0.0, 0.0, 0.0)],
                                kpt_weights=[1.0],
                                orbital_infos=orbital_infos,
                                lowest_band_index=8,
                                fermi_level=0.5)


def test_num_electron_in_cbm(mocker):
    mock1 = mocker.Mock()
    mock2 = mocker.Mock()
    mock3 = mocker.Mock()
    mock4 = mocker.Mock()
    mock1.occupation = 0.1
    mock2.occupation = 0.2
    mock3.occupation = 0.3
    mock4.occupation = 0.4
    orb_info_by_spin = [[mock1, mock2], [mock3, mock4]]  # k-idx, band-idx
    actual = num_electron_in_cbm(orb_info_by_spin, cbm_idx=1, weights=[0.1, 0.9])
    expected = 0.1 * 0.2 + 0.9 * 0.4
    assert actual == pytest.approx(expected)

    actual = num_electron_in_cbm(orb_info_by_spin, cbm_idx=0, weights=[0.1, 0.9])
    expected = 0.1 * (0.1 + 0.2) + 0.9 * (0.3 + 0.4)
    assert actual == pytest.approx(expected)


def test_num_hole_in_vbm(mocker):
    mock1 = mocker.Mock()
    mock2 = mocker.Mock()
    mock3 = mocker.Mock()
    mock4 = mocker.Mock()
    mock1.occupation = 0.1
    mock2.occupation = 0.2
    mock3.occupation = 0.3
    mock4.occupation = 0.4
    orb_info_by_spin = [[mock1, mock2], [mock3, mock4]]  # k-idx, band-idx
    actual = num_hole_in_vbm(orb_info_by_spin, vbm_idx=0, weights=[0.1, 0.9])
    expected = 0.1 * (1 - 0.1) + 0.9 * (1 - 0.3)
    assert actual == pytest.approx(expected)

    actual = num_hole_in_vbm(orb_info_by_spin, vbm_idx=1, weights=[0.1, 0.9])
    expected = 0.1 * (2 - 0.1 - 0.2) + 0.9 * (2 - 0.3 - 0.4)
    assert actual == pytest.approx(expected)


@pytest.fixture
def band_edge_states():
    vbm_info = EdgeInfo(band_idx=9, kpt_coord=(0.0, 0.0, 0.0),
                        orbital_info=OrbitalInfo(
                            energy=-0.9, orbitals={"Mn": [0.5, 0.7, 0.0, 0.0],
                                                   "O": [0.0, 0.0, 0.0, 0.0]},
                            occupation=1.0, participation_ratio=0.1))
    cbm_info = EdgeInfo(band_idx=12, kpt_coord=(0.0, 0.0, 0.0),
                        orbital_info=OrbitalInfo(
                            energy=1.2, orbitals={"Mn": [0.0, 0.0, 0.0, 0.0],
                                                  "O": [0.1, 0.3, 0.0, 0.0]},
                            occupation=0.02, participation_ratio=0.1))
    localized_orb_1 = LocalizedOrbital(
        band_idx=10, ave_energy=0.0, occupation=1.0,
        orbitals={"Mn": [0.1, 0.2, 0.0, 0.0], "O": [0.3, 0.4, 0.0, 0.0]},
        participation_ratio=0.1)
    localized_orb_2 = LocalizedOrbital(
        band_idx=11, ave_energy=1.0, occupation=0.05,
        orbitals={"Mn": [0.5, 0.8, 0.0, 0.0], "O": [0.0, 0.0, 0.0, 0.0]},
        participation_ratio=0.1)
    return BandEdgeStates(
        states=[BandEdgeState(vbm_info=vbm_info,
                              cbm_info=cbm_info,
                              vbm_orbital_diff=0.09999999999999998,
                              cbm_orbital_diff=0.09999999999999998,
                              localized_orbitals=[localized_orb_1,
                                                  localized_orb_2],
                              vbm_hole_occupation=0.0,
                              cbm_electron_occupation=0.03
                              )])


def test_make_band_edge_state(p_edge_state, orb_infos, band_edge_states):
    actual = make_band_edge_states(orb_infos, p_edge_state)
    assert actual == band_edge_states


def test_make_band_edge_state_w_defect_charge_info(p_edge_state, orb_infos, mocker):
    defect_charge_info = mocker.Mock()
    defect_charge_info.localized_orbitals.return_value = [[9]]
    actual = make_band_edge_states(orb_infos, p_edge_state, defect_charge_info)
    expected = EdgeInfo(band_idx=8, kpt_coord=(0.0, 0.0, 0.0),
                        orbital_info=OrbitalInfo(
                            energy=-1.1, orbitals={"Mn": [0.5, 0.6, 0.0, 0.0],
                                                   "O": [0.0, 0.0, 0.0, 0.0]},
                            occupation=1.0, participation_ratio=0.1))
    assert actual.states[0].vbm_info == expected


def test_make_band_edge_state_wo_participation_ratio(
        p_edge_state, orb_infos, band_edge_states):
    # in-gap participation ratio is set to None
    orb_infos.orbital_infos[0][0][2].participation_ratio = None
    band_edge_states.states[0].localized_orbitals[0].participation_ratio = None
    actual = make_band_edge_states(orb_infos, p_edge_state)
    assert actual == band_edge_states


def test_orbital_diff():
    orb_1 = {"Mn": [0.1, 0.0, 0.0, 0.0]}
    orb_2 = {"Mn": [0.0, 0.1, 0.0, 0.0]}
    assert orbital_diff(orb_1, orb_2) == 0.2

    orb_1 = {"Mn": [0.1, 0.0, 0.0, 0.0]}
    orb_2 = {"O": [0.0, 0.1, 0.0, 0.0]}
    assert orbital_diff(orb_1, orb_2) == 0.2


