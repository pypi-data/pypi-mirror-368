import setuptools
import onkopus as op

with open("README.md", "r") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

version = op.conf_reader.config["DEFAULT"]["VERSION"]

setuptools.setup(
    name="onkopus",
    version=version,
    author="Nadine S. Kurz",
    author_email="nadine.kurz@bioinf.med.uni-goettingen.de",
    description="Variant interpretation framework to analyze and interpret genetic alterations in cancer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    scripts=['./onkopus/onkopus'],
    url="https://gitlab.gwdg.de/MedBioinf/mtb/onkopus/onkopus",
    packages=setuptools.find_packages(),
    install_requires=['requests','numpy','matplotlib','pandas','plotly','scikit-learn','async-timeout','redis','pyaml','adagenes'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.9',
    license="GPLv3",
    include_package_data=True
)