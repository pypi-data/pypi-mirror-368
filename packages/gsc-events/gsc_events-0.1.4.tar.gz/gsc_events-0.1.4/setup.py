from setuptools import setup, find_packages

setup(
    name="gsc_events",
    version="0.1.4",
    author="budiworld",
    author_email="budi.world@yahoo.com",
    description="Python library for capturing and handling game events in Plutonium T6",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/Yallamaztar/gsc-events", 
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.13',
)
