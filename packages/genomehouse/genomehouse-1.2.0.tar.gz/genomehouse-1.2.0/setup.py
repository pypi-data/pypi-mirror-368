from setuptools import setup, find_packages

setup(
	name="genomehouse",
	version="1.2.0",
	description="Modular bioinformatics toolkit for sequence analysis, parsing, ML, and visualization.",
	author="Mubashir Ali",
	author_email="codewithbismillah@gmail.com",
	url="https://github.com/GenomeHouse/GenomeHouse-1.1",
	packages=find_packages(),
	install_requires=[
		"numpy",
		"pandas",
		"scikit-learn",
		"matplotlib",
		"seaborn",
		"joblib"
	],
	python_requires='>=3.8',
	entry_points={
		'console_scripts': [
			'genomehouse-cli=scripts.genomehouse_cli:main',
		],
	},
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		"Intended Audience :: Science/Research",
		"Topic :: Scientific/Engineering :: Bio-Informatics"
	],
	include_package_data=True,
	long_description=open("README.md").read(),
	long_description_content_type="text/markdown",
)
