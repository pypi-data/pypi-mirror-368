import os
import shutil
import logging
from setuptools import setup, Extension
from setuptools.command.sdist import sdist
from Cython.Build import cythonize
import numpy as np


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REQUIRED_FILES = [
    "cxglearner/__init__.py",
    "cxglearner/tools/__init__.py",
    "cxglearner/tools/patternpiece/__init__.py",
    "cxglearner/tools/mdlgraph/__init__.py",
    "cxglearner/tools/patternpiece/ac_matcher.pyx",
    "cxglearner/tools/mdlgraph/mdl_ds.pyx",
    "cxglearner/tools/mdlgraph/atomic_operations.c"
]

for file in REQUIRED_FILES:
    if not os.path.exists(file):
        logger.error(f"Missing required file: {file}")
        raise FileNotFoundError(f"Required file missing: {file}")


class CleanSdist(sdist):
    def run(self):
        logger.info("Running CleanSdist...")
        logger.info(f"Current directory: {os.getcwd()}")
        clean_paths = [
            'cxglearner/tools/patternpiece/ac_matcher.cpp',
            'cxglearner/tools/mdlgraph/mdl_ds.c',
            'build',
            'cxglearner.egg-info'
        ]

        for path in clean_paths:
            if os.path.exists(path):
                logger.info(f"Removing: {path}")
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
        os.makedirs("cxglearner.egg-info", exist_ok=True)

        super().run()


compiler_directives = {
    'boundscheck': False,
    'wraparound': False,
    'profile': True,
    'linetrace': True,
}

extensions = [
    Extension(
        "cxglearner.tools.patternpiece.ac_matcher",
        sources=["cxglearner/tools/patternpiece/ac_matcher.pyx"],
        extra_compile_args=["-fopenmp"],
        extra_link_args=["-fopenmp"]
    ),
    Extension(
        "cxglearner.tools.mdlgraph.mdl_ds",
        sources=[
            "cxglearner/tools/mdlgraph/mdl_ds.pyx",
            "cxglearner/tools/mdlgraph/atomic_operations.c"
        ],
        extra_compile_args=["-fopenmp"],
        extra_link_args=["-fopenmp"]
    )
]

setup(
    name="cxglearner",
    packages=[
        "cxglearner",
        "cxglearner.tools",
        "cxglearner.tools.patternpiece",
        "cxglearner.tools.mdlgraph",
    ],
    package_dir={'': '.'},
    include_package_data=True,
    package_data={
        'cxglearner': ['*.py'],
        'cxglearner.tools': ['*.py'],
        'cxglearner.tools.patternpiece': ['*.pyx', '*.cpp'],
        'cxglearner.tools.mdlgraph': ['*.pyx', '*.c'],
    },
    ext_modules=cythonize(extensions, compiler_directives=compiler_directives),
    include_dirs=[np.get_include()],
    cmdclass={'sdist': CleanSdist},
    setup_requires=[
        'cython>=3.0.0',
        'numpy>=1.21.0',
        'setuptools>=62.1.0'
    ],
    install_requires=[
        'numpy>=1.21.0'
    ],
    zip_safe=False,
    options={
        'egg_info': {
            'egg_base': '.'
        }
    }
)
