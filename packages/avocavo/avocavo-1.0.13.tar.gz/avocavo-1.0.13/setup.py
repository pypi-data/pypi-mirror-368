"""
Setup configuration for Avocavo Python SDK
"""

from setuptools import setup, find_packages
import os

# Read long description from README
def read_long_description():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "Avocavo Python SDK - Nutrition analysis made simple with secure USDA data access"

# Read version from package
def get_version():
    version_file = os.path.join("avocavo", "__init__.py")
    with open(version_file, "r") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split('"')[1]
    return "1.0.0"

setup(
    name="avocavo",
    version=get_version(),
    author="Avocavo",
    author_email="api-support@avocavo.com",
    description="Avocavo Python SDK - Nutrition analysis made simple with secure USDA data access",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/avocavo/avocavo-python",
    project_urls={
        "Documentation": "https://nutrition.avocavo.app/docs/python",
        "API Dashboard": "https://nutrition.avocavo.app",
        "Bug Tracker": "https://github.com/avocavo/avocavo-python/issues",
        "Changelog": "https://github.com/avocavo/avocavo-python/blob/main/CHANGELOG.md",
        "Support": "https://nutrition.avocavo.app/support",
        "Homepage": "https://avocavo.app",
    },
    classifiers=[
        # Development Status
        "Development Status :: 5 - Production/Stable",
        
        # Intended Audience
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        
        # Topic
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Database :: Front-Ends",
        
        # License
        "License :: OSI Approved :: MIT License",
        
        # Python versions
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8", 
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        
        # Operating System
        "Operating System :: OS Independent",
        
        # Natural Language
        "Natural Language :: English",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "keyring>=24.0.0",  # For secure API key storage
        "supabase>=2.8.0",  # For unified OAuth authentication
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
            "twine>=4.0",
            "wheel>=0.40",
        ],
        "test": [
            "pytest>=7.0",
            "pytest-mock>=3.10",
            "responses>=0.23.0",
            "pytest-asyncio>=0.21.0",
        ],
        "docs": [
            "sphinx>=6.0",
            "sphinx-rtd-theme>=1.2",
            "myst-parser>=1.0",
        ],
    },
    keywords=[
        "nutrition", "api", "usda", "food", "recipe", "health", "fitness", 
        "calories", "macros", "nutrients", "fooddata", "fdc", "cooking",
        "meal-planning", "diet", "wellness", "avocavo", "secure"
    ],
    include_package_data=True,
    zip_safe=False,
    
    # Security metadata
    options={
        "metadata": {
            "security_contact": "security@avocavo.com"
        }
    },
    
    # Package metadata
    platforms=["any"],
    license="MIT",
    
    # Additional metadata for PyPI
    download_url="https://pypi.org/project/avocavo/",
)