from setuptools import setup, find_packages
install_requires=["numpy", "pandas", "seaborn", "matplotlib", "plotly", "scipy", "statsmodels", "scikit-posthocs", "scikit-learn"]


setup(
    name="omicspreprocessing",
    version="0.1.2",
    packages=find_packages(),
    install_requires=install_requires,
    author="Amirhossein Sakhteman",
    author_email="amirhossein.sakhteman@tume.de",
    description="Tools for imputation, statistical analysis and preprocessing of omics data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>=3.7',
)
