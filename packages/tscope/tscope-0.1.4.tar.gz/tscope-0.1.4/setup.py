from setuptools import setup, find_packages
import os

# Read the README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="tscope",
    # version 将被 setuptools_scm 自动设置
    author="Henrik",
    author_email="im.zhangxc@gmail.com",
    description="A simple Python oscilloscope for displaying 1-dim dynamic data in the command line",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sszxc/TerminalScope",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[  # no external dependencies currently
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "tscope=tscope.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
