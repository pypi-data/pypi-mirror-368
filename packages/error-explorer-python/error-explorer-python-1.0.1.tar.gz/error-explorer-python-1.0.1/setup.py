from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="error-explorer-python",
    version="1.0.1",
    author="Manguet",
    author_email="benjamin.manguet@gmail.com",
    description="Python SDK for Error Explorer - Capture and report errors automatically",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Manguet/ErrorReportPythonSDK",
    project_urls={
        "Bug Tracker": "https://github.com/Manguet/ErrorReportPythonSDK/issues",
        "Source": "https://github.com/Manguet/ErrorReportPythonSDK",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: System :: Logging",
        "Topic :: System :: Monitoring",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "django": ["Django>=3.0"],
        "flask": ["Flask>=1.0"],
        "fastapi": ["FastAPI>=0.65.0"],
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.10",
            "black>=21.0",
            "isort>=5.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "error-explorer=error_explorer.cli:main",
        ],
    },
    keywords="error monitoring debugging logging django flask fastapi python",
)
