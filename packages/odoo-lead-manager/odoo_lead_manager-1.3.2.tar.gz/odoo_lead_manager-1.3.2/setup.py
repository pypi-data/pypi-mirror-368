#!/usr/bin/env python3
"""
Setup script for odoo-lead-manager package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as fh:
            return fh.read()
    return "A comprehensive Python package for managing Odoo leads with smart distribution"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    return []

setup(
    name="odoo-lead-manager",
    version="1.3.2",
    author="Lead Management Team",
    author_email="team@example.com",
    description="Comprehensive Python package for managing Odoo leads with smart distribution",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/example/odoo-lead-manager",
    project_urls={
        "Bug Tracker": "https://github.com/example/odoo-lead-manager/issues",
        "Documentation": "https://github.com/example/odoo-lead-manager#readme",
        "Source Code": "https://github.com/example/odoo-lead-manager",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "pytest-mock>=3.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.910",
        ],
        "mcp": [
            "fastmcp>=0.4.0",
            "typing-extensions>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "odoo-lead-manager=odoo_lead_manager.cli:main",
            "odlm=odoo_lead_manager.cli:main",
            "odoo-mcp-server=mcp_server:main",
        ],
    },
    keywords="odoo, lead, management, distribution, crm, sales, automation",
    include_package_data=True,
    zip_safe=False,
)
