from setuptools import setup, Extension
import pybind11

ext_modules = [
    Extension(
        "dynamic_segment_tree._dseg",
        ["dynamic_segment_tree/_dseg.cpp"],
        include_dirs=[pybind11.get_include()],
        language="c++",
        extra_compile_args=["-O3", "-std=c++17"]
    )
]

setup(
    name="dynamic-segment-tree",
    version="0.1.0",
    author="Abdullah Enes Oncu",
    author_email="abdullahenesoncu@gmail.com",
    description="Dynamic segment tree with Python bindings",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    ext_modules=ext_modules,
    packages=["dynamic_segment_tree"],
    install_requires=["pybind11>=2.6.0"],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: C++",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    zip_safe=False,
)
