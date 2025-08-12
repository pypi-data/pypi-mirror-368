# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
from pathlib import Path

from monty.serialization import loadfn
from pydefect.analyzer.eigenvalue_plotter import EigenvalueMplPlotter
from pydefect.chem_pot_diag.chem_pot_diag import CompositionEnergy, \
    CompositionEnergies
from pydefect.cli.main_tools import parse_dirs
from pydefect.cli.vasp.make_local_extrema import \
    make_local_extrema_from_volumetric_data
from pydefect.cli.vasp.make_band_edge_orbital_infos import \
    make_band_edge_orbital_infos
from pydefect.cli.vasp.make_calc_results import make_calc_results_from_vasp
from pydefect.cli.vasp.make_perfect_band_edge_state import \
    make_perfect_band_edge_state_from_vasp
from pydefect.cli.vasp.make_poscars_from_query import make_poscars_from_query
from pydefect.cli.vasp.make_unitcell import make_unitcell_from_vasp
from pydefect.input_maker.defect_entries_maker import DefectEntriesMaker
from pydefect.input_maker.defect_set import DefectSet
from pydefect.input_maker.local_extrema import VolumetricDataAnalyzeParams
from pydefect.input_maker.supercell_info import SupercellInfo
from pydefect.util.mp_tools import MpQuery
from pymatgen.core import Structure
from pymatgen.io.vasp import Vasprun, Outcar, Procar
from vise.defaults import defaults
from vise.util.logger import get_logger

logger = get_logger(__name__)


def make_unitcell(args):
    unitcell = make_unitcell_from_vasp(
        vasprun_band=args.vasprun_band,
        outcar_band=args.outcar_band,
        outcar_dielectric_clamped=args.outcar_dielectric_clamped,
        outcar_dielectric_ionic=args.outcar_dielectric_ionic,
        system_name=args.name)
    unitcell.to_yaml_file()


def make_competing_phase_dirs(args):
    query = MpQuery(element_list=args.elements, e_above_hull=args.e_above_hull)
    make_poscars_from_query(materials_query=query.materials, path=Path.cwd())


def make_composition_energies(args):
    if args.yaml_file:
        composition_energies = CompositionEnergies.from_yaml(args.yaml_file)
    else:
        composition_energies = CompositionEnergies()

    def _inner(_dir: Path):
        outcar = Outcar(_dir / defaults.outcar)
        composition = Structure.from_file(_dir / defaults.contcar).composition
        energy = float(outcar.final_energy)  # original type is FloatWithUnit
        return composition, CompositionEnergy(energy, str(_dir))

    for c, ce in parse_dirs(args.dirs, _inner, args.verbose):
        if c in composition_energies:
            original_energy = composition_energies[c].energy
            original_source = composition_energies[c].source
            if ce.energy > original_energy:
                logger.info(
                    f"Energy in {ce.source} is higher than that of "
                    f"{original_source} ({ce.energy} vs {original_energy}), "
                    f"so skip it.")
                continue
        composition_energies[c] = ce

    composition_energies.to_yaml_file()


def make_local_extrema(args):
    volumetric_data = args.volumetric_data[0]
    if len(args.volumetric_data) > 1:
        for i in args.volumetric_data[1:]:
            volumetric_data += i

    params = VolumetricDataAnalyzeParams(args.threshold_frac,
                                         args.threshold_abs,
                                         args.min_dist,
                                         args.tol,
                                         args.radius)
    local_extrema = make_local_extrema_from_volumetric_data(
        volumetric_data=volumetric_data,
        params=params,
        info=args.info,
        find_min=not args.find_max)
    local_extrema.to_json_file()


def make_defect_entries(args):
    supercell_info: SupercellInfo = loadfn("supercell_info.json")
    perfect = Path("perfect")

    try:
        perfect.mkdir()
        logger.info("Making perfect dir...")
        supercell_info.structure.to(filename=str(perfect / "POSCAR"))
    except FileExistsError:
        logger.info(f"perfect dir exists, so skipped...")

    defect_set = DefectSet.from_yaml()
    maker = DefectEntriesMaker(supercell_info, defect_set)

    for defect_entry in maker.defect_entries:
        dir_path = Path(defect_entry.full_name)
        try:
            dir_path.mkdir()
            logger.info(f"Making {dir_path} dir...")
            if defect_entry.perturbed_structure:
                defect_entry.perturbed_structure.to(
                    filename=str(dir_path / "POSCAR"))
            else:
                defect_entry.structure.to(filename=str(dir_path / "POSCAR"))

            defect_entry.to_json_file(
                filename=str(dir_path / "defect_entry.json"))
            defect_entry.to_prior_info(
                filename=str(dir_path / "prior_info.yaml"))
        except FileExistsError:
            logger.info(f"{dir_path} dir exists, so skipped...")


def make_calc_results(args):
    file_name = "calc_results.json"

    def _inner(_dir: Path):
        calc_results = make_calc_results_from_vasp(
            vasprun=Vasprun(_dir / defaults.vasprun, parse_potcar_file=False),
            outcar=Outcar(_dir / defaults.outcar))
        calc_results.to_json_file(str(_dir / file_name))

    parse_dirs(args.dirs, _inner, args.verbose, file_name)


def make_perfect_band_edge_state(args):
    procar = Procar(args.dir / defaults.procar)
    vasprun = Vasprun(args.dir / defaults.vasprun, parse_potcar_file=False)
    outcar = Outcar(args.dir / defaults.outcar)
    perfect_band_edge_state = \
        make_perfect_band_edge_state_from_vasp(procar, vasprun, outcar)
    perfect_band_edge_state.to_json_file(
        args.dir / "perfect_band_edge_state.json")

    vbm = perfect_band_edge_state.vbm_info.energy
    cbm = perfect_band_edge_state.cbm_info.energy
    band_edge_orb_infos = make_band_edge_orbital_infos(
        procar, vasprun, vbm, cbm)
    band_edge_orb_infos.to_json_file(args.dir / "band_edge_orbital_infos.json")

    plotter = EigenvalueMplPlotter(
        title="perfect", band_edge_orb_infos=band_edge_orb_infos,
        supercell_vbm=vbm, supercell_cbm=cbm)
    plotter.construct_plot()
    plotter.plt.savefig(fname=args.dir / "eigenvalues.pdf")
    plotter.plt.clf()


def make_band_edge_orb_infos_and_eigval_plot(args):
    supercell_vbm = args.p_state.vbm_info.energy
    supercell_cbm = args.p_state.cbm_info.energy

    file_name = "band_edge_orbital_infos.json"

    def _inner(_dir: Path):
        try:
            defect_entry = loadfn(_dir / "defect_entry.json")
            title = defect_entry.name
        except FileNotFoundError:
            title = "No name"
        procar = Procar(_dir / defaults.procar)
        vasprun = Vasprun(_dir / defaults.vasprun, parse_potcar_file=False)

        str_info = None
        if args.no_participation_ratio is False:
            str_info = loadfn(_dir / "defect_structure_info.json")
        try:
            eigval_shift_yaml = loadfn(_dir / "eigenvalue_shift.yaml")
            eigval_shift = eigval_shift_yaml["shift_value"]
        except FileNotFoundError:
            eigval_shift = 0.0

        band_edge_orb_infos = make_band_edge_orbital_infos(
            procar, vasprun, supercell_vbm, supercell_cbm, str_info,
            eigval_shift=eigval_shift)
        band_edge_orb_infos.to_json_file(_dir / file_name)

        plotter = EigenvalueMplPlotter(
            title=title, band_edge_orb_infos=band_edge_orb_infos,
            supercell_vbm=supercell_vbm, supercell_cbm=supercell_cbm,
            y_range=args.y_range)
        plotter.construct_plot()
        plotter.plt.savefig(fname=_dir / "eigenvalues.pdf")
        plotter.plt.clf()

    parse_dirs(args.dirs, _inner, args.verbose, file_name)