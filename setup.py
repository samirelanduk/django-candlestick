from setuptools import setup

with open("README.md") as f:
    long_description = f.read()

setup(
    name="django_candlestick",
    version="0.1.0",
    description="A django library for tracking and storing the prices of assets over time.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/samirelanduk/django-candlestick",
    author="Sam Ireland",
    author_email="mail@samireland.com",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Office/Business :: Financial :: Investment",
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="django stocks",
    py_modules=["django_candlestick"],
    python_requires="!=2.*, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*",
)
