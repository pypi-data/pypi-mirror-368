from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="timezones-lib",
    version="1.0.0",
    author="TimezoneLib",
    author_email="info@timezonelib.com",
    description="Get current time in different timezones (PST, BST, WAT, CET, EST)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/timezones-lib",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=["pytz>=2023.3"],
    entry_points={
        "console_scripts": [
            "tzlib=timezones_lib.cli:main",
        ],
    },
)