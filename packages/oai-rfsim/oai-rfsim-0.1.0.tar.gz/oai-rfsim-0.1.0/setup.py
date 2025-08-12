from __future__ import annotations

from pathlib import Path
from setuptools import setup, find_packages

# The README at the repository root contains the long description.  We
# deliberately keep it short here because the package documentation
# resides under ``share/oai_rfsim/README.md``.
readme_path = Path(__file__).resolve().parent / "README.md"
try:
    with readme_path.open("r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Helper tools for OpenAirInterface RF simulator"

setup(
    name="oai-rfsim",
    version="0.1.0",
    author="OpenAI Assistant",
    description="Helper tools to build and run OpenAirInterface gNB/UE in RF simulator mode",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=["oai_rfsim"],
    # The ``oai_rfsim`` package lives at the repository root in the
    # ``oai_rfsim`` directory.  Avoid referring to the old ``share``
    # location so that pip can locate the package correctly when
    # installed from a source archive.
    package_dir={"oai_rfsim": "oai_rfsim"},
    include_package_data=True,
    install_requires=[],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "oai-rfsim=oai_rfsim.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)