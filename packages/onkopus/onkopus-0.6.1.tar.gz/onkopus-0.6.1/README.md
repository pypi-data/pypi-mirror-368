
![Onkopus](https://gitlab.gwdg.de/MedBioinf/mtb/onkopus/onkopus/-/raw/main/assets/onkopus_logo_v0.1.4.2_150.png?inline=false)

# Onkopus: A modular variant interpretation framework

[![pipeline](https://gitlab.gwdg.de/MedBioinf/mtb/onkopus/onkopus/badges/main/pipeline.svg)](https://gitlab.gwdg.de/MedBioinf/mtb/onkopus/onkopus) |
[![commits](https://gitlab.gwdg.de/MedBioinf/mtb/onkopus/onkopus/-/jobs/artifacts/main/raw/commits.svg?job=build_badges)](https://gitlab.gwdg.de/MedBioinf/mtb/adagenes)
[![license](https://gitlab.gwdg.de/MedBioinf/mtb/onkopus/onkopus/-/jobs/artifacts/main/raw/license.svg?job=build_badges)](https://gitlab.gwdg.de/MedBioinf/mtb/adagenes)
[![coverage](https://gitlab.gwdg.de/MedBioinf/mtb/onkopus/onkopus/badges/main/coverage.svg)](https://gitlab.gwdg.de/MedBioinf/mtb/onkopus/onkopus)
[![python_version](https://gitlab.gwdg.de/MedBioinf/mtb/onkopus/onkopus/-/jobs/artifacts/main/raw/python_version.svg?job=build_badges)](https://gitlab.gwdg.de/MedBioinf/mtb/adagenes)
[![release](https://gitlab.gwdg.de/MedBioinf/mtb/onkopus/onkopus/-/badges/release.svg)](https://gitlab.gwdg.de/MedBioinf/mtb/onkopus/onkopus)

## What is Onkopus?

Onkopus is an easy-to-use cancer variant interpretation framework to annotate, interpret 
and prioritize genetic alterations in cancer. 
Onkopus provides annotation for different mutation types including a wide range of features, including 
genomic, transcriptomic and protein information, biochemical features, pathogenicty prediction, 
functional effect prediction, and potential therapies. 


## Getting started

Install the Onkopus python package via pip:
```bash
python -m pip install onkopus
```

You can use Onkopus both as a command line tool and in python. 
All modules can also be installed locally as well. 

### Use Onkopus from the command line

Onkopus provides a command line tool to directly annotate variant files. 
Run the ```onkopus``` tool by specifying an input file (`-i`) and the genome version (`-g`) ('hg19'/'hg38'/'t2t'). 
Optionally pass an output file (`-o`) and specific modules (`-m`):  
```bash
onkopus run -i somatic_mutations.vcf -g hg38 -o somatic_mutations.ann.vcf
```
(Note: This will annotate will all Onkopus modules, including potential therapies and drug classifications. 
Since this process may take a while, use it only for small to medium-sized variant files.)

To functionally annotate large VCF files, run
```commandline
onkopus run -i somatic_mutations.vcf -g hg38 -m functional_annotation -o somatic_mutations.fn.ann.vcf
```

To annotate with specific Onkopus modules, select the module with the `-m` option:
```commandline
onkopus run -i somatic_mutations.vcf -g hg38 -m alphamissense
onkopus run -i somatic_mutations.vcf -g hg38 -m revel,primateai
```

Liftover between reference genomes: Use the `-g` option to define the source file's genome version, and the `-t` 
option to define the target genome (here: hg19 to hg38). 
```commandline
onkopus run -i somatic_mutations.vcf -m liftover -g hg19 -t hg38
```

To test Onkopus with one of the built-in sample VCF files, run:
```bash
onkopus run -i somaticMutations.vcf -md test -g hg38 -o somaticMutations.ann.vcf

```

#### Liftover

To convert a variant file into another genome assembly, use the AdaGenes Liftover module integrated in Onkopus. Use 
`g` to specifiy the reference genome of the source file, and the `-t` option for the reference genome the file 
should be converted to (hg19/hg38/t2t).

```commandline
onkopus run -i somaticMutations.vcf -m liftover -g hg19 -t hg38 -o somaticMutations.GRCh38.vcf
```

### Install Onkopus locally

By default, Onkopus accesses the publicly available modules to annotate variants. 
It is also possible to install Onkopus completely locally, e.g. to process sensitive patient data. 

To install Onkopus locally, make sure that you have installed Docker on your host system. 

To change the configuration to use locally running modules, configure the following environment variables before you 
start Onkopus: 
```commandline
export ONKOPUS_MODULE_PROTOCOL=https
export ONKOPUS_MODULE_SERVER=localhost
export ONKOPUS_PORTS_ACTIVE=1
```

In the next step, you can install the Onkopus modules individually or all together. To install an 
Onkopus module, run `onkopus install -m ` followed by the module identifier, e.g.  
```commandline
onkopus install -m clinvar
```
Run `onkopus list-modules` to get a complete list of all available modules. 
To install all available modules in one step, run 
```commandline
onkopus install -m all
```
(Note: This will install all available Onkopus modules. The required databases are installed as soon as you start 
Onkopus.)

After you have installed all the modules you need, you can start Onkopus with 
```commandline
onkopus start
```

To make sure that the installation and start of the modules was successful, you can run
```commandline
docker ps
```
If the Onkopus modules have been successfully started, you should see an overview of the running modules. 

To stop all Onkopus modules, run 
```commandline
onkopus stop
```

### Use Onkopus from Python

You can also use Onkopus to directly load your variant data in your Python code as an AdaGenes biomarker frame.
(Note: This will load the entire variant data into memory and is thus only applicable for small to medium sized variant 
files.)
Use Onkopus from Python by running the full annotation pipeline or instantiate 
custom Onkopus clients and calling `process_data`:

#### Annotate variants with all modules

For a complete variant annotation, including functional and clinical annotation, run

```python
import onkopus as op

bframe = op.read_file('./somatic_mutations.vcf', genome_version="hg38", input_format="vcf")
bframe = op.annotate(bframe)
```

#### Annotate with specific modules

```python
import onkopus as op

genome_version="hg38"
bframe = op.read_file('./somatic_mutations.vcf', input_format='vcf')

# Annotate with ClinVar
client = op.ClinVarClient(genome_version=genome_version)
bframe.data = client.process_data(bframe.data)

# Annotate with AlphaMissense
client = op.AlphaMissenseClient(genome_version=genome_version)
bframe.data = client.process_data(bframe.data)

op.write_file('./somatic_mutations.annotated.vcf', bframe)
```

## License

GPLv3

## Documentation

A detailed documentation on how to use the Onkopus web application, the CLI and the python package 
can be found on the public [Onkopus website](https://mtb.bioinf.med.uni-goettingne.de/onkopus). 

## Public version

A public instance of Onkopus Web is available at [https://mtb.bioinf.med.uni-goettingen.de/onkopus](https://mtb.bioinf.med.uni-goettingen.de/onkopus). 
