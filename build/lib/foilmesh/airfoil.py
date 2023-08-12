import numpy as np
from pathlib import Path
import json

from foilmesh.splinerefine import SplineRefine
from foilmesh.trailingedge import TrailingEdge
from foilmesh import meshing as meshing

from foilmesh import connect
from foilmesh.controldict import ControlDict, extension

import logging
from typing import Union

from foilmesh.utils import timer

logger = logging.getLogger(__name__)


class Airfoil:
    """Class to read airfoil data from file (or use predefined airfoil)

    Attributes:
        penwidth (float): thickness of airfoil outline
        raw_coordinates (numpy array): list of contour points as tuples
    """

    def __init__(self, name):
        # get MainWindow instance (overcomes handling parents)
        # self.mainwindow = QtCore.QCoreApplication.instance().mainwindow

        self.name = name
        self.chord = None
        self.has_TE = False
        # self.contourPolygon = None
        # self.contourSpline = None
        self.spline_data = None
        self.raw_coordinates = None
        # self.penwidth = 4.0
        self.control = ControlDict

    def readContour(self, filename: Union[str, np.ndarray]):
        if isinstance(filename, np.ndarray):
            filename = filename.astype("str").tolist()
            data = [" ".join(i) for i in filename]
        else:
            try:
                with open(filename, mode="r") as f:
                    lines = f.readlines()
            except IOError as error:
                # exc_info=True sends traceback to the logger
                logger.error(
                    "Failed to open file {} with error {}".format(filename, error),
                    exc_info=True,
                )
                return False

            data = [line.strip() for line in lines[1:] if line.strip() != ""]

        # find and drop duplicate points (except first and last)
        data_clean = list()
        for index, line in enumerate(data):
            if index == 0:
                data_clean.append(line)
                continue
            elif index == len(data) - 1:
                data_clean.append(line)
                break

            if line != data[index - 1]:
                data_clean.append(line)
            else:
                logger.info("Dropped duplicate point {}".format(line))

        # check for correct data
        # specifically important for drag and drop
        try:
            x = [float(l.split()[0]) for l in data_clean]
            y = [float(l.split()[1]) for l in data_clean]
        except (ValueError, IndexError) as error:
            logger.error("Unable to parse file file {}".format(filename))
            logger.error("Following error occured: {}".format(error))
            return False
        except:
            # exc_info=True sends traceback to the logger
            logger.error(
                "Unable to parse file file {}. Unknown error caught".format(filename),
                exc_info=True,
            )
            return False

        # store airfoil coordinates as list of tuples
        self.raw_coordinates = np.array((x, y))

        # normalize airfoil to unit chord
        self.raw_coordinates[0] -= np.min(x)
        divisor = np.max(self.raw_coordinates[0])
        self.raw_coordinates[0] /= divisor
        self.raw_coordinates[1] /= divisor

        self.offset = [np.min(y), np.max(y)]
        return True

    def readControl(self, jsonfile):
        with open(jsonfile, "r") as fin:
            data = json.load(fin)
        self.control.Airfoil_file = data["Airfoil_file"]
        self.control.Output = data["Output"]
        self.control.Spline_refine.update(data["Spline_refine"])
        self.control.Trailing_edges = data["Trailing_edges"]
        self.control.Trailing_control.update(data["Trailing_control"])
        self.control.Airfoil_mesh.update(data["Airfoil_mesh"])
        self.control.Trailing_mesh.update(data["trailing_mesh"])
        self.control.Windtunnel_airfoil.update(data["Windtunnel_airfoil"])
        self.control.Windtunnel_wake.update(data["Windtunnel_wake"])

    @timer
    def StructureMesh(self):
        if (
            self.control.Airfoil_data is not None
            and self.control.Airfoil_file is not None
        ):
            logging.error("Airdoil_file and Airfoil_data only one can be defined!")
        else:
            print(f'---> Airfoil "{self.name}" to mesh --->')
            print("---> Start mesh structure gird --->")
            if self.control.Airfoil_file is not None:
                self.readContour(self.control.Airfoil_file)
            else:
                self.readContour(self.control.Airfoil_data)
            refine = SplineRefine(self)
            refine.doSplineRefine(
                tolerance=self.control.Spline_refine["Refinement tolerance"],
                points=self.control.Spline_refine["Number of points on spline"],
                ref_te=self.control.Spline_refine["Refine trailing edge old"],
                ref_te_n=self.control.Spline_refine["Refine trailing edge new"],
                ref_te_ratio=self.control.Spline_refine["Refine trailing edge ratio"],
            )

            if self.control.Trailing_edges:
                self.has_TE = True
                te = self.control.Trailing_control
                trailing = TrailingEdge(self)
                trailing.trailingEdge(
                    blend=te["Upper side blending length"] / 100.0,
                    ex=te["Upper blending polynomial exponent"],
                    thickness=te["Trailing edge thickness relative to chord"],
                    side="upper",
                )
                trailing.trailingEdge(
                    blend=te["Lower side blending length"] / 100.0,
                    ex=te["Lower blending polynomial exponent"],
                    thickness=te["Trailing edge thickness relative to chord"],
                    side="lower",
                )

            wind_tunnel = meshing.Windtunnel(self)
            contour = self.spline_data[0]

            # mesh around airfoil
            acm = self.control.Airfoil_mesh
            wind_tunnel.AirfoilMesh(
                name="block_airfoil",
                contour=contour,
                divisions=acm["Divisions normal to airfoil"],
                ratio=acm["Cell growth rate"],
                thickness=acm["1st cell layer thickness"],
            )

            # mesh at trailing edge
            tem = self.control.Trailing_mesh
            wind_tunnel.TrailingEdgeMesh(
                name="block_TE",
                te_divisions=tem["Divisions at trailing edge"],
                thickness=tem["1st cell layer thickness"],
                divisions=tem["Divisions downstream"],
                ratio=tem["Cell growth rate"],
            )

            # mesh tunnel airfoil
            tam = self.control.Windtunnel_airfoil
            wind_tunnel.TunnelMesh(
                name="block_tunnel",
                tunnel_height=tam["Windtunnel height"],
                divisions_height=tam["Divisions of tunnel height"],
                ratio_height=tam["Cell thickness ratio"],
                dist=tam["Distribution biasing"],
                smoothing_algorithm=tam["Smoothing algorithm"],
                smoothing_iterations=tam["Smoothing iterations"],
                smoothing_tolerance=tam["Smoothing tolerance"],
            )

            # mesh tunnel wake
            twm = self.control.Windtunnel_wake
            wind_tunnel.TunnelMeshWake(
                name="block_tunnel_wake",
                tunnel_wake=twm["Windtunnel wake"],
                divisions=twm["Divisions in the wake"],
                ratio=twm["Cell thickness ratio"],
                spread=twm["Equalize vertical wake line at"] / 100.0,
            )
            cnt=connect.Connect(None)
            # connect = connect.Connect(None)
            vertices, connectivity, _ = cnt.connectAllBlocks(wind_tunnel.blocks)

            # add mesh to Wind-tunnel instance
            wind_tunnel.mesh = vertices, connectivity

            # generate cell to edge connectivity from mesh
            wind_tunnel.makeLCE()

            # generate cell to edge connectivity from mesh
            wind_tunnel.makeLCE()

            # generate boundaries from mesh connectivity
            wind_tunnel.makeBoundaries()

            print("<--- Finished meshing <---")
            print("---> Starting mesh export --->")

            mesh_name = Path(self.control.Output)
            getattr(meshing.BlockMesh, "write" + extension[mesh_name.suffix])(
                wind_tunnel, name=mesh_name
            )

            print("<--- Finished mesh export <---")


if __name__ == "__main__":
    import foilmesh as fm

    af = fm.Airfoil(name="myairfoil")
    # af.control.Airfoil_data=np.array([[1.00,0.95],[0.89565,0.777]])
    af.readControl("./example.json")
    af.StructureMesh()
