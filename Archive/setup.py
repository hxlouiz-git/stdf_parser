import glob
import os
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
from setuptools.command.install_lib import install_lib

# Try to import Cython, but make it optional
try:
    from Cython.Build import cythonize
    USE_CYTHON = True
except ImportError:
    USE_CYTHON = False
    print("Cython not available, installing without compilation")

# Check environment variable to disable Cython
if os.environ.get('STDF_PARSER_NO_CYTHON', '').lower() in ('1', 'true', 'yes'):
    USE_CYTHON = False
    print("Cython disabled via STDF_PARSER_NO_CYTHON environment variable")

# All .py source files to compile except __init__.py (which only has imports)
source_files = [
    f for f in glob.glob("stdf_parser/*.py")
    if not f.endswith("__init__.py")
]

# Module names that will have compiled .pyd counterparts
compiled_modules = {
    os.path.splitext(os.path.basename(f))[0] for f in source_files
} if USE_CYTHON else set()


class BuildPyExcludeSource(build_py):
    """Skip .py files that are compiled by Cython so source is not in the wheel."""
    def find_package_modules(self, package, package_dir):
        modules = super().find_package_modules(package, package_dir)
        return [
            (pkg, mod, path)
            for pkg, mod, path in modules
            if mod == "__init__" or mod not in compiled_modules
        ]


class InstallLibExcludeC(install_lib):
    """Exclude generated .c files from the installed wheel."""
    def install(self):
        outfiles = super().install()
        if outfiles:
            outfiles = [f for f in outfiles if not f.endswith('.c')]
        return outfiles


setup_kwargs = {
    "packages": find_packages(),
}

if USE_CYTHON:
    setup_kwargs["ext_modules"] = cythonize(
        source_files,
        build_dir="build_cython",   # .c files go here, not into stdf_parser/
        compiler_directives={"language_level": "3"},
        annotate=False,
    )
    setup_kwargs["cmdclass"] = {
        "build_py": BuildPyExcludeSource,
        "install_lib": InstallLibExcludeC,
    }
    setup_kwargs["package_data"] = {"stdf_parser": ["*.pyd"]}
    setup_kwargs["exclude_package_data"] = {"stdf_parser": ["*.c", "*.py"]}

setup(**setup_kwargs)
