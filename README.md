A convenient program produces airfoil structural meshes and exports them in a variety of formats.<br>
![mesh zoom](./assert/mesh_zoom.gif "mesh")<br>

# Install
1. 
    ```
    pip install foilmesh
    ```
2.
    ```
    git clone https://github.com/Zcaic/Foilmesh.git
    cd Foilmesh && pip install .
    ```

# usage
```
import foilmesh as fm

af = fm.Airfoil(name="myairfoil")
# af.control.Airfoil_data=np.array([[1.00,0.95],[0.89565,0.777]])
af.readControl("./example.json")
af.StructureMesh()
```
