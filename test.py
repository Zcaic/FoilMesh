import json
from pathlib import Path

from foilmesh.airfoil import Airfoil
from foilmesh.splinerefine import SplineRefine
from foilmesh.trailingedge import TrailingEdge
from foilmesh import meshing as meshing
from foilmesh import connect

# from FoilMesh import controldict

# controldict.ControlDict.Airfoil_data

with open("batch.json", "r") as fin:
    batch_control = json.load(fin)
    # print(batch)

airfoil_path = batch_control["Airfoils"]["path"]
mesh_path = batch_control["Output formats"]["path"]
output_formats = batch_control["Output formats"]["formats"]

airfoils = batch_control["Airfoils"]["names"]
trailing_edges = batch_control["Airfoils"]["trailing_edges"]


message = "Airfoils files to mesh:"
print(message)
for airfoil in airfoils:
    message = f"     --> {airfoil}"
    print(message)
print("\n")

for i, airfoil in enumerate(airfoils):
    message = f"Starting Structure meshing for airfoil {airfoil}"
    print(message)
    basename = Path(airfoil).stem
    af = Airfoil(name=basename)
    af.readContour(Path(airfoil_path) / airfoil, "#")

    refinement = batch_control["Airfoil contour refinement"]
    refine = SplineRefine(af)
    refine.doSplineRefine(
        tolerance=refinement["Refinement tolerance"],
        points=refinement["Number of points on spline"],
        ref_te=refinement["Refine trailing edge old"],
        ref_te_n=refinement["Refine trailing edge new"],
        ref_te_ratio=refinement["Refine trailing edge ratio"],
    )

    if trailing_edges[i] == "yes":
        af.has_TE = True

        te = batch_control["Airfoil trailing edge"]

        trailing = TrailingEdge(af)

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

    wind_tunnel = meshing.Windtunnel(af)
    contour = af.spline_data[0]

    acm = batch_control["Airfoil contour mesh"]

    # mesh around airfoil
    wind_tunnel.AirfoilMesh(
        name="block_airfoil",
        contour=contour,
        divisions=acm["Divisions normal to airfoil"],
        ratio=acm["Cell growth rate"],
        thickness=acm["1st cell layer thickness"],
    )

    # mesh at trailing edge
    tem = batch_control["Airfoil trailing edge mesh"]
    wind_tunnel.TrailingEdgeMesh(
        name="block_TE",
        te_divisions=tem["Divisions at trailing edge"],
        thickness=tem["1st cell layer thickness"],
        divisions=tem["Divisions downstream"],
        ratio=tem["Cell growth rate"],
    )

    # mesh tunnel airfoil
    tam = batch_control["Windtunnel mesh airfoil"]
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
    twm = batch_control["Windtunnel mesh wake"]
    wind_tunnel.TunnelMeshWake(
        name="block_tunnel_wake",
        tunnel_wake=twm["Windtunnel wake"],
        divisions=twm["Divisions in the wake"],
        ratio=twm["Cell thickness ratio"],
        spread=twm["Equalize vertical wake line at"] / 100.0,
    )

    connect = connect.Connect(None)
    vertices, connectivity, _ = connect.connectAllBlocks(wind_tunnel.blocks)

    # add mesh to Wind-tunnel instance
    wind_tunnel.mesh = vertices, connectivity

    # generate cell to edge connectivity from mesh
    wind_tunnel.makeLCE()

    # generate cell to edge connectivity from mesh
    wind_tunnel.makeLCE()

    # generate boundaries from mesh connectivity
    wind_tunnel.makeBoundaries()

    message = f"Finished batch meshing for airfoil {airfoil}"
    print(message)

    message = f"Starting mesh export for airfoil {airfoil}"
    print(message)

    for output_format in output_formats:
        extension = {
            "FLMA": ".flma",
            "SU2": ".su2",
            "GMSH": ".msh",
            "VTK": ".vtk",
            "CGNS": ".cgns",
            "ABAQUS": ".inp",
            "OBJ": ".obj",
        }
        
        mesh_name = Path(mesh_path)/(basename + extension[output_format])
        getattr(meshing.BlockMesh, 'write'+output_format)(wind_tunnel, name=mesh_name)

        message = f'Finished mesh export for airfoil {airfoil} to {mesh_name}'
        print(message)



