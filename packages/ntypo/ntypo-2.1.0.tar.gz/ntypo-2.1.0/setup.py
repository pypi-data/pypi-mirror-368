from setuptools import setup, find_packages

setup(
    name="ntypo",
    version="2.1.0",
    author="Eren Öğrül",
    author_email="termapp@pm.me",
    description="A terminal typing speed test built with ncurses",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    package_data={"ntypo": ["words.txt"]},
    entry_points={
        "console_scripts": [
            "ntypo=ntypo.cli:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)