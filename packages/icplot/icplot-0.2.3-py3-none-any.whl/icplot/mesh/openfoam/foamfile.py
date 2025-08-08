from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FoamFile:
    """
    A parsed foam file
    """

    location: str
    foam_object: str
    body_size: int = 0
    body: tuple[str, ...] = ()
    version: float = 2.0
    format: str = "ascii"
    arch: str = '"LSB;label=32;scalar=64"'
    foam_class: str = "vectorField"


def write_header(spec: FoamFile) -> str:

    output = "FoamFile\n{"
    output += f"\tversion\t{spec.version};\n"
    output += f"\tformat\t{spec.format};\n"
    output += f'\tarch\t"{spec.arch}";\n'
    output += f"\tclass\t{spec.foam_class};\n"
    output += f'\tlocation\t"{spec.location}";\n'
    output += f"\tobject\t{spec.foam_object};\n"
    output += "}\n\n"
    return output


def parse(content: str) -> FoamFile:

    state = ""

    header: dict = {}
    body: list = []
    body_size = -1

    working_size = 0
    working_array: list = []
    arrays: list = []

    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("//"):
            continue
        if stripped.startswith("/*"):
            state = "in_comment"
            continue
        if stripped.startswith("\\*"):
            state = ""
            continue
        if state == "in_comment":
            continue
        if stripped.startswith("FoamFile"):
            state = "in_foamfile"
            continue
        if stripped.startswith("{"):
            continue
        if stripped.startswith("}"):
            state = ""
            continue
        if state == "in_foamfile":
            split = stripped.split(" ")
            key = split[0].strip()
            value = split[-1].strip()[0:-1]  # remove trailing ;
            header[key] = value
            continue
        if state == "in_array":
            if stripped == "(":
                continue
            if stripped == ")":
                state = ""
                if len(working_array) != working_size:
                    raise RuntimeError("Array not of expected size - aborting")
                arrays.append(tuple(working_array))
                working_array = []
                working_size = -1
                continue
            inside_brackets = stripped[1:-1]
            split = inside_brackets.split(" ")
            working_array.append(tuple(float(e) for e in split))
            continue
        if state == "":
            if stripped.isnumeric():
                state = "in_array"
                working_size = int(stripped)
                continue

    return FoamFile(
        location=header["location"],
        foam_object=header["object"],
        version=header["version"],
        format=header["format"],
        arch=header["arch"],
        foam_class=header["class"],
        body_size=body_size,
        body=tuple(body),
    )


def read_foamfile(path: Path) -> FoamFile:

    with open(path, "r", encoding="utf-8") as f:
        return parse(f.read())
