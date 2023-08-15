from setuptools import setup,find_packages
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='FoilMesh',
    author='Zcaic',
    version='0.0.2',
    description='FoilMesh is a tool to mesh airfoil structural grid',
    long_description=long_description,
    long_description_content_type='text/markdown',
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