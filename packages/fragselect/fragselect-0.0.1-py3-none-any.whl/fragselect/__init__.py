#!python

__project__ = "fragselect"
__version__ = "0.0.1"
__license__ = "Apache"
__description__ = "An open-source Python package of the AlphaPept ecosystem"
__author__ = "Mann Labs"
__author_email__ = "opensource@alphapept.com"
__github__ = "https://github.com/MannLabs/fragselect"
__keywords__ = [
    "bioinformatics",
    "software",
    "AlphaPept ecosystem",
]
__python_version__ = ">=3.8"
__classifiers__ = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: Scientific/Engineering :: Bio-Informatics",
]
__console_scripts__ = [
    "fragselect=fragselect.cli:run",
]
__urls__ = {
    "Mann Labs at MPIB": "https://www.biochem.mpg.de/mann",
    "Mann Labs at CPR": "https://www.cpr.ku.dk/research/proteomics/mann/",
    "GitHub": __github__,
    "PyPI": "https://pypi.org/project/fragselect/",
}
__extra_requirements__ = {
    "development": "requirements_development.txt",
}

import warnings

warnings.filterwarnings(
    "ignore", message="Numba extension module.*rocket_fft.*failed to load.*"
)
warnings.filterwarnings(
    "ignore", category=RuntimeWarning, message="Mean of empty slice"
)
warnings.filterwarnings(
    "ignore", category=RuntimeWarning, message="Degrees of freedom <= 0 for slice"
)
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message="A worker stopped while some jobs were given to the executor.*",
    module="joblib.externals.loky.process_executor",
)
warnings.filterwarnings(
    "ignore", category=RuntimeWarning, message="All-NaN slice encountered"
)
