from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

base_url = "https://github.com/SimLej18/manim-presentations"

setup(
    name="manim-presentations",
    version="0.1.0",
    author="S Lejoly",
    author_email="simon.lejoly@unamur.be",
    description="A Python framework for creating composable manim-slides presentations.",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=base_url,
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Multimedia :: Graphics",
    ],
    python_requires=">=3.8",
    install_requires=[
        "manim",
        "manim-slides",
    ],
    extras_require={
        "dev": [
            "pytest",
            "black",
            "flake8",
        ],
    },
    entry_points={
        "console_scripts": [
            "manim-presentations=manim_presentations.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "manim_presentations": ["templates/*", "assets/*"],
    },
    keywords="manim, animations, mathematics, presentations, education, visualization",
    project_urls={
        "Bug Reports": base_url+"/issues",
        "Source": base_url,
        "Documentation": base_url+"/README.md",
    },
)