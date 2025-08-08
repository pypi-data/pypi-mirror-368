"""
Meshing utilities for use in openfoam
"""

import shutil
import subprocess
import os
from pathlib import Path
from typing import cast


from icplot.mesh import Edge, HexCell, Mesh, Patch

from .foamfile import FoamFile, write_header


def get_foamfile_header() -> FoamFile:
    return FoamFile(
        version=2.0,
        format="ascii",
        arch="LSB;label=32;scalar=64",
        foam_class="dictionary",
        location="system",
        foam_object="blockMeshDict",
    )


def has_openfoam() -> bool:
    return bool(shutil.which("openfoam"))


def has_blockmesh() -> bool:
    return has_openfoam() and bool(shutil.which("blockMesh"))


def _write_mesh_blocks(cells: tuple[HexCell, ...]) -> str:

    output = "blocks\n(\n"
    for c in cells:
        verts = " ".join(str(v) for v in c.vertices)
        output += f"\thex ({verts})\n"

        counts = " ".join(str(count) for count in c.cell_counts)
        output += f"\t({counts})\n"

        grades = " ".join(str(g) for g in c.grading_ratios)
        output += f"\t{c.grading} ({grades})\n"
    output += ");\n\n"
    return output


def _write_mesh_edges(edges: tuple[Edge, ...]) -> str:

    if not edges:
        return ""

    output = "edges\n(\n"
    for e in edges:
        if e.type == "line":
            output += f"\tline {e.vert0} {e.vert1}\n"
        else:
            interps = ""
            for p in e.interp_points:
                interps += f"({p.x} {p.y} {p.z}) "
            output += f"\t {e.type} {e.vert0} {e.vert1} {interps}\n"
    output += ");\n\n"
    return output


def _write_mesh_boundaries(patches: tuple[Patch, ...]) -> str:

    if not patches:
        return ""

    output = "boundary\n(\n"
    for patch in patches:
        output += f"\t{patch.name}\n"
        output += "\t{\n"
        output += f"\t\ttype {patch.type};\n"
        output += "\t\tfaces\n\t\t(\n"
        for f in patch.faces:
            faces = " ".join(str(idx) for idx in f)
            output += f"\t\t\t({faces})\n"
        output += "\t\t);\n"
        output += "\t}\n"
    output += ");\n\n"
    return output


def write_blockmesh(mesh: Mesh) -> str:
    """
    Given a mesh, write it in openfoam blockMesh format
    """

    output = write_header(get_foamfile_header())

    output += f"scale\t{mesh.scale};\n"

    output += "vertices\n(\n"
    for idx, v in enumerate(mesh.vertices):
        output += f"\t( {v.x} {v.y} {v.z} ) // # {idx} \n"
    output += ");\n\n"

    output += _write_mesh_edges(mesh.edges)

    output += _write_mesh_blocks(tuple([cast(HexCell, c) for c in mesh.cells]))

    output += _write_mesh_boundaries(mesh.patches)
    return output


def generate_mesh(mesh: Mesh, case_dir: Path):

    if not has_blockmesh():
        raise RuntimeError("Openfoam not found, can't generate mesh")

    system_dir = case_dir / "system"
    os.makedirs(system_dir, exist_ok=True)

    mesh_str = write_blockmesh(mesh)
    mesh_file = system_dir / "blockMeshDict"
    with open(mesh_file, "w", encoding="utf-8") as f:
        f.write(mesh_str)

    control_dict = system_dir / "controlDict"
    if not control_dict.exists():
        shutil.copy(Path(__file__).parent / "controlDict", control_dict)

    cmd = f"blockMesh -case {case_dir}"
    subprocess.run(cmd, cwd=case_dir, shell=True, check=True)

    cmd = f"blockMesh -case {case_dir} -write-vtk"
    subprocess.run(cmd, cwd=case_dir, shell=True, check=True)
