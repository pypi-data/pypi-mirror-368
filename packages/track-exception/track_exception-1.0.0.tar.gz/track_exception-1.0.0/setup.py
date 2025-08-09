from setuptools import setup, find_packages

setup(
    name="track_exception",
    version="1.0.0",
    description="A utility to track and log website scraping exceptions in SQLite",
    author="Vishvesh Jasani",
    packages=find_packages(),
    install_requires=[],
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
