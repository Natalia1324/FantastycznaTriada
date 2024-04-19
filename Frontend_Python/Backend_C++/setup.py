from setuptools import setup, Extension
import pybind11

cpp_args = ['-std=c++20', '-stdlib=libc++', '-mmacosx-version-min=10.7']

sfc_module = Extension(
    'backend',
    sources=['backend.cpp'],
    include_dirs=[pybind11.get_include()],
    language='c++',
    extra_compile_args=cpp_args,
    )

setup(
    name='backend',
    version='1.0',
    description='Backend written in C++ for "Fantastyczna Triada"',
    ext_modules=[sfc_module],
)