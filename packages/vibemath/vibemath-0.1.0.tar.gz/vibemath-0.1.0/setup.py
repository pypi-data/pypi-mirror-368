from setuptools import setup, find_packages

with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vibemath",
    version="0.1.0",
    author="yemeen",
    author_email="yemeen.ayub@gmail.com",
    description="Python package that uses GPT to evaluate mathematical expressions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yemeen/vibemath",
    project_urls={
        "Bug Tracker": "https://github.com/yemeen/vibemath/issues",
        "Documentation": "https://github.com/yemeen/vibemath#readme",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
        "numpy>=1.20.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "mypy>=1.0.0",
            "twine>=4.0.0",
            "build>=0.10.0",
        ],
    },
    keywords="math gpt ai mathematics evaluation openai",
    license="MIT",
    include_package_data=True,
)
