from pathlib import Path
import os
import re
from setuptools import setup, find_packages


def get_version():
    with open(os.path.join("simple_report", "__init__.py"), "r") as f:
        match = re.search(r'__version__ = ["\'](.+?)["\']', f.read())
        return match.group(1)


# Read the contents of README file
source_root = Path(".")
with (source_root / "README.md").open(encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="simple-report",
    version=get_version(),
    author="Douglas Sgrott",
    author_email="doug.sgrott@gmail.com",
    packages=find_packages(),
    # package_dir={"": "simple_report"},
    url="https://github.com/dougsgrott/simple-report",
    license="MIT",
    description="Simple HTML report generation using Python",
    python_requires=">=3.6",
    # install_requires=requirements,
    extras_require={
        "notebook": [
            "jupyter-client>=5.3.4",
            "jupyter-core>=4.6.3",
            "ipywidgets>=7.5.1",
        ],
    },
    package_data={
        "simple_report": ["py.typed"],
    },
    include_package_data=True,
)
