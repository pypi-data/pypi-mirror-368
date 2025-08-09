from setuptools import setup, find_packages

setup(
    name='constellaxion_utils',
    version='1.0.0',
    packages=find_packages(include=['constellaxion_utils', 'constellaxion_utils.*']),  # Ensure subpackages are included
    install_requires=[
        'gcsfs',
        'watchdog'
    ],
    author='Constellaxion Technologies, Inc.',
    author_email='dev@constellaxion.ai',
    description='The Utils package for constellaXion CLI jobs',
    include_package_data=True,  # Ensures all package data is included
)