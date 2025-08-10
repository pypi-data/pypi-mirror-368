from setuptools import setup, find_packages

setup(
    name="refpy",
    version="0.1.18",
    description="Package for subsea pipelines and risers design in Python",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/refpy/refpy",
    author="ismael-ripoll",
    license="GNU General Public License v3.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires='>=3.11',
    install_requires=[],
    project_urls={
        "Documentation": "https://refpy.github.io/refpy",
        "Source": "https://github.com/refpy/refpy",
        "Tracker": "https://github.com/refpy/refpy/issues",
    }
)