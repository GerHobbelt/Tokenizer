import os
import shutil
import sys

import pybind11

from setuptools import Extension, find_packages, setup

include_dirs = [pybind11.get_include()]
library_dirs = []
package_data = {}


def _get_long_description():
    readme_path = "README.md"
    with open(readme_path, encoding="utf-8") as readme_file:
        return readme_file.read()


def _get_project_version():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    version_path = os.path.join(base_dir, "pyonmttok", "version.py")
    version = {}
    with open(version_path, encoding="utf-8") as fp:
        exec(fp.read(), version)
    return version["__version__"]


def _maybe_add_library_root(lib_name, header_only=False):
    root = os.environ.get("%s_ROOT" % lib_name)
    if root is None:
        return
    include_dirs.append(os.path.join(root, "include"))
    if not header_only:
        for lib_subdir in ("lib64", "lib"):
            lib_dir = os.path.join(root, lib_subdir)
            if os.path.isdir(lib_dir):
                library_dirs.append(lib_dir)
                break
    print("include_dirs: " + str(include_dirs))


def _maybe_add_dic_resources(lib_name):
    root = os.environ.get("%s_ROOT" % lib_name)

    jiebadic_src = os.path.join(root, os.sep.join(["share", "cppjieba", "dict"]))
    for lib_subdir in ("lib64", "lib"):
        mecabdic_src = os.path.join(
            root, os.sep.join([lib_subdir, "mecab", "dic", "unidic_lite"])
        )
        if os.path.isdir(mecabdic_src):
            break
    for lib_subdir in ("lib64", "lib"):
        mecabkodic_src = os.path.join(
            root, os.sep.join([lib_subdir, "mecab-ko", "dic", "mecab-ko-dic"])
        )
        if os.path.isdir(mecabkodic_src):
            break

    print("CPPJIEBA_DIC: " + str(jiebadic_src))
    print("MECAB_DIC: " + str(mecabdic_src))
    print("MECABKO_DIC: " + str(mecabkodic_src))

    base_dir = os.path.dirname(os.path.abspath(__file__))
    jiebadic_tgt = os.path.join(base_dir, "pyonmttok", "cppjieba_dic")
    mecabdic_tgt = os.path.join(base_dir, "pyonmttok", "mecab_dic")
    mecabkodic_tgt = os.path.join(base_dir, "pyonmttok", "mecabko_dic")

    if jiebadic_src is not None:
        shutil.copytree(jiebadic_src, jiebadic_tgt, dirs_exist_ok=True)
        with open(os.path.join(jiebadic_tgt, "__init__.py"), "w") as _:
            pass
        with open(os.path.join(jiebadic_tgt, "pos_dict", "__init__.py"), "w") as _:
            pass
        package_data["pyonmttok.cppjieba_dic"] = ["*.utf8"]
        package_data["pyonmttok.cppjieba_dic.pos_dict"] = ["*.utf8"]

    if mecabdic_src is not None:
        shutil.copytree(mecabdic_src, mecabdic_tgt, dirs_exist_ok=True)
        with open(os.path.join(mecabdic_tgt, "__init__.py"), "w") as _:
            pass
        package_data["pyonmttok.mecab_dic"] = ["*.bin", "*.def", "*.dic", "dicrc"]
    if mecabkodic_src is not None:
        shutil.copytree(mecabkodic_src, mecabkodic_tgt, dirs_exist_ok=True)
        with open(os.path.join(mecabkodic_tgt, "__init__.py"), "w") as _:
            pass
        package_data["pyonmttok.mecabko_dic"] = ["*.bin", "*.def", "*.dic", "dicrc"]

    print("package_data: " + str(package_data))


_maybe_add_library_root("TOKENIZER")
_maybe_add_dic_resources("TOKENIZER")

cflags = ["-std=c++17", "-fvisibility=hidden"]
ldflags = []
if sys.platform == "darwin":
    cflags.append("-mmacosx-version-min=10.14")
    ldflags.append("-Wl,-rpath,/usr/local/lib")
elif sys.platform == "win32":
    cflags = ["/std:c++17", "/d2FH4-"]
    package_data["pyonmttok"] = ["*.dll"]

tokenizer_module = Extension(
    "pyonmttok._ext",
    sources=["pyonmttok/Python.cc"],
    extra_compile_args=cflags,
    extra_link_args=ldflags,
    include_dirs=include_dirs,
    library_dirs=library_dirs,
    libraries=["OpenNMTTokenizer"],
)

setup(
    name="pyonmttok",
    version=_get_project_version(),
    license="MIT",
    description=(
        "Fast and customizable text tokenization library with "
        "BPE and SentencePiece support"
    ),
    long_description=_get_long_description(),
    long_description_content_type="text/markdown",
    author="OpenNMT",
    url="https://opennmt.net",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    project_urls={
        "Forum": "https://forum.opennmt.net/",
        "Source": "https://github.com/OpenNMT/Tokenizer/",
    },
    keywords="tokenization opennmt unicode bpe sentencepiece subword",
    packages=find_packages(),
    package_data=package_data,
    python_requires=">=3.6",
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    ext_modules=[tokenizer_module],
)
