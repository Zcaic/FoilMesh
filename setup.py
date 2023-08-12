from setuptools import setup,find_packages

setup(
    name='FoilMesh',
    author='Zcaic',
    version='0.0.1',
    description='FoilMesh is a tool to mesh airfoil structural grid',
    url="https://github.com/Zcaic/Foilmesh",
    keywords="aerodynamics cfd airfoil grid mesh",
    packages=find_packages(),
    python_requires='>=3.0',
    install_requires=[
        'numpy',
        'scipy',
        'rich'              
        ],
)