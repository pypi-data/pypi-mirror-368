#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import pytest
import ase
import numpy as np
import json
from typing import Tuple

from nomad.datamodel import EntryArchive, EntryMetadata
import runschema
import simulationworkflowschema
from nomad.utils import get_logger
from nomad.units import ureg
from nomad.metainfo import MSection, Quantity, SubSection, Section
from nomad.normalizing import normalizers


LOGGER = get_logger(__name__)

parser_examples = [
    "tests/data/template.json",
    "tests/data/exciting.Ag.archive.json",
    "tests/data/exciting.GW.archive.json",
    "tests/data/exciting.nitrogen.archive.json",
    "tests/data/exciting.carbon.archive.json",
    "tests/data/vasp.archive.json",
    "tests/data/vasp.compressed.archive.json",
    "tests/data/vasp.outcar.archive.json",
    # TODO metainfo failure
    # "tests/data/fhiaims.archive.json",
    "tests/data/fhivibes.archive.json",
    "tests/data/cp2k.archive.json",
    "tests/data/crystal.archive.json",
    "tests/data/cpmd.archive.json",
    "tests/data/nwchem.archive.json",
    "tests/data/bigdft.archive.json",
    "tests/data/wien2k.archive.json",
    "tests/data/ams.archive.json",
    "tests/data/gaussian.archive.json",
    "tests/data/abinit.archive.json",
    "tests/data/quantumespresso.archive.json",
    "tests/data/orca.archive.json",
    "tests/data/castep.archive.json",
    "tests/data/dlpoly.archive.json",
    "tests/data/libatoms.archive.json",
    "tests/data/octopus.archive.json",
    "tests/data/phonopy.archive.json",
    "tests/data/gpaw.Fe2.archive.json",
    "tests/data/gpaw.H2_lcao.archive.json",
    "tests/data/atk.archive.json",
    "tests/data/gulp.archive.json",
    "tests/data/siesta.archive.json",
    "tests/data/elk.archive.json",
    "tests/data/elastic.archive.json",
    "tests/data/turbomole.archive.json",
    "tests/data/gamess.archive.json",
    "tests/data/dmol.archive.json",
    "tests/data/fleur.archive.json",
    "tests/data/molcas.archive.json",
    "tests/data/qbox.archive.json",
    "tests/data/onetep.archive.json",
    "tests/data/eels.archive.json",
    "tests/data/lobster.archive.json",
    "tests/data/aflow.archive.json",
    "tests/data/atomate.archive.json",
    "tests/data/asr.archive.json",
    "tests/data/psi4.archive.json",
    "tests/data/yambo.archive.json",
    "tests/data/archive.json",
    "tests/data/nexus.201805_WSe2_arpes.archive.json",
    "tests/data/nexus.SiO2onSi.ellips.archive.json",
]


# TODO remove fhiiams-specifix metainfo usage from method normalizer.
# We do not want to import the electronicparsers project for this!
class x_fhi_aims_section_controlIn_basis_set(MSection):
    m_def = Section(validate=False)

    x_fhi_aims_controlIn_species_name = Quantity(
        type=str,
        shape=[],
    )


class Method(runschema.method.Method):
    m_def = Section(extends_base_section=True)

    x_fhi_aims_section_controlIn_basis_set = SubSection(
        sub_section=x_fhi_aims_section_controlIn_basis_set, repeats=True
    )


def run_normalize(entry_archive: EntryArchive) -> EntryArchive:
    for normalizer in normalizers:
        normalizer(entry_archive).normalize()
    return entry_archive


def load_archive(filepath: str) -> EntryArchive:
    archive = EntryArchive.m_from_dict(json.load(open(filepath)))
    archive.metadata = EntryMetadata()
    return archive


def get_template_computation() -> EntryArchive:
    """Returns a basic archive template for a computational calculation"""
    template = EntryArchive()
    run = runschema.run.Run()
    template.run.append(run)
    run.program = runschema.run.Program(name="VASP", version="4.6.35")
    system = runschema.system.System()
    run.system.append(system)
    system.atoms = runschema.system.Atoms(
        lattice_vectors=[
            [5.76372622e-10, 0.0, 0.0],
            [0.0, 5.76372622e-10, 0.0],
            [0.0, 0.0, 4.0755698899999997e-10],
        ],
        positions=[
            [2.88186311e-10, 0.0, 2.0377849449999999e-10],
            [0.0, 2.88186311e-10, 2.0377849449999999e-10],
            [0.0, 0.0, 0.0],
            [2.88186311e-10, 2.88186311e-10, 0.0],
        ],
        labels=["Br", "K", "Si", "Si"],
        periodic=[True, True, True],
    )
    scc = runschema.calculation.Calculation()
    run.calculation.append(scc)
    scc.system_ref = system
    scc.energy = runschema.calculation.Energy(
        free=runschema.calculation.EnergyEntry(value=-1.5936767191492225e-18),
        total=runschema.calculation.EnergyEntry(value=-1.5935696296699573e-18),
        total_t0=runschema.calculation.EnergyEntry(value=-3.2126683561907e-22),
    )
    return template


def get_template_dft() -> EntryArchive:
    """Returns a basic archive template for a DFT calculation."""
    template = get_template_computation()
    run = template.run[-1]
    method = runschema.method.Method()
    run.method.append(method)
    method.electrons_representation = [
        runschema.method.BasisSetContainer(
            type="plane waves",
            scope=["wavefunction"],
            basis_set=[
                runschema.method.BasisSet(
                    type="plane waves",
                    scope=["valence"],
                )
            ],
        )
    ]
    method.electronic = runschema.method.Electronic(method="DFT")
    xc_functional = runschema.method.XCFunctional(
        exchange=[runschema.method.Functional(name="GGA_X_PBE")]
    )
    method.dft = runschema.method.DFT(xc_functional=xc_functional)
    scc = run.calculation[-1]
    scc.method_ref = method
    return template


def get_section_system(atoms):
    if runschema:
        system = runschema.system.System()
        system.atoms = runschema.system.Atoms(
            positions=atoms.get_positions() * 1e-10,
            labels=atoms.get_chemical_symbols(),
            lattice_vectors=atoms.get_cell() * 1e-10,
            periodic=atoms.get_pbc(),
        )
        return system


def get_template_for_structure(atoms) -> EntryArchive:
    template = get_template_dft()
    template.run[0].calculation[0].system_ref = None
    template.run[0].calculation[0].eigenvalues.append(
        runschema.calculation.BandEnergies()
    )
    template.run[0].calculation[0].eigenvalues[0].kpoints = [[0, 0, 0]]
    template.run[0].system = []

    # Fill structural information
    # system = template.run[0].m_create(System)
    # system.atom_positions = atoms.get_positions() * 1E-10
    # system.atom_labels = atoms.get_chemical_symbols()
    # system.simulation_cell = atoms.get_cell() * 1E-10
    # system.configuration_periodic_dimensions = atoms.get_pbc()
    system = get_section_system(atoms)
    template.run[0].system.append(system)

    return run_normalize(template)


@pytest.fixture(params=parser_examples, ids=lambda spec: spec)
def parsed_example(request) -> EntryArchive:
    mainfile = request.param
    result = load_archive(mainfile)
    return mainfile, result


@pytest.fixture
def normalized_example(parsed_example: Tuple[str, EntryArchive]) -> EntryArchive:
    run_normalize(parsed_example[1])
    return parsed_example


@pytest.fixture(scope="session")
def single_point() -> EntryArchive:
    """Single point calculation."""
    template = get_template_dft()
    return run_normalize(template)


@pytest.fixture(scope="session")
def molecular_dynamics() -> EntryArchive:
    """Molecular dynamics calculation."""
    template = get_template_dft()
    run = template.run[0]

    # Create calculations
    n_steps = 10
    calcs = []
    for step in range(n_steps):
        system = runschema.system.System()
        run.system.append(system)
        calc = runschema.calculation.Calculation()
        calc.system_ref = system
        calc.time = step
        calc.step = step
        calc.volume = step
        calc.pressure = step
        calc.temperature = step
        calc.energy = runschema.calculation.Energy(
            potential=runschema.calculation.EnergyEntry(value=step),
        )
        rg_values = runschema.calculation.RadiusOfGyrationValues(
            value=step, label="MOL"
        )
        if system.atoms_group:
            rg_values.atomsgroup_ref = system.atoms_group[0]
        calc.radius_of_gyration = [
            runschema.calculation.RadiusOfGyration(
                kind="molecular",
                radius_of_gyration_values=[rg_values],
            )
        ]
        calcs.append(calc)
        run.calculation.append(calc)

    # Create workflow
    diff_values = simulationworkflowschema.molecular_dynamics.DiffusionConstantValues(
        value=2.1,
        error_type="Pearson correlation coefficient",
        errors=[0.98],
    )
    msd_values = (
        simulationworkflowschema.molecular_dynamics.MeanSquaredDisplacementValues(
            times=[0, 1, 2],
            n_times=3,
            value=[0, 1, 2],
            label="MOL",
            errors=[0, 1, 2],
            diffusion_constant=diff_values,
        )
    )
    msd = simulationworkflowschema.molecular_dynamics.MeanSquaredDisplacement(
        type="molecular",
        direction="xyz",
        error_type="bootstrapping",
        mean_squared_displacement_values=[msd_values],
    )
    rdf_values = (
        simulationworkflowschema.molecular_dynamics.RadialDistributionFunctionValues(
            bins=[0, 1, 2],
            n_bins=3,
            value=[0, 1, 2],
            frame_start=0,
            frame_end=100,
            label="MOL-MOL",
        )
    )
    rdf = simulationworkflowschema.molecular_dynamics.RadialDistributionFunction(
        type="molecular",
        radial_distribution_function_values=[rdf_values],
    )
    results = simulationworkflowschema.molecular_dynamics.MolecularDynamicsResults(
        radial_distribution_functions=[rdf],
        mean_squared_displacements=[msd],
    )
    method = simulationworkflowschema.molecular_dynamics.MolecularDynamicsMethod(
        thermodynamic_ensemble="NVT",
        integration_timestep=0.5 * ureg("fs"),
    )
    md = simulationworkflowschema.molecular_dynamics.MolecularDynamics(
        results=results, method=method
    )
    results.calculation_result_ref = calcs[-1]
    results.calculations_ref = calcs
    template.workflow2 = md

    return run_normalize(template)


@pytest.fixture(scope="session")
def phonon() -> EntryArchive:
    archive = load_archive("tests/data/phonopy.archive.json")
    return run_normalize(archive)


@pytest.fixture(scope="session")
def geometry_optimization() -> EntryArchive:
    template = get_template_dft()
    template.run[0].system = None
    template.run[0].calculation = None
    run = template.run[0]
    atoms1 = ase.build.bulk("Si", "diamond", cubic=True, a=5.431)
    atoms2 = ase.build.bulk("Si", "diamond", cubic=True, a=5.431)
    atoms2.translate([0.01, 0, 0])
    sys1 = get_section_system(atoms1)
    sys2 = get_section_system(atoms2)
    scc1 = runschema.calculation.Calculation()
    scc2 = runschema.calculation.Calculation()
    scc1.energy = runschema.calculation.Energy(
        total=runschema.calculation.EnergyEntry(value=1e-19),
        total_t0=runschema.calculation.EnergyEntry(value=1e-19),
    )
    scc2.energy = runschema.calculation.Energy(
        total=runschema.calculation.EnergyEntry(value=0.5e-19),
        total_t0=runschema.calculation.EnergyEntry(value=0.5e-19),
    )
    scc1.system_ref = sys1
    scc2.system_ref = sys2
    scc1.method_ref = run.method[0]
    scc2.method_ref = run.method[0]
    run.system.append(sys1)
    run.system.append(sys2)
    run.calculation.append(scc1)
    run.calculation.append(scc2)

    template.workflow2 = simulationworkflowschema.GeometryOptimization(
        method=simulationworkflowschema.GeometryOptimizationMethod(
            convergence_tolerance_energy_difference=1e-3 * ureg.electron_volt,
            convergence_tolerance_force_maximum=1e-11 * ureg.newton,
            convergence_tolerance_displacement_maximum=1e-3 * ureg.angstrom,
            method="bfgs",
            type="atomic",
        )
    )
    template.workflow2.normalize(template, get_logger(__name__))

    run_normalize(template)
    return template


@pytest.fixture(scope="session")
def bulk() -> EntryArchive:
    atoms = ase.build.bulk("Si", "diamond", cubic=True, a=5.431)
    return get_template_for_structure(atoms)


@pytest.fixture(scope="session")
def atom() -> EntryArchive:
    atoms = ase.Atoms(
        symbols=["H"],
        scaled_positions=[[0.5, 0.5, 0.5]],
        cell=[10, 10, 10],
        pbc=True,
    )
    return get_template_for_structure(atoms)


@pytest.fixture(scope="session")
def molecule() -> EntryArchive:
    atoms = ase.build.molecule("CO2")
    return get_template_for_structure(atoms)


@pytest.fixture(scope="session")
def one_d() -> EntryArchive:
    atoms = ase.build.graphene_nanoribbon(
        1, 1, type="zigzag", vacuum=10, saturated=True
    )
    return get_template_for_structure(atoms)


@pytest.fixture(scope="session")
def two_d() -> EntryArchive:
    atoms = ase.Atoms(
        symbols=["C", "C"],
        scaled_positions=[
            [0, 0, 0.5],
            [1 / 3, 1 / 3, 0.5],
        ],
        cell=[
            [2.461, 0, 0],
            [np.cos(np.pi / 3) * 2.461, np.sin(np.pi / 3) * 2.461, 0],
            [0, 0, 20],
        ],
        pbc=True,
    )
    return get_template_for_structure(atoms)


@pytest.fixture(scope="session")
def surface() -> EntryArchive:
    atoms = ase.build.fcc111("Al", size=(2, 2, 3), vacuum=10.0)
    return get_template_for_structure(atoms)
