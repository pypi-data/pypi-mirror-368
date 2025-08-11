from setuptools import setup, find_packages

with open("requirements.txt", "r") as file:
    common_requirements = file.readlines()

with open("packages/doc-loader.txt", "r") as file:
    doc_loader = file.readlines()

with open("packages/index.txt", "r") as file:
    index = file.readlines()

with open("packages/tools.txt", "r") as file:
    tools = file.readlines()

with open("packages/eval.txt", "r") as file:
    eval = file.readlines()

all = common_requirements + doc_loader + index + tools + eval

setup(
    name="fabriq",
    version="0.1.6",
    description="Fabriq is a Python SDK for developing quick, low code, and enterprise-level Generative AI solutions.",
    author="Aaryan Verma",
    url="https://github.com/Aaryanverma/fabriq",
    packages=find_packages(),
    install_requires=common_requirements,
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
    ],
    extras_require = {
        'doc-loader': doc_loader,
        'index': index,
        'tools': tools,
        'eval': eval,
        'all': all
    }
)