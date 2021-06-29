from setuptools import setup
from glob import glob
import os

with open("README.md") as f:
    long_description = f.read()

setup(
    name="django_candlestick",
    version="0.2.0",
    description="A django library for tracking and storing the prices of assets over time.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/samirelanduk/django-candlestick",
    author="Sam Ireland",
    author_email="mail@samireland.com",
    license="GPLv3+",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Topic :: Internet :: WWW/HTTP",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Topic :: Office/Business :: Financial :: Investment",
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="django stocks",
    packages=["candlestick"],
    include_package_data=True,
    python_requires="!=2.*, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*",
    install_requires=["django_timezone_field", "yfinance"]
)
