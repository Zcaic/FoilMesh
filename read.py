import foilmesh as fm

af = fm.Airfoil(name="myairfoil")
# af.control.Airfoil_data=np.array([[1.00,0.95],[0.89565,0.777]])
af.readControl("./example.json")
# af.control.Output='./mesh.vtk'
af.StructureMesh()