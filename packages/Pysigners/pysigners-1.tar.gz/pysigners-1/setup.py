from setuptools import setup, find_packages
setup(
    name="Pysigners",
    version="1",
    author="Dragon",
    author_email="reco9678785@gmail.com",
    description="null",
    packages=find_packages(),
    install_requires=[
        "user_agent",
        "requests",
        "MedoSigner",
        "pycryptodome"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)