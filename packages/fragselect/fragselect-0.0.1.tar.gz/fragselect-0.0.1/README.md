![Pip installation](https://github.com/MannLabs/FragSelect/workflows/Default%20installation%20and%20tests/badge.svg)
![PyPi releases](https://github.com/MannLabs/FragSelect/workflows/Publish%20on%20PyPi%20and%20release%20on%20GitHub/badge.svg)
[![Downloads](https://pepy.tech/badge/FragSelect)](https://pepy.tech/project/FragSelect)
[![Downloads](https://pepy.tech/badge/FragSelect/month)](https://pepy.tech/project/FragSelect)
[![Downloads](https://pepy.tech/badge/FragSelect/week)](https://pepy.tech/project/FragSelect)


# FragSelect
An open-source Python package of the AlphaPept ecosystem from the [Mann Labs at the Max Planck Institute of Biochemistry](https://www.biochem.mpg.de/mann) and the [University of Copenhagen](https://www.cpr.ku.dk/research/proteomics/mann/). To enable all hyperlinks in this document, please view it at [GitHub](https://github.com/MannLabs/FragSelect).

* [**About**](#about)
* [**License**](#license)
* [**Installation**](#installation)
  * [**Pip installer**](#pip)
  * [**Developer installer**](#developer)
* [**Usage**](#usage)
  * [**CLI**](#cli)
  * [**Python and jupyter notebooks**](#python-and-jupyter-notebooks)
* [**Troubleshooting**](#troubleshooting)
* [**Citations**](#citations)
* [**How to contribute**](#how-to-contribute)
* [**Changelog**](#changelog)

---
## About

An open-source Python package of the AlphaPept ecosystem from the [Mann Labs at the Max Planck Institute of Biochemistry](https://www.biochem.mpg.de/mann) and the [University of Copenhagen](https://www.cpr.ku.dk/research/proteomics/mann/).

![Deep Learning Workflow for Quality Scoring and Protein Intensity Estimation](fragselect.png)

*Figure: Deep learning workflow for quality scoring and protein intensity estimation. The system takes mass spectrometry features as input, uses a neural network to predict quality scores, and leverages these scores to improve protein intensity estimation accuracy by distinguishing between high and low-quality measurements.*

---
## License

FragSelect was developed by the [Mann Labs at the Max Planck Institute of Biochemistry](https://www.biochem.mpg.de/mann) and the [University of Copenhagen](https://www.cpr.ku.dk/research/proteomics/mann/) and is freely available with an [Apache License](LICENSE.txt). External Python packages (available in the [requirements](requirements) folder) have their own licenses, which can be consulted on their respective websites.

---
## Installation

FragSelect can be installed and used on all major operating systems (Windows, macOS and Linux).
There are two different types of installation possible:

* [**Pip installer:**](#pip) Choose this installation if you want to use FragSelect as a Python package in an existing Python 3.8 environment (e.g. a Jupyter notebook). The CLI can be installed with pip as well.
* [**Developer installer:**](#developer) Choose this installation if you are familiar with CLI tools, [conda](https://docs.conda.io/en/latest/) and Python. This installation allows access to all available features of FragSelect and even allows to modify its source code directly. Generally, the developer version of FragSelect outperforms the precompiled versions which makes this the installation of choice for high-throughput experiments.



### Pip

FragSelect can be installed in an existing Python 3.8 environment with a single `bash` command. *This `bash` command can also be run directly from within a Jupyter notebook by prepending it with a `!`*:

```bash
pip install FragSelect
```

Installing FragSelect like this avoids conflicts when integrating it in other tools, as this does not enforce strict versioning of dependancies. However, if new versions of dependancies are released, they are not guaranteed to be fully compatible with FragSelect. While this should only occur in rare cases where dependencies are not backwards compatible, you can always force FragSelect to use dependancy versions which are known to be compatible with:

```bash
pip install "FragSelect[stable]"
```

NOTE: You might need to run `pip install pip==21.0` before installing FragSelect like this. Also note the double quotes `"`.

For those who are really adventurous, it is also possible to directly install any branch (e.g. `@development`) with any extras (e.g. `#egg=FragSelect[stable,development-stable]`) from GitHub with e.g.

```bash
pip install "git+https://github.com/MannLabs/FragSelect.git@development#egg=FragSelect[stable,development-stable]"
```

### Developer

FragSelect can also be installed in editable (i.e. developer) mode with a few `bash` commands. This allows to fully customize the software and even modify the source code to your specific needs. When an editable Python package is installed, its source code is stored in a transparent location of your choice. While optional, it is advised to first (create and) navigate to e.g. a general software folder:

```bash
mkdir ~/folder/where/to/install/software
cd ~/folder/where/to/install/software
```

***The following commands assume you do not perform any additional `cd` commands anymore***.

Next, download the FragSelect repository from GitHub either directly or with a `git` command. This creates a new FragSelect subfolder in your current directory.

```bash
git clone https://github.com/MannLabs/FragSelect.git
```

For any Python package, it is highly recommended to use a separate [conda virtual environment](https://docs.conda.io/en/latest/), as otherwise *dependancy conflicts can occur with already existing packages*.

```bash
conda create --name FragSelect python=3.8 -y
conda activate FragSelect
```

Finally, FragSelect and all its [dependancies](requirements) need to be installed. To take advantage of all features and allow development (with the `-e` flag), this is best done by also installing the [development dependencies](requirements/requirements_development.txt) instead of only the [core dependencies](requirements/requirements.txt):

```bash
pip install -e "./FragSelect[development]"
```

By default this installs loose dependancies (no explicit versioning), although it is also possible to use stable dependencies (e.g. `pip install -e "./FragSelect[stable,development-stable]"`).

***By using the editable flag `-e`, all modifications to the [FragSelect source code folder](FragSelect) are directly reflected when running FragSelect. Note that the FragSelect folder cannot be moved and/or renamed if an editable version is installed. In case of confusion, you can always retrieve the location of any Python module with e.g. the command `import module` followed by `module.__file__`.***

---
## Usage

There are two ways to use FragSelect:

* [**CLI**](#cli)
* [**Python**](#python-and-jupyter-notebooks)

NOTE: The first time you use a fresh installation of FragSelect, it is often quite slow because some functions might still need compilation on your local operating system and architecture. Subsequent use should be a lot faster.


### CLI

The CLI can be run with the following command (after activating the `conda` environment with `conda activate FragSelect` or if an alias was set to the FragSelect executable):

```bash
FragSelect -h
```

It is possible to get help about each function and their (required) parameters by using the `-h` flag.

### Python and Jupyter notebooks

FragSelect can be imported as a Python package into any Python script or notebook with the command `import FragSelect`.

A brief [Jupyter notebook tutorial](nbs/tutorial.ipynb) on how to use the API is also present in the [nbs folder](nbs).

---
## Troubleshooting

In case of issues, check out the following:

* [Issues](https://github.com/MannLabs/FragSelect/issues): Try a few different search terms to find out if a similar problem has been encountered before
* [Discussions](https://github.com/MannLabs/FragSelect/discussions): Check if your problem or feature requests has been discussed before.

---
## Citations

There are currently no plans to draft a manuscript.

---
## How to contribute

If you like this software, you can give us a [star](https://github.com/MannLabs/FragSelect/stargazers) to boost our visibility! All direct contributions are also welcome. Feel free to post a new [issue](https://github.com/MannLabs/FragSelect/issues) or clone the repository and create a [pull request](https://github.com/MannLabs/FragSelect/pulls) with a new branch. For an even more interactive participation, check out the [discussions](https://github.com/MannLabs/FragSelect/discussions) and the [the Contributors License Agreement](misc/CLA.md).

---
## Changelog

See the [HISTORY.md](HISTORY.md) for a full overview of the changes made in each version.