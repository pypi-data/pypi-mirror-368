from setuptools import setup, find_packages

setup(
    name="ilovemadpussy9",          # Your package name on PyPI
    version="0.1.0",                       # Incremented version number
    author="auth",
    author_email="bisects@proton.me",
    description="wrd",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    packages=find_packages(include=["package", "package.*"]),
    package_data={
        "package": ["__init__.py", "module.py"],  # Explicitly include package files
    },
    include_package_data=True,  # Ensure package_data is included
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)