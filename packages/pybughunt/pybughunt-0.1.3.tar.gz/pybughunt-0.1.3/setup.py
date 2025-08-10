from setuptools import setup, find_packages

setup(
    name="pybughunt",
    version="0.1.3",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "numpy>=1.20.0",
        "scikit-learn>=1.0.0",
        "torch>=1.9.0",
        "transformers>=4.12.0",
        "astroid>=2.8.0",
        "pylint>=2.11.0",
    ],
    python_requires=">=3.8",
    description="A Python library for detecting logical and syntactical errors in Python code",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Preksha Upadhyay",
    author_email="prekshaupadhyay03@gmail.com",
    url="https://github.com/Preksha-7/pybughunt",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
