from setuptools import setup, find_packages

setup(
    name="tongban_report",
    version="0.3.1",
    author="roger813",
    author_email="roger813@163.com",
    license = "MIT AND (Apache-2.0 OR BSD-2-Clause)",
    description="A short description of your package",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/your-package",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "python-docx",
        "matplotlib",
        "openpyxl"
    ],
    entry_points={
        "console_scripts": [
            "tongban_report=tongban_report.main:main",
        ],
    },
)