from setuptools import setup, find_packages

setup(
    name="tnbs_stim_clean",  # Name of your package
    version="0.1.5",  # Version of your package
    packages=find_packages(),  # Automatically find packages
    install_requires=[  # External dependencies
        "numpy",       
        "matplotlib",  
        "mne",         # Required for EEG/MEG data import
    ],
    long_description=open("README.md").read(),  # Long description for PyPI
    long_description_content_type='text/markdown',  # Optional, set to markdown
    classifiers=[  # Help users find your package
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.1',  # Minimum Python version
)
