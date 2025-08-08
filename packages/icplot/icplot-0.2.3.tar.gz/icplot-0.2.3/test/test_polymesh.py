from icplot.mesh.openfoam import polymesh
from iccore.test_utils import get_test_data_dir


def test_read_polymesh():

    data_dir = get_test_data_dir()

    mesh = polymesh.read_polymesh(data_dir / "openfoam/polymesh/basic")
    print(mesh)
