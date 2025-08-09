import os
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install


class CustomInstallCommand(install):
    """Optionally print a message about running slips-setup manually."""
    def run(self):
        install.run(self)
        print("\n[INFO] Installation complete.\nTo install system-level dependencies, run:\n  slips-setup\n")


setup(
    name="slips-sdk",
    version="0.1.11",
    author="Jenil Vekariya",
    author_email="vekariyajenil888@gmail.com",
    description="SDK for interacting with slips IDS components",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jenilv-07/slips-sdk.git",  # Replace with your real repo
    project_urls={
        "Documentation": "https://github.com/jenilv-07/slips-sdk#readme",
        "Source": "https://github.com/jenilv-07/slips-sdk",
        "Issues": "https://github.com/jenilv-07/slips-sdk/issues",
    },
    packages=find_packages(include=["slips", "slips.*"]),
    include_package_data=True,
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: GNU Affero General Public License v3",
    ],
    python_requires='>=3.10',
    cmdclass={
        'install': CustomInstallCommand,
    },
    entry_points={
        'console_scripts': [
            'slips-setup=slips.slips_setup:main',
        ],
    },
)
