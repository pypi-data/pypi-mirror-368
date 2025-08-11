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
import ase.build
import numpy as np
from logging import LogRecord
import json
import os

from nomad import config
from nomad.datamodel import EntryArchive
from nomad.metainfo import Quantity, Section, JSON
from nomad.utils import dump_json

from conftest import run_normalize, load_archive, get_template_for_structure


def assert_log(caplog, level: str, event_part: str) -> LogRecord:
    """
    Assert whether a log message exists in the logs of the tests at a certain level.

    Parameters
    ----------
    caplog : pytest fixture
        This informs pytest that we want to access the logs from a pytest test.
    level : str
        The level of type of log for which we will search (e.g. 'WARN',
        'ERROR', 'DEBUG').
    event_part : str
        The error message we're after. We search the logs matching level if they
        contain this string.

    """
    match = None
    for record in caplog.get_records(when="call"):
        if record.levelname == level:
            try:
                event_data = json.loads(record.msg)
                present = event_part in event_data["event"]
            except Exception:
                present = event_part in record.msg

            if present:
                match = record
                # No need to look for more matches since we aren't counting matches.
                break

    assert match is not None

    return match


fcc_symmetry = "tests/data/fcc_crystal_structure.json"

two_d = "tests/data/fcc_crystal_structure.json"

vasp_archive = "tests/data/vasp.archive.json"


parser_exceptions = {
    "wien2k": ["results.method.simulation.dft.xc_functional_names"],
    "abinit": [
        "results.material.chemical_formula_descriptive",
        "results.material.structural_type",
    ],
    "dlpoly": [
        "results.material.chemical_formula_descriptive",
        "results.method.simulation.dft.basis_set_type",
        "results.method.simulation.dft.xc_functional_names",
        "results.material.structural_type",
    ],
    "libatoms": [
        "results.material.elements",
        "results.method.simulation.dft.basis_set_type",
        "results.method.simulation.dft.xc_functional_names",
    ],
    "phonopy": [
        "results.method.simulation.dft.basis_set_type",
        "results.method.simulation.dft.xc_functional_names",
    ],
    "gamess": [
        "results.material.chemical_formula_descriptive",
        "results.material.structural_type",
        "results.method.simulation.dft.xc_functional_names",
        "results.method.simulation.dft.basis_set_type",
    ],
    "gulp": [
        "results.material.chemical_formula_descriptive",
        "results.method.simulation.dft.xc_functional_names",
        "results.material.structural_type",
        "results.method.simulation.dft.basis_set_type",
    ],
    "elastic": [
        "results.method.simulation.dft.basis_set_type",
        "results.method.simulation.dft.xc_functional_names",
        "results.material.structural_type",
    ],
    "elk": [
        "results.method.simulation.dft.basis_set_type",
        "results.method.simulation.dft.xc_functional_names",
        "results.material.structural_type",
    ],
    # TODO why rename parsers?
    "fleur": [
        "results.method.simulation.dft.basis_set_type",
        "results.method.simulation.dft.xc_functional_names",
        "results.material.structural_type",
    ],
    "molcas": [
        "results.material.chemical_formula_descriptive",
        "results.method.simulation.dft.xc_functional_names",
        "results.material.structural_type",
        "results.method.simulation.dft.basis_set_type",
    ],
    "dmol": [
        "results.method.simulation.dft.basis_set_type",
        "results.method.simulation.dft.xc_functional_names",
        "results.material.structural_type",
    ],
    "ams": ["results.material.structural_type"],
    "qbox": [
        "results.material.chemical_formula_descriptive",
        "results.material.elements",
        "results.method.simulation.dft.basis_set_type",
        "results.method.simulation.dft.xc_functional_names",
        "results.material.structural_type",
    ],
    "cpmd": [
        "results.material.chemical_formula_descriptive",
        "results.method.simulation.dft.basis_set_type",
        "results.method.simulation.dft.xc_functional_names",
        "results.material.structural_type",
    ],
    "onetep": [
        "results.material.chemical_formula_descriptive",
        "results.material.elements",
        "results.method.simulation.dft.basis_set_type",
        "results.method.simulation.dft.xc_functional_names",
        "results.material.structural_type",
    ],
    "siesta": [
        "results.method.simulation.dft.basis_set_type",
        "results.method.simulation.dft.xc_functional_names",
        "results.material.structural_type",
    ],
    "lobster": [
        "results.method.simulation.dft.basis_set_type",
        "results.method.simulation.dft.xc_functional_names",
        "results.material.structural_type",
    ],
    "xps": [
        "results.material.chemical_formula_descriptive",
        "results.material.elements",
    ],
    "aflow": [
        "results.method.simulation.dft.basis_set_type",
        "results.method.simulation.dft.xc_functional_names",
    ],
    "yambo": [
        "results.material.chemical_formula_descriptive",
        "results.material.elements",
        "results.method.simulation.dft.basis_set_type",
        "results.method.simulation.dft.xc_functional_names",
        "results.material.structural_type",
    ],
}
"""
Keys that the normalizer for certain parsers might not produce. In an ideal world this
map would be empty.
"""


def test_template_example_normalizer():
    parsed_template_example = load_archive("tests/data/template.json")
    run_normalize(parsed_template_example)


def assert_normalized(mainfile: str, entry_archive: EntryArchive):
    parser = "archive"
    if mainfile:
        parser = os.path.basename(mainfile).split(".")[0]
    if parser == "nexus":
        return

    results = entry_archive.results
    entry_archive.metadata.apply_archive_metadata(entry_archive)
    exceptions = parser_exceptions.get(parser, [])

    if "results.material.chemical_formula_descriptive" not in exceptions:
        assert results.material.chemical_formula_descriptive is not None
        assert (
            results.material.chemical_formula_descriptive
            != config.services.unavailable_value
        )
    if "results.material.elements" not in exceptions:
        assert len(results.material.elements) > 0

    assert results.method is not None
    if results.method.method_name == "DFT":
        assert results.method.simulation.program_name is not None
        assert results.method.simulation.program_version is not None
        assert results.method.simulation.dft.basis_set_type is not None
        assert results.method.simulation.dft.xc_functional_names is not None
        assert results.material.structural_type is not None

        for key in [
            "results.method.simulation.program_name",
            "results.method.simulation.program_version",
            "results.method.simulation.dft.basis_set_type",
            "results.method.simulation.dft.xc_functional_names",
            "results.material.structural_type",
            "results.material.chemical_formula_descriptive",
        ]:
            if key in exceptions:
                continue

            assert entry_archive[key] != config.services.unavailable_value, (
                "%s must not be unavailable" % key
            )

    assert entry_archive.metadata
    assert entry_archive.metadata.quantities
    assert len(entry_archive.metadata.quantities) > 0

    # check if the result can be dumped
    dump_json(entry_archive.m_to_dict())


def test_normalizer(normalized_example: EntryArchive):
    assert_normalized(*normalized_example)


def test_normalization_atoms(bulk):
    """Tests correct value extraction of the system values."""
    atoms = bulk.run[0].system[0].atoms
    reference_lattice = 5.431
    reference_lattice_reciprocal = 2 * np.pi / reference_lattice
    assert (
        atoms.lattice_vectors.to("angstrom").magnitude
        == reference_lattice * np.identity(3)
    ).all()
    assert (
        atoms.lattice_vectors_reciprocal.to("1/angstrom").magnitude
        == reference_lattice_reciprocal * np.identity(3)
    ).all()


def test_normalizer_faulty_matid(caplog):
    """Runs normalizer on an example w/ bools for atom pos. Should force matid error."""
    archive = load_archive("tests/data/no_sim_cell_boolean_positions.json")
    run_normalize(archive)
    assert_log(caplog, "ERROR", "matid project system classification failed")
    assert_log(caplog, "ERROR", "no lattice vectors but periodicity")


def test_normalizer_single_string_atom_labels(caplog):
    """
    Runs normalizer on ['Br1SiSiK'] expects error. Should replace the label with 'X' and
    the numbers of positions should not match the labels.
    """
    archive = load_archive("tests/data/single_string_atom_labels.json")
    run_normalize(archive)
    assert_log(caplog, "ERROR", "len of atom position does not match number of atoms")


def test_normalizer_unknown_atom_label():
    """Runs normalizer on ['Br','Si','Si','Za'], for normalization Za will be replaced,
    but stays in the labels.
    """
    archive = load_archive("tests/data/unknown_atom_label_test.json")
    run_normalize(archive)
    assert archive.run[0].m_xpath("system[*].atoms.labels")[0][3] == "Za"


def test_symmetry_classification_fcc():
    """Runs normalizer where lattice vectors should give fcc symmetry."""
    archive = load_archive(fcc_symmetry)
    archive = run_normalize(archive)
    expected_crystal_system = "cubic"
    expected_bravais_lattice = "cF"
    expected_point_group = "m-3m"
    expected_origin_shift = [0, 0, 0]
    sec_symmetry = archive.run[0].system[0].symmetry[0]
    crystal_system = sec_symmetry.crystal_system
    assert crystal_system == expected_crystal_system
    bravais_lattice = sec_symmetry.bravais_lattice
    assert bravais_lattice == expected_bravais_lattice
    point_group = sec_symmetry.point_group
    assert point_group == expected_point_group
    origin_shift = sec_symmetry.origin_shift
    assert all(origin_shift == expected_origin_shift)


def test_to_ase():
    archive = load_archive(fcc_symmetry)
    archive = run_normalize(archive)
    assert archive.run[0].system[0].atoms.to_ase() is not None


def test_system_classification(atom, molecule, one_d, two_d, surface, bulk):
    """Tests that the system classification is correct for different kind of systems"""
    # Atom
    assert atom.run[0].system[-1].type == "atom"
    # Molecule
    assert molecule.run[0].system[-1].type == "molecule / cluster"
    # 1D system
    assert one_d.run[0].system[-1].type == "1D"
    # 2D system
    assert two_d.run[0].system[-1].type == "2D"
    # Surface
    assert surface.run[0].system[-1].type == "surface"
    # Bulk system
    assert bulk.run[0].system[-1].type == "bulk"


@pytest.mark.parametrize(
    "entry",
    [
        ("single_point"),
        ("molecular_dynamics"),
        ("geometry_optimization"),
        ("phonon"),
    ],
)
def test_representative_systems(entry, request):
    """Checks that the representative systems are correctly identified and
    processed by SystemNormalizer.
    """
    entry = request.getfixturevalue(entry)

    # For systems with multiple frames the first and two last should be processed.
    try:
        frames = entry.workflow[0].calculations_ref
    except Exception:
        scc = entry.run[0].calculation[-1]
        repr_system = scc.system_ref
    else:
        if entry.workflow[0].type == "molecular_dynamics":
            scc = frames[0]
        else:
            scc = frames[-1]
        repr_system = scc.system_ref

    # If the selected system refers to a subsystem, choose it instead.
    try:
        system = repr_system.sub_system_ref
        if system is None:
            system = repr_system.systems_ref[0]
        repr_system = system
    except Exception:
        pass

    # Check that only the representative system has been labels with
    # "is_representative"
    for system in entry.run[0].system:
        if system.m_parent_index == repr_system.m_parent_index:
            assert system.is_representative is True
        else:
            assert system.is_representative is None


def test_reduced_chemical_formula():
    "Ensure we get the right reduced chemical formula for glucose atom labels"
    archive = load_archive("tests/data/glucose_atom_labels.json")
    archive = run_normalize(archive)
    expected_red_chem_formula = "C6H12O6"
    sec_system = archive.run[0].system[0]
    reduced_chemical_formula = sec_system.chemical_composition_hill
    assert expected_red_chem_formula == reduced_chemical_formula


def test_vasp_incar_system():
    """
    Ensure we can test an incar value in the VASP example
    """
    import runschema  # noqa

    class Method(runschema.method.Method):
        m_def = Section(extends_base_section=True)

        x_vasp_incar_in = Quantity(
            type=JSON,
            shape=[],
            description="""
            contains all the user-input INCAR parameters
            """,
        )

    archive = load_archive(vasp_archive)
    archive = run_normalize(archive)
    expected_value = "SrTiO3"  # material's formula in vasp.xml

    backend_value = archive.run[0].method[0].x_vasp_incar_in["SYSTEM"]

    assert expected_value == backend_value


def test_aflow_prototypes():
    """Tests that some basis structures are matched with the correct AFLOW prototypes"""

    def get_proto(atoms):
        archive = get_template_for_structure(atoms)
        try:
            sec_proto = archive.run[0].system[0].prototype[0]
            prototype_aflow_id = sec_proto.aflow_id
            prototype_label = sec_proto.label
        except Exception:
            prototype_aflow_id = None
            prototype_label = None

        return prototype_aflow_id, prototype_label

    # No prototype info for non-bulk structures
    water = ase.build.molecule("H2O")
    prototype_aflow_id, prototype_label = get_proto(water)
    assert prototype_aflow_id is None
    assert prototype_label is None

    # No prototype info for bulk structure without match
    rattled = ase.build.bulk("C", crystalstructure="diamond", a=3.57, cubic=True)
    rattled.rattle(stdev=2, seed=42)
    rattled.wrap()
    aflow_id, prototype_label = get_proto(rattled)
    assert aflow_id is None
    assert prototype_label is None

    # Diamond
    diamond = ase.build.bulk("C", crystalstructure="diamond", a=3.57)
    prototype_aflow_id, prototype_label = get_proto(diamond)
    assert prototype_aflow_id == "A_cF8_227_a"
    assert prototype_label == "227-C-cF8"

    # BCC
    bcc = ase.build.bulk("Fe", crystalstructure="bcc", a=2.856)
    prototype_aflow_id, prototype_label = get_proto(bcc)
    assert prototype_aflow_id == "A_cI2_229_a"
    assert prototype_label == "229-W-cI2"

    # FCC
    fcc = ase.build.bulk("Ge", crystalstructure="fcc", a=5.658)
    prototype_aflow_id, prototype_label = get_proto(fcc)
    assert prototype_aflow_id == "A_cF4_225_a"
    assert prototype_label == "225-Cu-cF4"

    # Rocksalt
    rocksalt = ase.build.bulk("NaCl", crystalstructure="rocksalt", a=5.64)
    prototype_aflow_id, prototype_label = get_proto(rocksalt)
    assert prototype_aflow_id == "AB_cF8_225_a_b"
    assert prototype_label == "225-ClNa-cF8"

    # Zincblende
    zincblende = ase.build.bulk(
        "ZnS", crystalstructure="zincblende", a=5.42, cubic=True
    )
    prototype_aflow_id, prototype_label = get_proto(zincblende)
    assert prototype_aflow_id == "AB_cF8_216_c_a"
    assert prototype_label == "216-SZn-cF8"

    # Wurtzite
    wurtzite = ase.build.bulk("SiC", crystalstructure="wurtzite", a=3.086, c=10.053)
    prototype_aflow_id, prototype_label = get_proto(wurtzite)
    assert prototype_aflow_id == "AB_hP4_186_b_b"
    assert prototype_label == "186-SZn-hP4"


@pytest.mark.skipif(
    config.normalize.springer_db_path is None, reason="Springer DB path missing"
)
def test_springer_normalizer():
    """
    Ensure the Springer normalizer works well with the VASP example.
    """
    archive = load_archive(vasp_archive)
    archive = run_normalize(archive)

    springer_cls = (
        archive.run[0]
        .system[0]
        .m_def.all_sub_sections["springer_material"]
        .sub_section.section_cls
    )
    springer = springer_cls.m_from_dict(
        archive.run[0].m_xpath("system[*].springer_material")[0][0]
    )

    assert springer.id == "sd_0305232"
    assert springer.alphabetical_formula == "O3SrTi"
    assert (
        springer.url
        == "http://materials.springer.com/isp/crystallographic/docs/sd_0305232"
    )
