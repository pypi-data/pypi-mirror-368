"""
Setup script for libadic Python bindings

This uses CMake to build the C++ library and pybind11 bindings
"""

import os
import re
import subprocess
import sys
from pathlib import Path

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext


class CMakeExtension(Extension):
    """Extension that triggers CMake build"""
    def __init__(self, name, sourcedir=""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    """Custom build command that runs CMake"""
    
    def build_extension(self, ext):
        # Check for required tools
        try:
            subprocess.check_output(["cmake", "--version"])
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "CMake is required to build libadic. "
                "Please install CMake (>=3.14) and ensure it's in your PATH. "
                "Visit https://cmake.org/download/ for installation instructions."
            )
        
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        
        # Required for auto-detection of auxiliary "native" libs
        if not extdir.endswith(os.path.sep):
            extdir += os.path.sep
        
        debug = int(os.environ.get("DEBUG", 0)) if self.debug is None else self.debug
        cfg = "Debug" if debug else "Release"
        
        print(f"Building libadic in {cfg} mode...")
        print(f"Extension directory: {extdir}")
        
        # CMake lets you override the generator - we need to check this.
        # Can be set with Conda-Build, for example.
        cmake_generator = os.environ.get("CMAKE_GENERATOR", "")
        
        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
            f"-DCMAKE_BUILD_TYPE={cfg}",
            "-DBUILD_PYTHON_BINDINGS=ON",
            "-DBUILD_SHARED_LIBS=OFF",  # Static link the main library
        ]
        
        build_args = []
        
        if self.compiler.compiler_type != "msvc":
            # Using Ninja-build since it a) is available as a wheel and b)
            # multithreads automatically. MSVC would require all variables be
            # exported for Ninja to pick it up, which is a little tricky to do.
            # Users can override the generator with CMAKE_GENERATOR in
            # the environment.
            if not cmake_generator or cmake_generator == "Ninja":
                try:
                    import ninja
                    
                    ninja_executable_path = Path(ninja.BIN_DIR) / "ninja"
                    cmake_args += [
                        "-GNinja",
                        f"-DCMAKE_MAKE_PROGRAM:FILEPATH={ninja_executable_path}",
                    ]
                except ImportError:
                    pass
        else:
            # Single config generators are handled "normally"
            single_config = any(x in cmake_generator for x in {"NMake", "Ninja"})
            
            # CMake allows an arch-in-generator style for backward compatibility
            contains_arch = any(x in cmake_generator for x in {"ARM", "Win64"})
            
            # Specify the arch if using MSVC generator, but only if it doesn't
            # contain a backward-compatibility arch spec already in the
            # generator name.
            if not single_config and not contains_arch:
                cmake_args += ["-A", "x64" if sys.maxsize > 2**32 else "Win32"]
            
            # Multi-config generators have a different way to specify configs
            if not single_config:
                cmake_args += [
                    f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{cfg.upper()}={extdir}"
                ]
                build_args += ["--config", cfg]
        
        if sys.platform.startswith("darwin"):
            # Cross-compile support for macOS - respect ARCHFLAGS if set
            archs = re.findall(r"-arch (\S+)", os.environ.get("ARCHFLAGS", ""))
            if archs:
                cmake_args += ["-DCMAKE_OSX_ARCHITECTURES={}".format(";".join(archs))]
        
        # Set CMAKE_BUILD_PARALLEL_LEVEL to control the parallel build level
        # across all generators.
        if "CMAKE_BUILD_PARALLEL_LEVEL" not in os.environ:
            # self.parallel is a Python 3 only way to set parallel jobs by hand
            # using -j in the build_ext call, not supported by pip or PyPA-build.
            if hasattr(self, "parallel") and self.parallel:
                # CMake 3.12+ only.
                build_args += [f"-j{self.parallel}"]
        
        build_temp = Path(self.build_temp) / ext.name
        if not build_temp.exists():
            build_temp.mkdir(parents=True)
        
        print(f"Running CMake configure in: {build_temp}")
        print(f"CMake arguments: {cmake_args}")
        
        try:
            subprocess.check_call(["cmake", ext.sourcedir] + cmake_args, cwd=build_temp)
        except subprocess.CalledProcessError as e:
            print(f"\n❌ CMake configuration failed!")
            print("This might be due to missing dependencies (GMP, MPFR) or CMake version.")
            print("Please check the following:")
            print("1. CMake >= 3.14 is installed")
            print("2. GMP and MPFR development libraries are installed:")
            print("   - Ubuntu/Debian: sudo apt-get install libgmp-dev libmpfr-dev")
            print("   - macOS: brew install gmp mpfr") 
            print("   - Windows: Use vcpkg install gmp mpfr")
            print(f"3. Python development headers are available")
            raise RuntimeError(f"CMake configuration failed with exit code {e.returncode}")
        
        print(f"Running CMake build with arguments: {build_args}")
        try:
            subprocess.check_call(["cmake", "--build", "."] + build_args, cwd=build_temp)
        except subprocess.CalledProcessError as e:
            print(f"\n❌ CMake build failed!")
            print("This might be due to compilation errors or missing dependencies.")
            print("Check the build output above for specific error messages.")
            raise RuntimeError(f"CMake build failed with exit code {e.returncode}")
        
        print("✅ libadic build completed successfully!")


# Read the README for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

# Get version from _version.py
def get_version():
    version_file = Path("python/libadic/_version.py")
    if version_file.exists():
        with open(version_file) as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split('"')[1]
    return "1.0.0-dev"


setup(
    name="libadic",
    version=get_version(),
    author="libadic Contributors",
    author_email="info@iguan.ai",
    description="High-performance p-adic arithmetic library for cryptography and the Reid-Li criterion",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/IguanAI/libadic",
    ext_modules=[CMakeExtension("libadic")],
    cmdclass={"build_ext": CMakeBuild},
    packages=["libadic"],
    package_dir={"libadic": "python/libadic"},
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "isort",
            "mypy",
        ],
        "notebooks": [
            "jupyter",
            "matplotlib",
            "scipy",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Mathematics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: C++",
    ],
    keywords="p-adic, number theory, mathematics, riemann hypothesis, reid-li",
    project_urls={
        "Bug Reports": "https://github.com/IguanAI/libadic/issues",
        "Source": "https://github.com/IguanAI/libadic",
        "Documentation": "https://github.com/IguanAI/libadic/blob/main/README.md",
        "API Reference": "https://github.com/IguanAI/libadic/blob/main/docs/API_REFERENCE.md",
        "Crypto API": "https://github.com/IguanAI/libadic/blob/main/PYTHON_CRYPTO_API.md",
    },
    zip_safe=False,
)