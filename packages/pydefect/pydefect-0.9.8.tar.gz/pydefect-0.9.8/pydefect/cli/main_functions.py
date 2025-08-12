# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
from pathlib import Path
from typing import Union

from matplotlib import pyplot as plt
from monty.serialization import loadfn
from pydefect.analyzer.calc_results import CalcResults, NoElectronicConvError, \
    NoIonicConvError
from pydefect.analyzer.defect_energy import DefectEnergyInfo
from pydefect.analyzer.defect_energy_plotter import DefectEnergyMplPlotter
from pydefect.analyzer.make_band_edge_states import make_band_edge_states
from pydefect.analyzer.make_calc_summary import make_calc_summary
from pydefect.analyzer.make_defect_energy_info import make_defect_energy_info
from pydefect.analyzer.make_defect_energy_summary import \
    make_defect_energy_summary
from pydefect.analyzer.make_defect_structure_info import \
    MakeDefectStructureInfo
from pydefect.chem_pot_diag.chem_pot_diag import CompositionEnergies, \
    RelativeEnergies, ChemPotDiagMaker, TargetVertices, change_element_sequence
from pydefect.chem_pot_diag.cpd_plotter import ChemPotDiag2DMplPlotter, \
    ChemPotDiag3DMplPlotter
from pydefect.cli.main_tools import sanitize_matrix, parse_dirs
from pydefect.cli.vasp.make_efnv_correction import make_efnv_correction
from pydefect.corrections.no_correction import NoCorrection
from pydefect.corrections.site_potential_plotter import SitePotentialMplPlotter
from pydefect.input_maker.append_interstitial import append_interstitial
from pydefect.input_maker.defect_set_maker import DefectSetMaker
from pydefect.input_maker.manual_supercell_maker import ManualSupercellMaker, \
    make_sites_from_yaml_file
from pydefect.input_maker.supercell_maker import SupercellMaker
from pymatgen.analysis.phase_diagram import PDPlotter
from pymatgen.core import Composition
from vise.util.logger import get_logger

logger = get_logger(__name__)


def get_calc_results(d: Path, check: bool) -> Union[CalcResults, bool]:
    try:
        calc_results = loadfn(d / "calc_results.json")
    except FileNotFoundError:
        logger.warning(f"calc_results.json doesn't exist in {d}.")
        raise

    if calc_results.electronic_conv is False:
        logger.warning(f"SCF in {d} is not reached.")
        if check:
            raise NoElectronicConvError

    elif calc_results.ionic_conv is False:
        logger.warning(f"Ionic convergence in {d} is not reached.")
        if check:
            raise NoIonicConvError

    return calc_results


def make_standard_and_relative_energies(args):
    comp_energies = CompositionEnergies.from_yaml(
        args.composition_energies_yaml)
    std_energies, rel_energies = comp_energies.std_rel_energies
    std_energies.to_yaml_file()
    rel_energies.to_yaml_file()
    try:
        pd = comp_energies.to_phase_diagram()
        plotter = PDPlotter(pd, backend="matplotlib", show_unstable=float("inf"))
        plotter.get_plot(plt=plt)
        plt.savefig("convex_hull.pdf")
        # plotter = PDPlotter(pd, show_unstable=float("inf"))
        # plotter.show()

    except:
        pass

    if rel_energies.unstable_compounds:
        logger.info("The unstable compound information is shown below.")
        print(rel_energies.unstable_comp_info)


def make_cpd_and_vertices(args):
    rel_energies = RelativeEnergies.from_yaml(args.rel_energy_yaml)
    if args.target:
        elements = args.elements or \
                   Composition(args.target).chemical_system.split("-")
    else:
        elements = args.elements or list(rel_energies.all_element_set)

    cpd_maker = ChemPotDiagMaker(rel_energies, elements, args.target)
    cpd = cpd_maker.chem_pot_diag
    cpd.to_json_file()
    if args.target:
        cpd.to_target_vertices.to_yaml_file()


def plot_chem_pot_diag(args):
    cpd = args.chem_pot_diag
    cpd = change_element_sequence(cpd)
    if cpd.dim == 2:
        plotter = ChemPotDiag2DMplPlotter(cpd)
    elif cpd.dim == 3:
        plotter = ChemPotDiag3DMplPlotter(cpd)
    else:
        raise ValueError(f"Only 2 or 3 dimensions are supported. "
                         f"Now {cpd.dim} dimensions.")

    plt = plotter.draw_diagram()
    plt.savefig(fname="cpd.pdf")
    plt.show()


def make_supercell(args):
    kwargs = {}
    if args.analyze_symmetry:
        supercell_maker = SupercellMaker
    else:
        supercell_maker = ManualSupercellMaker
        kwargs["sites"] = make_sites_from_yaml_file(args.sites_yaml_filename)

    if args.matrix:
        matrix = sanitize_matrix(args.matrix)
        maker = supercell_maker(args.unitcell, matrix=matrix, **kwargs)
    else:
        if args.min_num_atoms:
            kwargs["min_num_atoms"] = args.min_num_atoms
        if args.max_num_atoms:
            kwargs["max_num_atoms"] = args.max_num_atoms
        maker = supercell_maker(args.unitcell, **kwargs)

    maker.supercell.structure.to(filename="SPOSCAR")
    maker.supercell_info.to_json_file()


def append_interstitial_to_supercell_info(args):
    supercell_info = append_interstitial(args.supercell_info,
                                         args.base_structure,
                                         [args.frac_coords],
                                         [args.info])
    supercell_info.to_json_file()


def pop_interstitial_from_supercell_info(args):
    supercell_info = args.supercell_info
    logger.info("Be careful that the interstitials indices are changed.")
    if args.pop_all is False:
        assert args.index > 0
        supercell_info.interstitials.pop(args.index - 1)
    else:
        try:
            while True:
                supercell_info.interstitials.pop()
        except IndexError:
            pass

    supercell_info.to_json_file()


def make_defect_set(args):
    supercell_info = loadfn("supercell_info.json")
    if args.oxi_states:
        oxi_states = dict(zip(args.oxi_states[::2], args.oxi_states[1::2]))
    else:
        oxi_states = None
    maker = DefectSetMaker(supercell_info,
                           oxi_states,
                           args.dopants,
                           keywords=args.keywords)
    maker.defect_set.to_yaml()


def calc_defect_structure_info(args):
    supercell_info = args.supercell_info
    file_name = "defect_structure_info.json"

    def _inner(_dir: Path):
        calc_results = get_calc_results(_dir, args.check_calc_results)
        defect_entry = loadfn(_dir / "defect_entry.json")
        defect_str_info = MakeDefectStructureInfo(
            supercell_info.structure,
            defect_entry.structure,
            calc_results.structure,
            dist_tol=args.dist_tolerance,
            symprec=args.symprec).defect_structure_info
        defect_str_info.to_json_file(str(_dir / file_name))

    parse_dirs(args.dirs, _inner, args.verbose, file_name)


def make_efnv_correction_main_func(args):
    file_name = "correction.json"
    def _inner(_dir: Path):
        calc_results = get_calc_results(_dir, args.check_calc_results)
        defect_entry = loadfn(_dir / "defect_entry.json")
        efnv = make_efnv_correction(defect_entry.charge,
                                    calc_results,
                                    args.perfect_calc_results,
                                    args.unitcell.dielectric_constant,
                                    defect_region_radius=args.radius,
                                    calc_all_sites=args.calc_all_sites)
        efnv.to_json_file(_dir / file_name)

        title = defect_entry.full_name
        plotter = SitePotentialMplPlotter.from_efnv_corr(
            title=title, efnv_correction=efnv)
        plotter.construct_plot()
        plotter.plt.savefig(fname=_dir / "correction.pdf")
        plotter.plt.clf()

    parse_dirs(args.dirs, _inner, args.verbose, file_name)


def make_band_edge_states_main_func(args):
    file_name = "band_edge_states.json"
    def _inner(_dir: Path):
        orb_infos = loadfn(_dir / "band_edge_orbital_infos.json")
        try:
            defect_charge_info = loadfn(_dir / "defect_charge_info.json")
        except FileNotFoundError:
            defect_charge_info = None
        band_edge_states = make_band_edge_states(orb_infos, args.p_state,
                                                 defect_charge_info)
        band_edge_states.to_json_file(str(_dir / file_name))

    parse_dirs(args.dirs, _inner, args.verbose, file_name)


def make_defect_energy_infos_main_func(args):
    file_name = "defect_energy_info.yaml"
    def _inner(_dir: Path):
        calc_results = get_calc_results(_dir, args.check_calc_results)
        defect_entry = loadfn(_dir / "defect_entry.json")
        try:
            correction = loadfn(_dir / "correction.json")
        except FileNotFoundError:
            logger.warning(
                "Since correction.json file does not exist, no correction is "
                "applied.")
            correction = NoCorrection()
        try:
            band_edge_states = loadfn(_dir / "band_edge_states.json")
        except FileNotFoundError:
            band_edge_states = None
        defect_energy_info = make_defect_energy_info(
            defect_entry=defect_entry,
            calc_results=calc_results,
            correction=correction,
            perfect_calc_results=args.perfect_calc_results,
            standard_energies=args.std_energies,
            unitcell=args.unitcell,
            band_edge_states=band_edge_states)
        defect_energy_info.to_yaml_file(str(_dir / file_name))

    parse_dirs(args.dirs, _inner, args.verbose, file_name)


def make_defect_energy_summary_main(
        dirs, verbose, target_vertices_yaml, unitcell, p_state):

    def _inner(_dir: Path):
        return DefectEnergyInfo.from_yaml(str(_dir / "defect_energy_info.yaml"))

    energy_infos = parse_dirs(dirs, _inner, verbose)
    target_vertices = TargetVertices.from_yaml(target_vertices_yaml)
    defect_energy_summary = make_defect_energy_summary(
        energy_infos, target_vertices, unitcell, p_state)
    defect_energy_summary.to_json_file()


def make_defect_energy_summary_main_func(args):
    make_defect_energy_summary_main(args.dirs,
                                    args.verbose,
                                    args.target_vertices_yaml,
                                    args.unitcell,
                                    args.p_state)


def make_calc_summary_main_func(args):
    def _inner(_dir: Path):
        calc_results = get_calc_results(_dir, args.check_calc_results)
        defect_entry = loadfn(_dir / "defect_entry.json")
        str_info = loadfn(_dir / "defect_structure_info.json")
        return calc_results, defect_entry, str_info

    _infos = parse_dirs(args.dirs, _inner, args.verbose)
    calc_summary = make_calc_summary(_infos, args.perfect_calc_results)
    calc_summary.to_json_file()


def plot_defect_energy(args):
    plotter = DefectEnergyMplPlotter(
        defect_energy_summary=args.defect_energy_summary,
        chem_pot_label=args.label,
        y_range=args.y_range,
        allow_shallow=args.allow_shallow,
        with_corrections=args.with_corrections,
        label_line=args.label_line,
        add_charges=args.add_charges,
        add_thin_lines=args.plot_all_energies)

    plotter.construct_plot()
    plotter.plt.savefig(f"energy_{args.label}.pdf")
