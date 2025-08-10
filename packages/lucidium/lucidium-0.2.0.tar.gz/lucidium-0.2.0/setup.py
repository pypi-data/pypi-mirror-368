"""# lucidium.setup

# Lucidium setup utility.
"""

from pathlib    import Path
from setuptools import find_packages, setup
from typing     import Any, Dict

def get_long_description():
    """# Get Long Description.
    
    Relay long description from README file.
    """
    # Open file.
    with open(Path(__file__).parent / "README.md", encoding = "utf-8") as f:
        
        # Provide content.
        return f.read()

def get_version() -> str:
    """# Get Version.
    
    Fetch version from internal version file.

    ## Returns:
        * str:  Current version.
    """
    # Initialize dictionary to store globals.
    version_vars:   Dict[str, Any] =    {}
    
    # Open file.
    with open(Path(__file__).parent / "lucidium" / "_version_.py") as f:
        
        # Read data into dictionary.
        exec(f.read(), version_vars)
        
    # Provide version.
    return version_vars["__version__"]

# Set up package.
setup(
    name =                          "lucidium",
    version =                       get_version(),
    author =                        "Gabriel C. Trahan",
    author_email =                  "gabrieltrahan777@hotmail.com",
    description =                   """Experiments in neuro-symbolic reinforcement learning in the 
                                    pursuit of developing agents/methods to aid in organic 
                                    reasoning, inference, and logic.""",
    long_description =              get_long_description(),
    long_description_content_type = "text/markdown",
    license =                       "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007",
    license_files =                 ("LICENSE"),
    url =                           "https://github.com/theokoles7/lucidium",
    packages =                      find_packages(),
    python_requires =               ">=3.10",
    install_requires =              [
                                        "dashing",
                                        "numpy",
                                        "termcolor",
                                        "torch"
                                    ],
    entry_points =                  {
                                        "console_scripts":  [
                                                                "lucidium=lucidium.__main__:main"
                                                            ],
                                    },
    classifiers =                   [
                                        "Intended Audience :: Developers",
                                        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                                        "Operating System :: OS Independent",
                                        "Programming Language :: Python :: 3",
                                        "Programming Language :: Python :: 3.10",
                                        "Programming Language :: Python :: 3.11",
                                        "Programming Language :: Python :: 3.12",
                                        "Topic :: Scientific/Engineering :: Artificial Intelligence",
                                    ],
)