from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from pathlib import Path

class PreBuiltExtension(build_ext):
    """Skip build - assume .so files are already built by CMake"""
    def run(self):
        # Just check if the .so files exist
        so_files = list(Path("lattica_fhe_core").glob("*.so")) + \
                   list(Path("lattica_fhe_core").glob("*.dylib"))
        if not so_files:
            print("WARNING: No .so/.dylib files found in lattica_fhe_core/")
            print("Run build_scripts/builder.sh first!")

if __name__ == "__main__":
    setup(
        ext_modules=[Extension("lattica_fhe_core.cpp_sdk", [])],
        cmdclass={"build_ext": PreBuiltExtension},
    )