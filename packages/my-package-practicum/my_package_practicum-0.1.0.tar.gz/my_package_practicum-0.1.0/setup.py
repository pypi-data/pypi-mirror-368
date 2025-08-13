from setuptools import setup, find_packages

# If you created README.md, we’ll use it for long_description:
with open("README.md", "r", encoding="utf-8") as f:
    long_desc = f.read()

setup(
    name="my_package_practicum",                 # <<< change if you use a different name
    version="0.1.0",
    description="Small NLP helpers (TF-IDF utilities)",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    author="Atharva Chavan",
    author_email="atharva.chavan9898@gmail.com",
    url="https://github.com/yourname/nlpmini",  # optional
    packages=find_packages(exclude=("tests",)),
    python_requires=">=3.8",
    install_requires=[
        "scikit-learn>=1.1.0",
        "scipy>=1.8.0",
    ],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
)