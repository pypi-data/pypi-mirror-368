from setuptools import setup, Extension, find_packages
import platform
import os
import sys

# Configurações específicas por plataforma
if platform.system() == "Windows":
    # Windows
    extra_compile_args = ["/std:c++17", "/O2"]
    define_macros = [("NDEBUG", None)]
    libraries = []
    include_dirs = ["./mapper/inlcudes/win"]
elif platform.system() == "Linux":
    # Linux/Unix
    extra_compile_args = ["-std=c++17", "-fPIC", "-O3", "-march=native", "-ffast-math"]
    define_macros = [("NDEBUG", None)]
    libraries = []
    include_dirs = ["./mapper/inlcudes/linux"]

# Configuração da extensão C++
mapper_extension = Extension(
    "mapper.map_module",
    sources=[
        "mapper/main.cpp",
        "mapper/mapping_fields.cpp", 
        "mapper/flattener.cpp"
    ],
    include_dirs=include_dirs,
    extra_compile_args=extra_compile_args,
    define_macros=define_macros,
    libraries=libraries,
    language="c++"
)

# Configuração do setup
setup(
    name="mapper-lib",
    version="1.0.1",  # Increment version to avoid conflicts
    description="Uma biblioteca C++ para mapeamento e transformação de dados",
    author="Seu Nome",
    author_email="seu.email@exemplo.com",
    url="https://github.com/compre-sua-peca/csp_mapper",
    packages=find_packages(),
    py_modules=["main"],
    ext_modules=[mapper_extension],
    install_requires=[
        "pybind11>=2.0.0",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: C++",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="mapping, data transformation, c++, performance",
    long_description=open("README.md").read() if os.path.exists("README.md") else "Uma biblioteca C++ para mapeamento e transformação de dados",
    long_description_content_type="text/markdown",
    include_package_data=True,
    zip_safe=False,
)
