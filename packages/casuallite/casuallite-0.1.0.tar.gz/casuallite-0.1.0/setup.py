from setuptools import setup, find_packages

setup(
    name="casuallite",
    version="0.1.0",
    author="Project Genesis",
    author_email="srinimagi99@gmail.com",
    description="CasualLite: The world's first Hybrid Meta Causal Learning Algorithm",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/theAiAlgoRepository/casuallite",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    license="Apache-2.0",
    python_requires=">=3.8",
    install_requires=[
        "numpy",
        "seaborn",
        "pandas",
        "matplotlib",
        "scikit-learn",
        "scipy",
        "torch",
        "networkx"
    ],
    include_package_data=True,
    zip_safe=False,
)
