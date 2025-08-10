# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['urbanity']

package_data = \
{'': ['*'],
 'urbanity': ['building_height_data/*',
              'ghs_data/*',
              'lcz_data/*',
              'map_data/*',
              'overture_data/*',
              'svi_data/num_to_class.json',
              'svi_data/num_to_class.json',
              'svi_data/svi_data.json',
              'svi_data/svi_data.json']}

install_requires = \
['dotenv>=0.9.9,<0.10.0',
 'geopandas>=1.0.1,<2.0.0',
 'ipykernel==6.16.2',
 'ipyleaflet==0.17.2',
 'ipywidgets==8.0.2',
 'mercantile>=1.2.1,<2.0.0',
 'networkx==2.8.6',
 'numpy==1.26.4',
 'pandas>=2.2.2,<3.0.0',
 'pydeck>=0.9.1,<0.10.0',
 'rasterio>=1.3.8,<2.0.0']

extras_require = \
{'osm': ['pyrosm==0.6.2', 'protobuf==3.20.0', 'pyrobuf>=0.9.3,<0.10.0']}

setup_kwargs = {
    'name': 'urbanity',
    'version': '0.5.15',
    'description': 'A python package to generate urban graphs for any geographical location and scale',
    'long_description': None,
    'author': 'winstonyym',
    'author_email': 'winstonyym@u.nus.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
