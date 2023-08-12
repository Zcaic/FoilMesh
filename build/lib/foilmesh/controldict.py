import numpy as np
from pathlib import Path
from typing import Union


extension = {
    ".flma": "FLMA",
    ".su2": "SU2",
    ".msh": "GMSH",
    ".vtk": "VTK",
    ".cgns": "CGNS",
    ".inp": "ABAQUS",
    ".obj": "OBJ",
}


class ControlDict:
    """
    input:\n
        Airfoil_file: a airfoil file contains coordinates
        Airfoil_data: a ndarray contains coordinates
        note: Airdoil_file and Airfoil_data only one can be defined

        Output: the output mesh name with suffix ( \n
            AVL FIRE : .flma,\n
            SU2 : .su2,\n
            GMSH : .msh,\n
            VTK : .vtk,\n
            CGNS : .cgns,\n
            ABAQUS : .inp,\n
            OBJ : .obj\n
            )\n
        other mesh control parameters can be find: \n
        https://pyaero.readthedocs.io/en/latest/

    """

    Airfoil_file: Union[str, Path] = None
    Airfoil_data: np.ndarray = None

    Output: str = None

    Spline_refine = {
        "Refinement tolerance": 172.0,
        "Refine trailing edge old": 3,
        "Refine trailing edge new": 6,
        "Refine trailing edge ratio": 3,
        "Number of points on spline": 200,
    }

    Trailing_edges: bool = False
    Trailing_control = {
        "Upper side blending length": 30.0,
        "Lower side blending length": 30.0,
        "Upper blending polynomial exponent": 3,
        "Lower blending polynomial exponent": 3,
        "Trailing edge thickness relative to chord": 0.4,
    }

    Airfoil_mesh = {
        "Divisions normal to airfoil": 15,
        "1st cell layer thickness": 0.004,
        "Cell growth rate": 1.05,
    }

    Trailing_mesh = {
        "Divisions at trailing edge": 3,
        "Divisions downstream": 15,
        "1st cell layer thickness": 0.004,
        "Cell growth rate": 1.05,
    }

    Windtunnel_airfoil = {
        "Windtunnel height": 3.5,
        "Divisions of tunnel height": 100,
        "Cell thickness ratio": 10.0,
        "Distribution biasing": "symmetric",
        "Smoothing algorithm": "elliptic",
        "Smoothing iterations": 20,
        "Smoothing tolerance": 1.2e-5,
    }

    Windtunnel_wake = {
        "Windtunnel wake": 7.0,
        "Divisions in the wake": 100,
        "Cell thickness ratio": 15.0,
        "Equalize vertical wake line at": 30.0,
    }
