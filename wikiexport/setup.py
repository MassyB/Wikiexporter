from setuptools import setup, find_packages

requirements = [r.strip() for r in open('requirements.txt').readlines()]

setup(
    name='wikiexport',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points='''
        [console_scripts]
        wikiexport=src.main:main
    ''',
)