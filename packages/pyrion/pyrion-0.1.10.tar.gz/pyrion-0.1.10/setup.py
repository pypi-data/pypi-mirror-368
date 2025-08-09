#!/usr/bin/env python3
"""Setup script for pyrion C extensions.

All package metadata is in pyproject.toml - this file only handles C extensions.
"""

from setuptools import setup, Extension
import numpy as np

# C extension modules with aggressive optimization flags for genomics performance
common_flags = ["-O3", "-DNDEBUG", "-Wall"]

# Enhanced flags for faiparser to handle large genomic files
faiparser_flags = common_flags + [
    "-D_FILE_OFFSET_BITS=64",  # Enable large file support (>2GB genomic files)
    "-D_GNU_SOURCE",           # Enable GNU extensions (strndup, etc.)
    "-funroll-loops",          # Unroll loops for better performance
    "-finline-functions",      # Inline small functions
]

ext_modules = [
    Extension(
        "pyrion._chainparser",
        sources=["csrc/chainparser.c"],
        include_dirs=[np.get_include()],
        extra_compile_args=common_flags,
    ),
    Extension(
        "pyrion._bed12parser",
        sources=["csrc/bed12parser.c"],
        include_dirs=[np.get_include()],
        extra_compile_args=common_flags,
    ),
    Extension(
        "pyrion._fastaparser",
        sources=["csrc/fastaparser.c"],
        include_dirs=[np.get_include()],
        extra_compile_args=common_flags,
    ),
    Extension(
        "pyrion._narrowbedparser",
        sources=["csrc/narrowbedparser.c"],
        include_dirs=[np.get_include()],
        extra_compile_args=common_flags,
    ),
    Extension(
        "pyrion._faiparser",
        sources=["csrc/faiparser.c"],
        extra_compile_args=faiparser_flags,
    ),
    Extension(
        "pyrion._gtfparser",
        sources=["csrc/gtfparser.c"],
        include_dirs=[np.get_include()],
        extra_compile_args=common_flags,
    ),
]

if __name__ == "__main__":
    setup(ext_modules=ext_modules)